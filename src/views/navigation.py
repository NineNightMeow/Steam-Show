from PySide6.QtCore import (
    Qt,
    QUrl,
    QPoint,
    QRect,
)
from PySide6.QtGui import (
    QFont,
    QPainter,
    QColor,
    QBrush,
    QDesktopServices,
)
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    NavigationInterface,
    NavigationWidget,
    NavigationItemPosition,
    AvatarWidget,
    BodyLabel,
    CaptionLabel,
    IconWidget,
    PrimaryPushButton,
    Action,
    RoundMenu,
    MenuAnimationType,
    Flyout,
    FlyoutViewBase,
    FlyoutAnimationType,
    FluentIcon,
    isDarkTheme,
)
from qframelesswindow.utils import getSystemAccentColor

from src.utils.translator import Translator
from src.icons.icons import Icon
from src.utils.avatar import getAvatar
from src.user import User


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
            font = QFont()
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
        font = QFont()
        font.setPixelSize(14)
        painter.setFont(font)
        painter.drawText(QRect(10, 0, 255, 36), Qt.AlignVCenter, self.text)


class NavAvatar(NavigationWidget):
    def __init__(self, url="", text="", parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = getAvatar(url)
        self.text = text or Translator().not_logged_in

    def updateAvatar(self, url, text):
        self.avatar = getAvatar(url)
        self.text = text or Translator().not_logged_in
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

        if not self.avatar.isNull():
            painter.drawImage(8, 6, self.avatar)

        if not self.isCompacted:
            color = QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)
            painter.setPen(color)
            font = QFont()
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, self.text)


class ProfileCard(QWidget):
    def __init__(self, avatar: str, nickname: str, steamID: str, parent=None):
        super().__init__(parent=parent)

        self.avatar = AvatarWidget("", self)
        self.avatar.setImage(getAvatar(avatar, (48, 48)))
        self.avatar.setText(nickname)
        self.nameLabel = BodyLabel(
            nickname if nickname else Translator().not_logged_in, self
        )
        self.idLabel = CaptionLabel(steamID if steamID else "", self)

        self.setFixedSize(250, 72)
        self.avatar.move(2, 6)
        self.avatar.setRadius(24)
        self.nameLabel.move(64, 13)
        self.idLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))
        self.idLabel.move(64, 32)


class CustomFlyoutView(FlyoutViewBase):
    def __init__(self, text: str = "", action=None, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.addWidget(BodyLabel(text))
        self.vBoxLayout.addWidget(action, alignment=Qt.AlignRight)


class Navigation(NavigationInterface):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.t = Translator()

        self.initNavigation()

    def createNavItems(self):
        themeColor = getSystemAccentColor()

        self.avatar = NavAvatar(
            url=User.get("avatar"),
            text=User.get("nickname"),
            parent=self,
        )

        self.profile_menu = RoundMenu(parent=self)
        self.updateMenu(User.get("status"))

        self.functions = NavClassTitle(self.t.functions, self)
        self.tools = NavClassTitle(self.t.tools, self)

        self.home = NavItem(
            Icon.fromName("Home20Regular"),
            Icon.fromName("Home20Filled").icon(color=themeColor),
            self.t.home_title,
        )
        self.convert = NavItem(
            Icon.fromName("ArrowSyncCircle20Regular"),
            Icon.fromName("ArrowSyncCircle20Filled").icon(color=themeColor),
            self.t.convert_title,
        )
        self.deployment = NavItem(
            Icon.fromName("CloudArrowUp20Regular"),
            Icon.fromName("CloudArrowUp20Filled").icon(color=themeColor),
            self.t.deployment_title,
        )
        self.editor = NavItem(
            Icon.fromName("EditLineHorizontal320Regular"),
            Icon.fromName("EditLineHorizontal320Filled").icon(color=themeColor),
            self.t.editor_title,
        )
        self.message = NavItem(
            Icon.fromName("ChatArrowBackDown20Regular"),
            Icon.fromName("ChatArrowBackDown20Filled").icon(color=themeColor),
            self.t.message_title,
        )
        self.char = NavItem(
            Icon.fromName("GridDots20Regular"),
            Icon.fromName("GridDots20Filled").icon(color=themeColor),
            self.t.char_title,
        )
        self.level = NavItem(
            Icon.fromName("Calculator20Regular"),
            Icon.fromName("Calculator20Filled").icon(color=themeColor),
            self.t.level_title,
        )
        self.feedback = NavItem(
            Icon.fromName("PersonFeedback20Regular"),
            Icon.fromName("PersonFeedback20Filled").icon(color=themeColor),
            self.t.feedback,
            selectable=False,
        )
        self.log = NavItem(
            Icon.fromName("PulseSquare20Regular"),
            Icon.fromName("PulseSquare20Filled").icon(color=themeColor),
            self.t.log_title,
        )
        self.about = NavItem(
            Icon.fromName("Info20Regular"),
            Icon.fromName("Info20Filled").icon(color=themeColor),
            self.t.about_title,
        )

    def initNavigation(self):
        self.createNavItems()

        self.addWidget(
            routeKey="avatar",
            widget=self.avatar,
            onClick=lambda: self.showMenu(),
            tooltip=User.get("nickname") or self.t.not_logged_in,
        )
        self.addWidget(
            routeKey="home",
            widget=self.home,
            onClick=lambda: self.parent.switchInterface("home"),
            tooltip=self.t.home_title,
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
            tooltip=self.t.convert_title,
        )
        self.addWidget(
            routeKey="deployment",
            widget=self.deployment,
            onClick=lambda: self.parent.switchInterface("deployment"),
            tooltip=self.t.deployment_title,
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
            tooltip=self.t.editor_title,
        )
        self.addWidget(
            routeKey="message",
            widget=self.message,
            onClick=lambda: self.parent.switchInterface("message"),
            tooltip=self.t.message_title,
        )
        self.addWidget(
            routeKey="char",
            widget=self.char,
            onClick=lambda: self.parent.switchInterface("char"),
            tooltip=self.t.char_title,
        )
        self.addWidget(
            routeKey="level",
            widget=self.level,
            onClick=lambda: self.parent.switchInterface("level"),
            tooltip=self.t.level_title,
        )

        self.addWidget(
            routeKey="feedback",
            widget=self.feedback,
            onClick=lambda: self.openFeedback(),
            position=NavigationItemPosition.BOTTOM,
            tooltip=self.t.feedback,
        )
        self.addWidget(
            routeKey="log",
            widget=self.log,
            onClick=lambda: self.parent.switchInterface("log"),
            position=NavigationItemPosition.BOTTOM,
            tooltip=self.t.log_title,
        )
        self.addSeparator(position=NavigationItemPosition.BOTTOM)
        self.addWidget(
            routeKey="about",
            widget=self.about,
            onClick=lambda: self.parent.switchInterface("about"),
            position=NavigationItemPosition.BOTTOM,
            tooltip=self.t.about_title,
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
        self.avatar.updateAvatar(User.get("avatar"), User.get("nickname"))

        self.profile_card = ProfileCard(
            User.get("avatarFull"),
            User.get("nickname"),
            User.get("id"),
            parent=self,
        )

        self.profile_menu.clear()
        self.profile_menu.addWidget(self.profile_card, selectable=False)
        self.logout_action = Action(
            FluentIcon.EMBED,
            self.tr("Logout"),
            triggered=lambda: self.onLogout(),
        )
        if status:
            self.profile_menu.addActions(
                [
                    Action(
                        FluentIcon.DOCUMENT,
                        self.tr("Your Profile"),
                        triggered=lambda: QDesktopServices.openUrl(
                            QUrl(
                                f"https://steamcommunity.com/profiles/{User.get('id')}"
                            )
                        ),
                    ),
                    self.logout_action,
                ]
            )
        else:
            self.profile_menu.addAction(
                Action(
                    FluentIcon.EMBED,
                    self.tr("Login"),
                    triggered=lambda: User(self.parent).login(),
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

    def openFeedback(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/NineNightMeow/Steam-Show/issues")
        )

    def onLogout(self):
        self.confirm_button = PrimaryPushButton(self.tr("Logout"))
        self.confirm_button.clicked.connect(lambda: self.parent.user.logout())
        self.confirm_button.clicked.connect(lambda: self.confirm_flyout.hide())
        self.confirm_button.setFixedWidth(100)
        self.confirm_flyout = CustomFlyoutView(
            self.tr("Are you sure to logout?"),
            self.confirm_button,
        )
        Flyout.make(
            self.confirm_flyout,
            QPoint(
                self.parent.pos().x() + 40,
                self.parent.pos().y() + 30,
            ),
            self,
            aniType=FlyoutAnimationType.DROP_DOWN,
        )
