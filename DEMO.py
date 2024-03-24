from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from qfluentwidgets import FlowLayout, SmoothScrollArea, ToggleButton


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowLayout with ScrollArea Example")
        self.resize(400, 300)

        # 创建 ScrollArea 和 FlowLayout 容器
        self.scrollArea = SmoothScrollArea(self)  # 创建一个滚动区域
        self.scrollArea.setWidgetResizable(True)  # 允许滚动区域自动调整大小

        self.containerWidget = QWidget()  # 创建一个容器 QWidget
        self.flowLayout = FlowLayout(self.containerWidget)  # 将 FlowLayout 应用于容器

        # 向流体布局中添加多个按钮
        for i in range(50):  # 创建50个按钮作为示例
            button = ToggleButton(f"Button {i + 1}")
            self.flowLayout.addWidget(button)

        # 将包含FlowLayout的QWidget设置为ScrollArea的中心组件
        self.scrollArea.setWidget(self.containerWidget)

        # 主窗口布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.scrollArea)  # 将 ScrollArea 添加到窗口的布局中


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec_()