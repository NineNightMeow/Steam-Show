import os

from PyQt5.QtCore import (
    Qt,
    QUrl,
    QSize,
    QPoint,
    QRect,
    QEventLoop,
    QTimer,
)
from PyQt5.QtGui import (
    QIcon,
    QFont,
    QImage,
    QPainter,
    QColor,
    QBrush,
    QDesktopServices,
)
from PyQt5.QtWidgets import QApplication, QWidget
from qfluentwidgets import (
    SplashScreen,
    FluentWindow,
    NavigationWidget,
    NavigationItemPosition,
    AvatarWidget,
    BodyLabel,
    CaptionLabel,
    Action,
    RoundMenu,
    MessageBox,
    FluentIcon,
    Theme,
    SystemThemeListener,
    setTheme,
    isDarkTheme,
)

from src.views.home import Home
from src.views.convert import Convert
from src.views.deployment import Deployment
from src.views.editor import Editor
from src.views.message import Message
from src.views.char import Char
from src.views.level import Level
from src.views.log import Log
from src.views.about import About

from src.user import User
from src.utils.translator import Translator

t = Translator()


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

        painter.setBrush(QBrush(self.avatar))
        painter.translate(8, 6)
        painter.drawEllipse(0, 0, 24, 24)
        painter.translate(-8, -6)

        if not self.isCompacted:
            painter.setPen(Qt.white if isDarkTheme() else Qt.black)
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


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self._init_window()

        self.user = User(self)
        self.user.infoUpdated.connect(self.onUserInfoUpdated)
        self.user.loginStatusChanged.connect(self.onLoginStatusChanged)
        print(f"User Info: {self.user}")

        self.task_stack = []

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

        self.setMicaEffectEnabled(False)

        self.show()

        self.createSubInterface()
        self.initNavigation()

        self.themeListener = SystemThemeListener(self)
        self.themeListener._onThemeChanged = self.onThemeChanged
        self.themeListener.start()

        self.splashScreen.finish()

    def _init_window(self):
        self.setWindowTitle("Steam Show")
        self.setWindowIcon(QIcon(os.path.join("src", "icons", "favicon.png")))

        self.setFixedSize(600, 900)
        self.titleBar.iconLabel.hide()
        self.titleBar.maxBtn.hide()
        self.titleBar.setDoubleClickEnabled(False)

        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        center_point = screen.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())
        setTheme(Theme.AUTO)

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(500, loop.quit)
        loop.exec()

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

        self.home = Home(self)
        self.convert = Convert(self)
        self.deployment = Deployment(self)
        self.editor = Editor()
        self.message = Message()
        self.char = Char()
        self.level = Level()
        self.log = Log()
        self.about = About()

        self.interfaces = {
            "home": self.home,
            "convert": self.convert,
            "deployment": self.deployment,
            "editor": self.editor,
            "message": self.message,
            "char": self.char,
            "level": self.level,
            "log": self.log,
            "about": self.about,
        }

    def initNavigation(self):
        self.navigationInterface.displayModeChanged.connect(lambda: self.updateNav())

        self.addSubInterface(self.home, FluentIcon.HOME, t.home_title)
        self.navigationInterface.addSeparator()
        self.navigationInterface.addWidget(routeKey="functions", widget=self.functions)
        self.addSubInterface(self.convert, FluentIcon.SYNC, t.convert_title)
        self.addSubInterface(self.deployment, FluentIcon.CLOUD, t.deployment_title)
        self.navigationInterface.addSeparator()
        self.navigationInterface.addWidget(routeKey="tools", widget=self.tools)
        self.addSubInterface(self.editor, FluentIcon.PENCIL_INK, t.editor_title)
        self.addSubInterface(self.message, FluentIcon.MESSAGE, t.message_title)
        self.addSubInterface(self.char, FluentIcon.PHOTO, t.char_title)
        self.addSubInterface(self.level, FluentIcon.MARKET, t.level_title)

        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=self.avatar,
            onClick=lambda: self.profile_menu.exec(
                pos=QPoint(self.pos().x() + 50, self.pos().y() + self.height() - 200),
                ani=True,
            ),
            position=NavigationItemPosition.BOTTOM,
            tooltip=self.user.getNickname() or t.not_logged_in,
        )
        self.navigationInterface.addSeparator(position=NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem(
            routeKey="feedback",
            icon=FluentIcon.FEEDBACK,
            text=f"{self.tr('Feedback')}",
            onClick=self.openFeedback,
            selectable=False,
            tooltip=self.tr("Feedback"),
            position=NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(
            self.log,
            FluentIcon.COMMAND_PROMPT,
            t.log_title,
            position=NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.addSeparator(position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.about,
            FluentIcon.INFO,
            t.about_title,
            position=NavigationItemPosition.BOTTOM,
        )

        self.functions.hide()
        self.tools.hide()

        self.navigationInterface.setExpandWidth(200)

    def openFeedback(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/NineNightMeow/Steam-Show/issues")
        )

    def onUserInfoUpdated(self):
        print(f"User Info Updated:")
        print(f"-> Username: {self.user.getUsername()}")
        print(f"-> Nickname: {self.user.getNickname()}")
        print(f"-> SteamID: {self.user.getSteamID()}")
        print(f"-> Avatar: {self.user.getAvatar()}")
        print(f"-> Login Status: {self.user.getLoginStatus()}")

        if hasattr(self, "avatar"):
            self.avatar.updateAvatar(self.user.getAvatar(), self.user.getNickname())

    def onLoginStatusChanged(self, status):
        print(f"Login Status Changed: {status}")

        self.updateMenu(status)

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
                    FluentIcon.EMBED,
                    self.tr("Logout"),
                    triggered=lambda: self.user.logout(),
                )
            )
        else:
            self.profile_menu.addAction(
                Action(
                    FluentIcon.EMBED,
                    self.tr("Login"),
                    triggered=lambda: self.user.login(),
                )
            )

    def switchInterface(self, interface: str):
        if interface in self.interfaces:
            FluentWindow.switchTo(self, self.interfaces[interface])
        else:
            print(f"Page not found: {interface}")

    def onThemeChanged(self, theme: str):
        if theme == "Dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)

    def closeEvent(self, event):
        if self.task_stack:
            confirm = MessageBox(
                self.tr("Confirm to quit"),
                self.tr("There are still unfinished tasks. Are you sure to quit?"),
                self,
            )
            confirm.yesButton.setText(self.tr("Quit"))
            confirm.cancelButton.setText(self.tr("Cancel"))

            if confirm.exec():
                event.accept()
                self.themeListener.terminate()
                self.themeListener.deleteLater()
            else:
                event.ignore()
