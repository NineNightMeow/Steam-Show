from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QTableWidgetItem
from qfluentwidgets import (
    IconWidget,
    BodyLabel,
    CaptionLabel,
    PrimaryPushButton,
    TransparentToolButton,
    HyperlinkLabel,
    SimpleCardWidget,
    ExpandGroupSettingCard,
    FluentIcon,
)

from src.views.interface import Interface, Separator
from src.utils.translator import Translator
from src.app import App


class CreditsCard(ExpandGroupSettingCard):
    def __init__(self, icon, title, subtitle, parent=None):
        super().__init__(
            icon,
            title,
            subtitle,
            parent,
        )

        projects = [
            ["FFmpeg", "https://github.com/FFmpeg/FFmpeg"],
            ["PyQt-Fluent-Widgets", "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"],
            ["Braille-ASCII-Art", "https://github.com/LachlanArthur/Braille-ASCII-Art"],
            [
                "fluentui-system-icons",
                "https://github.com/microsoft/fluentui-system-icons",
            ],
        ]

        for project in projects:
            w = QWidget()
            w.setFixedHeight(60)
            layout = QHBoxLayout(w)
            layout.setContentsMargins(20, 5, 8, 5)

            link = TransparentToolButton(FluentIcon.LINK)
            url = project[1]
            link.clicked.connect(
                lambda checked, url=url: QDesktopServices.openUrl(QUrl(url))
            )

            layout.addWidget(BodyLabel(project[0], self))
            layout.addStretch(1)
            layout.addWidget(link)

            self.addGroupWidget(w)


class Card(SimpleCardWidget):
    def __init__(
        self,
        icon=None,
        title: str = "",
        content=None,
        action=None,
        event=None,
        parent=None,
    ):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(70)
        self.iconWidget.setFixedSize(16, 16)

        self.hBoxLayout.setContentsMargins(15, 5, 8, 5)
        self.hBoxLayout.setSpacing(16)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        if isinstance(content, str):
            self.contentLabel = CaptionLabel(content, self)
            self.contentLabel.setTextColor("#606060", "#d2d2d2")
            self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        else:
            self.vBoxLayout.addWidget(content, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addStretch(1)

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

        self.author_links = QWidget()
        self.author_links_layout = QHBoxLayout()
        self.author_links_layout.setContentsMargins(0, 0, 0, 0)
        self.author_links.setStyleSheet("font-size: 12px;")
        self.author_links.setLayout(self.author_links_layout)
        self.author_links_layout.addWidget(
            HyperlinkLabel(QUrl("https://github.com/NineNightMeow"), "Kuri Nayuki")
        )
        self.author_links_layout.addWidget(Separator())
        self.author_links_layout.addWidget(
            HyperlinkLabel(QUrl("https://github.com/HSP-hapy"), "Hapy")
        )
        self.author_links_layout.addWidget(Separator())
        self.author_links_layout.addWidget(
            HyperlinkLabel(QUrl("https://github.com/GongZhenAB"), "Zhen")
        )

        self.version_card = Card(
            icon=FluentIcon.APPLICATION,
            title=self.tr("App Version"),
            content=App().getVersion(),
            action=PrimaryPushButton(self.tr("Check Update")),
            event=self.checkUpdate,
            parent=self,
        )
        self.developer_card = Card(
            icon=FluentIcon.PEOPLE,
            title=self.tr("Developers"),
            content=self.author_links,
            event=self.openGitHub,
            parent=self,
        )
        self.gihub_card = Card(
            icon=FluentIcon.GITHUB,
            title="GitHub",
            content="NineNightMeow/Steam-Show",
            action=TransparentToolButton(FluentIcon.LINK),
            event=self.openGitHub,
            parent=self,
        )

        self.credits_card = CreditsCard(
            FluentIcon.BOOK_SHELF,
            self.tr("Credits"),
            self.tr("Open source projects used"),
            self,
        )

        self.layout.addWidget(self.version_card)
        self.layout.addWidget(self.developer_card)
        self.layout.addWidget(self.gihub_card)
        self.layout.addWidget(self.credits_card)
        self.layout.addStretch()

        self.view.setLayout(self.layout)

    def openGitHub(self):
        QDesktopServices.openUrl(QUrl("https://github.com/NineNightMeow/Steam-Show"))

    def checkUpdate(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/NineNightMeow/Steam-Show/releases")
        )
