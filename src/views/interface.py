from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import TitleLabel, CaptionLabel, isDarkTheme


class Interface(QWidget):
    def __init__(self, title: str = "", subtitle: str = "", parent=None):
        super().__init__(parent=parent)
        self.setObjectName("view")

        self.interfaceLayout = QVBoxLayout(self)

        self.header = QWidget(self)
        self.headerLayout = QVBoxLayout(self.header)

        if title:
            self.titleLabel = TitleLabel(title, self)
            self.headerLayout.addWidget(self.titleLabel)
        if subtitle:
            self.subtitleLabel = CaptionLabel(subtitle, self)
            self.headerLayout.addWidget(self.subtitleLabel)

        self.view = QWidget(self)

        self.interfaceLayout.addWidget(self.header)
        self.interfaceLayout.addWidget(self.view)

        self.setLayout(self.interfaceLayout)


class Separator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(6, 16)

    def paintEvent(self, e):
        painter = QPainter(self)
        pen = QPen(1)
        pen.setCosmetic(True)
        c = QColor(255, 255, 255, 21) if isDarkTheme() else QColor(0, 0, 0, 15)
        pen.setColor(c)
        painter.setPen(pen)

        x = self.width() // 2
        painter.drawLine(x, 0, x, self.height())
