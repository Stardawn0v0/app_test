# 没空做了 放弃GUI
import os
import subprocess
import traceback

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from qfluentwidgets import FlowLayout, Dialog, ToggleButton, TeachingTip, InfoBarIcon, TeachingTipTailPosition

from typing import Dict, Tuple
from qtui import Ui_Form
from PyQt5.QtWidgets import QApplication
from qframelesswindow import AcrylicWindow
import sys

from time_test import push_aapt, test_launch_time, is_device_connected, get_apk_path


GET_APP_LIST_SH = os.path.join(os.path.dirname(__file__), 'get_app_list.sh')

class MainWindow(AcrylicWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.windowEffect.setMicaEffect(self.winId())
        self.userApps_layout = FlowLayout()
        self.userApps_widget.setLayout(self.userApps_layout)
        self.systemApps_layout = FlowLayout()
        self.systemApps_widget.setLayout(self.systemApps_layout)
        self.apps = {}
        self.selectedApps = []

        sys.excepthook = lambda type, value, tb: self.on_error("".join(traceback.format_exception(type, value, tb)))

        self.tabChanger.addItem(
            routeKey='userApps',
            text='用户应用',
            onClick=lambda: self.tabs.setCurrentIndex(0),
        )
        self.tabChanger.addItem(
            routeKey='systemApps',
            text='系统应用',
            onClick=lambda: self.tabs.setCurrentIndex(1),
        )
        self.tabChanger.setCurrentItem('userApps')
        self.tabs.setCurrentIndex(0)

        self.scan_apps.clicked.connect(self.scan_apps_clicked)



    def tip(self, target, title: str, content: str, icon='Info', closable=True, duration=5000):
        """
        :param target: Tip指向的控件
        :param title: 标题
        :param content: 正文
        :param icon: 图标，可选值：Info, Warning, Error, Success
        :param closable: 是否可手动关闭
        :param duration: 时长
        :return:
        """
        if icon == 'Info':
            icon = InfoBarIcon.INFORMATION
        elif icon == 'Warning':
            icon = InfoBarIcon.WARNING
        elif icon == 'Error':
            icon = InfoBarIcon.ERROR
        elif icon == 'Success':
            icon = InfoBarIcon.SUCCESS
        TeachingTip.create(
            target=target,
            icon=icon,
            title=title,
            content=content,
            isClosable=closable,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=duration,
            parent=self
        )

    def on_error(self, output):
        w = Dialog('程序发生错误', output, self)
        w.cancelButton.setText('忽略')
        w.yesButton.setText('确认并复制错误信息到剪切板')
        w.yesButton.clicked.connect(lambda: QApplication.clipboard().setText(output))
        w.exec()

    def scan_apps_clicked(self):
        if not is_device_connected():
            self.tip(self.scan_apps, '设备未连接', '未找到已正确连接的ADB设备或已连接多个ADB设备', 'Error')
        try:
            push_aapt()  # 确保aapt工具已被推送至设备
            user_apps, system_apps = self.get_apps()
            self.add_user_apps(user_apps)
            self.add_system_apps(system_apps)
            self.apps = {**user_apps, **system_apps}
        except Exception as e:
            self.on_error(str(e))

    def get_apps(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """获取设备上的用户应用和系统应用，并返回两个字典：用户应用和系统应用。"""
        user_apps: Dict[str, str] = {}
        system_apps: Dict[str, str] = {}
        subprocess.run(['adb', 'push', GET_APP_LIST_SH, '/data/local/tmp/get_app_list.sh'], creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['adb', 'shell', 'chmod', '+x', '/data/local/tmp/get_app_list.sh'], creationflags=subprocess.CREATE_NO_WINDOW)
        output = subprocess.check_output(['adb', 'shell', '/data/local/tmp/get_app_list.sh']).decode('utf-8')
        for line in output.splitlines():
            # line: user/system<trim>app_name<trim>package_name
            parts = line.split('<trim>')
            if len(parts) == 3:
                if parts[0] == 'user':
                    user_apps[parts[2]] = parts[1]
                elif parts[0] == 'system':
                    system_apps[parts[2]] = parts[1]

        self.apps = {**user_apps, **system_apps}
        return user_apps, system_apps

    def add_user_apps(self, user_apps: Dict[str, str]):
        for app_name in user_apps.values():
            btn = ToggleButton(app_name)
            print(btn.text())
            btn.clicked.connect(self.onAppToggled)
            self.userApps_layout.addWidget(btn)

    def add_system_apps(self, system_apps: Dict[str, str]):
        for app_name in system_apps.values():
            btn = ToggleButton(app_name)
            btn.clicked.connect(self.onAppToggled)
            self.systemApps_layout.addWidget(btn)


    def onAppToggled(self):
        btn = self.sender()
        appName = btn.text()
        pkgName = [pkg for pkg, name in self.apps.items() if name == appName][0]

        if btn.isChecked():
            self.selectedApps.append(pkgName)
        else:
            self.selectedApps.remove(pkgName)



class ADB(QThread):
    finished = pyqtSignal(str)

    def __init__(self, cmd: str):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            output, error = process.communicate()
            if process.returncode == 0:
                self.finished.emit(output.decode('utf-8'))
            else:
                self.finished.emit(error.decode('utf-8'))
        except Exception as e:
            self.finished.emit(str(e))


def adb_run(cmd: str, on_adb_finished: callable):
    adb_thread = ADB(cmd)
    adb_thread.finished.connect(lambda output: on_adb_finished(output))
    adb_thread.start()
    return adb_thread






if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
