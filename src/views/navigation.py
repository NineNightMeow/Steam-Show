import os

from PyQt5.QtCore import (
    Qt,
    QUrl,
    QPoint,
    QRect,
)
from PyQt5.QtGui import (
    QFont,
    QImage,
    QPainter,
    QColor,
    QBrush,
    QDesktopServices,
)

from PyQt5.QtWidgets import QWidget
from qfluentwidgets import (
    NavigationInterface,
    NavigationWidget,
    NavigationItemPosition,
    AvatarWidget,
    BodyLabel,
    CaptionLabel,
    IconWidget,
    Action,
    RoundMenu,
    MenuAnimationType,
    FluentIcon,
    isDarkTheme,
)

from src.utils.translator import Translator
from src.icons.icons import Icon

t = Translator()


class NavItem(NavigationWidget):
    def __init__(self, icon, icon_selected, text, selectable=True, parent=None):
        super().__init__(isSelectable=True, parent=parent)
        self.icon = IconWidget(icon, self)
        self.icon.setFixedSize(24, 24)
        self.icon.hide()
        self.icon_selected = IconWidget(icon_selected, self)
        self.icon_selected.setFixedSize(24, 24)
        self.icon_selected.hide()
        self.text = text
        self.selectable = selectable
        self.isSelected = False

    def setSelected(self, isSelected: bool):
        self.isSelected = isSelected
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)

        if self.isEnter or (self.isSelected and self.selectable):
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        if self.isSelected and self.selectable:
            icon_widget = self.icon_selected
        else:
            icon_widget = self.icon

        painter.setBrush(QBrush(icon_widget.icon.pixmap(icon_widget.size())))
        painter.translate(8, 6)
        painter.drawPixmap(0, 0, icon_widget.icon.pixmap(icon_widget.size()))
        painter.translate(-8, -6)

        if not self.isCompacted:
            color = "#ffffff" if isDarkTheme() else "#000000"
            painter.setPen(QColor(color))
            font = QFont("Segoe UI")
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, self.text)


class NavClassTitle(NavigationWidget):
    def __init__(self, text, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.text = text

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        color = "#d2d2d2" if isDarkTheme() else "#606060"
        painter.setPen(QColor(color))
        font = QFont("Segoe UI")
        font.setPixelSize(14)
        painter.setFont(font)
        painter.drawText(QRect(10, 0, 255, 36), Qt.AlignVCenter, self.text)


class NavAvatar(NavigationWidget):
    def __init__(self, url="", alt="", parent=None):
        super().__init__(isSelectable=False, parent=parent)
        avatarUrl = os.path.join("src", "images", "default-avatar.png")
        if url:
            avatarUrl = url
        self.avatar = QImage(avatarUrl).scaled(
            24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.alt = t.not_logged_in
        if alt:
            self.alt = alt

    def updateAvatar(self, url, alt):
        if url:
            self.avatar = QImage(url).scaled(
                24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        self.alt = t.not_logged_in
        if alt:
            self.alt = alt
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)

        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        if isDarkTheme():
            painter.setBrush(QColor(80, 80, 80))
        else:
            painter.setBrush(QColor(240, 240, 240))

        painter.drawEllipse(8, 6, 24, 24)

        if not self.avatar.isNull():
            mask = QImage(24, 24, QImage.Format_ARGB32)
            mask.fill(Qt.transparent)

            mask_painter = QPainter(mask)
            mask_painter.setRenderHints(QPainter.Antialiasing)
            mask_painter.setBrush(QBrush(self.avatar))
            mask_painter.setPen(Qt.NoPen)
            mask_painter.drawEllipse(0, 0, 24, 24)
            mask_painter.end()

            painter.drawImage(8, 6, mask)

        if not self.isCompacted:
            color = QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)
            painter.setPen(color)
            font = QFont("Segoe UI")
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, self.alt)


class ProfileCard(QWidget):
    def __init__(self, avatar: str, nickname: str, steamID: str, parent=None):
        super().__init__(parent=parent)
        avatarUrl = os.path.join("src", "images", "default-avatar.png")
        if avatar:
            avatarUrl = avatar
        self.avatar = AvatarWidget(avatarUrl, self)
        self.avatar.setText(nickname)
        self.nameLabel = BodyLabel(nickname if nickname else t.not_logged_in, self)
        self.idLabel = CaptionLabel(steamID if steamID else "", self)

        self.setFixedSize(250, 72)
        self.avatar.move(2, 6)
        self.avatar.setRadius(24)
        self.nameLabel.move(64, 13)
        self.idLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))
        self.idLabel.move(64, 32)


class Navigation(NavigationInterface):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.user = self.parent.user

        self.initNavigation()

    def createNavItems(self):
        self.avatar = NavAvatar(
            url=self.user.getAvatar(),
            alt=self.user.getNickname(),
            parent=self,
        )
        self.profile_card = ProfileCard(
            self.user.getAvatar(),
            self.user.getNickname(),
            self.user.getSteamID(),
            parent=self,
        )

        self.profile_menu = RoundMenu(parent=self)
        self.updateMenu(self.user.getLoginStatus())

        self.functions = NavClassTitle(t.functions, self)
        self.tools = NavClassTitle(t.tools, self)

        self.home = NavItem(
            Icon.fromName("Home20Regular"),
            Icon.fromName("Home20Filled"),
            t.home_title,
        )
        self.convert = NavItem(
            Icon.fromName("ArrowSyncCircle20Regular"),
            Icon.fromName("ArrowSyncCircle20Filled"),
            t.convert_title,
        )
        self.deployment = NavItem(
            Icon.fromName("CloudArrowUp20Regular"),
            Icon.fromName("CloudArrowUp20Filled"),
            t.deployment_title,
        )
        self.editor = NavItem(
            Icon.fromName("EditLineHorizontal320Regular"),
            Icon.fromName("EditLineHorizontal320Filled"),
            t.editor_title,
        )
        self.message = NavItem(
            Icon.fromName("ChatArrowBackDown20Regular"),
            Icon.fromName("ChatArrowBackDown20Filled"),
            t.message_title,
        )
        self.char = NavItem(
            Icon.fromName("GridDots20Regular"),
            Icon.fromName("GridDots20Filled"),
            t.char_title,
        )
        self.level = NavItem(
            Icon.fromName("Calculator20Regular"),
            Icon.fromName("Calculator20Filled"),
            t.level_title,
        )
        self.feedback = NavItem(
            Icon.fromName("PersonFeedback20Regular"),
            Icon.fromName("PersonFeedback20Filled"),
            t.feedback,
            selectable=False,
        )
        self.log = NavItem(
            Icon.fromName("PulseSquare20Regular"),
            Icon.fromName("PulseSquare20Filled"),
            t.log_title,
        )
        self.about = NavItem(
            Icon.fromName("Info20Regular"),
            Icon.fromName("Info20Filled"),
            t.about_title,
        )

    def initNavigation(self):
        self.createNavItems()

        self.addWidget(
            routeKey="avatar",
            widget=self.avatar,
            onClick=lambda: self.showMenu(),
            tooltip=self.user.getNickname() or t.not_logged_in,
        )
        self.addWidget(
            routeKey="home",
            widget=self.home,
            onClick=lambda: self.parent.switchInterface("home"),
            tooltip=t.home_title,
        )
        self.addSeparator()
        self.addWidget(
            routeKey="functions",
            widget=self.functions,
        )
        self.addWidget(
            routeKey="convert",
            widget=self.convert,
            onClick=lambda: self.parent.switchInterface("convert"),
            tooltip=t.convert_title,
        )
        self.addWidget(
            routeKey="deployment",
            widget=self.deployment,
            onClick=lambda: self.parent.switchInterface("deployment"),
            tooltip=t.deployment_title,
        )
        self.addSeparator()
        self.addWidget(
            routeKey="tools",
            widget=self.tools,
        )
        self.addWidget(
            routeKey="editor",
            widget=self.editor,
            onClick=lambda: self.parent.switchInterface("editor"),
            tooltip=t.editor_title,
        )
        self.addWidget(
            routeKey="message",
            widget=self.message,
            onClick=lambda: self.parent.switchInterface("message"),
            tooltip=t.message_title,
        )
        self.addWidget(
            routeKey="char",
            widget=self.char,
            onClick=lambda: self.parent.switchInterface("char"),
            tooltip=t.char_title,
        )
        self.addWidget(
            routeKey="level",
            widget=self.level,
            onClick=lambda: self.parent.switchInterface("level"),
            tooltip=t.level_title,
        )

        self.addWidget(
            routeKey="feedback",
            widget=self.feedback,
            onClick=lambda: self.parent.openFeedback(),
            position=NavigationItemPosition.BOTTOM,
            tooltip=t.feedback,
        )
        self.addWidget(
            routeKey="log",
            widget=self.log,
            onClick=lambda: self.parent.switchInterface("log"),
            position=NavigationItemPosition.BOTTOM,
            tooltip=t.log_title,
        )
        self.addSeparator(position=NavigationItemPosition.BOTTOM)
        self.addWidget(
            routeKey="about",
            widget=self.about,
            onClick=lambda: self.parent.switchInterface("about"),
            position=NavigationItemPosition.BOTTOM,
            tooltip=t.about_title,
        )

        self.functions.hide()
        self.tools.hide()

        self.setExpandWidth(200)
        self.setCurrentItem("home")
        self.displayModeChanged.connect(lambda: self.updateNav())

    def updateNav(self):
        expanded = not self.functions.isVisible()

        if expanded:
            self.functions.show()
            self.tools.show()
        else:
            self.functions.hide()
            self.tools.hide()

    def updateMenu(self, status):
        self.profile_menu.clear()

        self.profile_menu.addWidget(self.profile_card, selectable=False)
        if status:
            self.profile_menu.addAction(
                Action(
                    FluentIcon.DOCUMENT,
                    self.tr("Your Profile"),
                    triggered=lambda: QDesktopServices.openUrl(
                        QUrl(
                            f"https://steamcommunity.com/profiles/{self.user.getSteamID()}"
                        )
                    ),
                )
            )
        self.profile_menu.addSeparator()
        if status:
            self.profile_menu.addAction(
                Action(
                    Icon.fromName("ArrowExit20Regular"),
                    self.tr("Logout"),
                    triggered=lambda: self.user.logout(),
                )
            )
        else:
            self.profile_menu.addAction(
                Action(
                    Icon.fromName("ArrowEnter20Regular"),
                    self.tr("Login"),
                    triggered=lambda: self.user.login(),
                )
            )

    def showMenu(self):
        self.profile_menu.exec(
            pos=QPoint(
                self.parent.pos().x() + 40,
                self.parent.pos().y() + 30,
            ),
            ani=True,
            aniType=MenuAnimationType.FADE_IN_DROP_DOWN,
        ),
