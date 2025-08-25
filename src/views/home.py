import os

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    SubtitleLabel,
    IconWidget,
    CaptionLabel,
    ElevatedCardWidget,
    FlowLayout,
    isDarkTheme,
)

from src.views.interface import Interface
from src.utils.translator import Translator
from src.icons.icons import Icon


class Card(ElevatedCardWidget):
    def __init__(
        self,
        icon=None,
        name: str = "",
        target: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.icon = IconWidget(icon, self)
        self.label = CaptionLabel(name, self)

        self.icon.setFixedSize(50, 50)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.icon, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)

        self.clicked.connect(lambda: parent.switchInterface(target))

        self.setFixedSize(150, 150)


class Home(Interface):
    def __init__(self, window):
        t = Translator()

        super().__init__(
            title=t.home_title,
            subtitle=t.home_subtitle,
        )
        self.setObjectName("home")

        layout = QVBoxLayout()

        banner_path = os.path.join(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "images", "banner.png"
            )
        )
        self.banner = QPixmap(banner_path)

        self.functions = QWidget()
        self.tools = QWidget()
        self.functions_layout = QVBoxLayout()
        self.tools_layout = QVBoxLayout()
        self.functions_flow = FlowLayout()
        self.tools_flow = FlowLayout()

        self.functions_flow.addWidget(
            Card(
                Icon.fromName("ArrowSyncCircle20Regular"),
                t.convert_title,
                "convert",
                window,
            )
        )
        self.functions_flow.addWidget(
            Card(
                Icon.fromName("CloudArrowUp20Regular"),
                t.deployment_title,
                "deployment",
                window,
            )
        )
        self.tools_flow.addWidget(
            Card(
                Icon.fromName("EditLineHorizontal320Regular"),
                t.editor_title,
                "editor",
                window,
            )
        )
        self.tools_flow.addWidget(
            Card(
                Icon.fromName("ChatArrowBackDown20Regular"),
                t.message_title,
                "message",
                window,
            )
        )
        self.tools_flow.addWidget(
            Card(
                Icon.fromName("GridDots20Regular"),
                t.char_title,
                "char",
                window,
            )
        )
        self.tools_flow.addWidget(
            Card(
                Icon.fromName("Calculator20Regular"),
                t.level_title,
                "level",
                window,
            )
        )

        self.functions_layout.addWidget(SubtitleLabel(t.functions, self))
        self.functions_layout.addLayout(self.functions_flow)
        self.tools_layout.addWidget(SubtitleLabel(t.tools, self))
        self.tools_layout.addLayout(self.tools_flow)

        self.functions.setLayout(self.functions_layout)
        self.tools.setLayout(self.tools_layout)

        layout.addWidget(self.functions)
        layout.addWidget(self.tools)
        layout.addStretch()

        self.view.setContentsMargins(0, 100, 0, 0)
        self.view.setLayout(layout)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), 250
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        gradient = QLinearGradient(0, 0, 0, h)

        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        pixmap = self.banner.scaled(w, h, transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))
