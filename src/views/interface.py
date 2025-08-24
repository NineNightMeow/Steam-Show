from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    TitleLabel,
    CaptionLabel,
    InfoBar,
    InfoBarPosition,
    StateToolTip,
    isDarkTheme,
)


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


class InfoTip:
    def __init__(
        self,
        type="info",
        title="",
        message="",
        isClosable=True,
        parent=None,
    ):
        type_map = {
            "info": InfoBar.info,
            "success": InfoBar.success,
            "warning": InfoBar.warning,
            "error": InfoBar.error,
        }

        if type not in type_map:
            type = "info"

        content_len = len(title) + len(message)
        if content_len > 20:
            orientation = Qt.Vertical
        else:
            orientation = Qt.Horizontal

        type_map[type](
            title=title,
            content=message,
            orient=orientation,
            isClosable=isClosable,
            position=InfoBarPosition.TOP,
            duration=content_len * 500,
            parent=parent,
        )


class StateTip:
    def __init__(self, title="", message="", parent=None):
        self.stateTooltip = StateToolTip(title, message, parent)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.closeButton.hide()
        self.stateTooltip.show()

    def update(self, title=None, message=None):
        if title is not None:
            self.stateTooltip.setTitle(title)
        if message is not None:
            self.stateTooltip.setContent(message)

    def close(self):
        self.stateTooltip.setState(True)


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
