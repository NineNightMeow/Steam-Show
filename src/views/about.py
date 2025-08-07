from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import (
    SimpleCardWidget,
    IconWidget,
    BodyLabel,
    CaptionLabel,
    PrimaryPushButton,
    TransparentToolButton,
    FluentIcon,
)

from src.views.interface import Interface
from src.utils.translator import Translator
from src.version import __version__


class card(SimpleCardWidget):
    def __init__(self, icon, title, content, action, event, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(73)
        self.iconWidget.setFixedSize(24, 24)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")

        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        if action:
            self.hBoxLayout.addStretch(1)
            self.hBoxLayout.addWidget(action, 0, Qt.AlignRight)

            if event:
                action.clicked.connect(event)


class About(Interface):
    def __init__(self):
        super().__init__(title=Translator().about_title)
        self.setObjectName("about")

        self.layout = QVBoxLayout(self)

        self.developer_card = card(
            icon=FluentIcon.PEOPLE,
            title=self.tr("Developers"),
            content="Kuri Nayuki & Hapy & Zhen",
            action=TransparentToolButton(FluentIcon.HEART.icon(color="#bf3989")),
            event=self.openGitHub,
            parent=self,
        )
        self.gihub_card = card(
            icon=FluentIcon.GITHUB,
            title="GitHub",
            content="NineNightMeow/Steam-Show",
            action=TransparentToolButton(FluentIcon.LINK),
            event=self.openGitHub,
            parent=self,
        )
        self.version_card = card(
            icon=FluentIcon.APPLICATION,
            title=self.tr("App Version"),
            content=__version__,
            action=PrimaryPushButton(self.tr("Check Update")),
            event=self.checkUpdate,
            parent=self,
        )

        self.layout.addWidget(self.developer_card)
        self.layout.addWidget(self.gihub_card)
        self.layout.addWidget(self.version_card)
        self.layout.addStretch()

        self.view.setLayout(self.layout)

    def openGitHub(self):
        QDesktopServices.openUrl(QUrl("https://github.com/NineNightMeow/Steam-Show"))

    def checkUpdate(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/NineNightMeow/Steam-Show/releases")
        )
