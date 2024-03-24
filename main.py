from PyQt5.QtCore import Qt

from qtui import Ui_Form
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from qframelesswindow import AcrylicWindow
from cmosui import SlidingStackedWidget
import sys


class MainWindow(AcrylicWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.windowEffect.setMicaEffect(self.winId())

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


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
