from PyQt5.QtWidgets import QStackedWidget, QApplication, QVBoxLayout, QLabel, QWidget, QPushButton
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QAbstractAnimation, QParallelAnimationGroup, Qt


class SlidingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_direction = Qt.Horizontal
        self.m_speed = 500
        self.m_animationType = QEasingCurve.OutCubic
        self.m_now = 0
        self.m_next = 0
        self.m_wrap = False
        self.m_pnow = QPoint(0, 0)
        self.m_active = False

    def setDirection(self, direction):
        self.m_direction = direction

    def setSpeed(self, speed):
        self.m_speed = speed

    def setAnimation(self, animationType):
        self.m_animationType = animationType

    def setWrap(self, wrap):
        self.m_wrap = wrap

    def slideInNext(self):
        now = self.currentIndex()
        if self.m_wrap or now < self.count() - 1:
            self.slideInIdx(now + 1)

    def slideInPrev(self):
        now = self.currentIndex()
        if self.m_wrap or now > 0:
            self.slideInIdx(now - 1)

    def slideInIdx(self, idx):
        if idx > self.count() - 1:
            idx %= self.count()
        elif idx < 0:
            idx = (idx + self.count()) % self.count()
        self.slideInWgt(self.widget(idx))

    def slideInWgt(self, newwidget):
        if self.m_active:
            return
        self.m_active = True
        _now = self.currentIndex()
        _next = self.indexOf(newwidget)
        if _now == _next:
            self.m_active = False
            return

        offsetx = self.frameRect().width()
        self.widget(_next).setGeometry(self.frameRect())
        if _now < _next:
            offsetx = -offsetx
        pnext = self.widget(_next).pos()
        pnow = self.widget(_now).pos()
        self.m_pnow = pnow

        offset = QPoint(offsetx, 0)  # 只在水平方向上偏移
        self.widget(_next).move(pnext - offset)
        self.widget(_next).show()
        self.widget(_next).raise_()

        anim_group = QParallelAnimationGroup(self, finished=self.animationDoneSlot)

        for index, start, end in zip((_now, _next), (pnow, pnext - offset), (pnow + offset, pnext)):
            animation = QPropertyAnimation(self.widget(index), b"pos")
            animation.setDuration(self.m_speed)
            animation.setEasingCurve(self.m_animationType)
            animation.setStartValue(start)
            animation.setEndValue(end)
            anim_group.addAnimation(animation)

        self.m_next = _next
        self.m_now = _now
        self.m_active = True
        anim_group.start(QAbstractAnimation.DeleteWhenStopped)

    def animationDoneSlot(self):
        self.setCurrentIndex(self.m_next)
        self.widget(self.m_now).hide()
        self.widget(self.m_now).move(self.m_pnow)
        self.m_active = False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.stackedWidget = SlidingStackedWidget()
        self.stackedWidget.setSpeed(500)  # 设置滑动速度为500毫秒
        self.stackedWidget.setAnimation(QEasingCurve.OutCubic)  # 设置非线性动画

        # 创建三个界面
        page1 = QWidget()
        page1Layout = QVBoxLayout()
        page1Layout.addWidget(QLabel("这是第一个界面"))
        page1.setLayout(page1Layout)

        page2 = QWidget()
        page2Layout = QVBoxLayout()
        page2Layout.addWidget(QLabel("这是第二个界面"))
        page2.setLayout(page2Layout)

        page3 = QWidget()
        page3Layout = QVBoxLayout()
        page3Layout.addWidget(QLabel("这是第三个界面"))
        page3.setLayout(page3Layout)

        # 将三个界面添加到SlidingStackedWidget中
        self.stackedWidget.addWidget(page1)
        self.stackedWidget.addWidget(page2)
        self.stackedWidget.addWidget(page3)

        # 创建三个按钮
        button1 = QPushButton("界面1")
        button1.clicked.connect(lambda: self.stackedWidget.slideInIdx(0))

        button2 = QPushButton("界面2")
        button2.clicked.connect(lambda: self.stackedWidget.slideInIdx(1))

        button3 = QPushButton("界面3")
        button3.clicked.connect(lambda: self.stackedWidget.slideInIdx(2))

        # 将按钮和SlidingStackedWidget添加到主布局中
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)
        layout.addWidget(self.stackedWidget)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
