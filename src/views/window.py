import os

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    SplashScreen,
    FluentWindow,
    MessageBox,
    Theme,
    SystemThemeListener,
    setTheme,
    setThemeColor,
)
from qframelesswindow.utils import getSystemAccentColor

from src.views.navigation import Navigation
from src.views.home import Home
from src.views.convert import Convert
from src.views.deployment import Deployment
from src.views.editor import Editor
from src.views.message import Message
from src.views.char import Char
from src.views.level import Level
from src.views.log import Log
from src.views.about import About
from src.views.login import Login

from src.user import User


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self._init_window()

        self.user = User(self)
        self.user.infoUpdated.connect(lambda info: self.onUserInfoUpdated(info))

        self.task_stack = []

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

        self.show()

        self.createInterfaces()
        self.navigation = Navigation(self)
        self.old_nav = self.hBoxLayout.itemAt(0).widget()
        self.old_nav.hide()
        self.hBoxLayout.replaceWidget(self.old_nav, self.navigation)

        self.themeListener = SystemThemeListener(self)
        self.themeListener._onThemeChanged = self.onThemeChanged
        self.themeListener.start()

        self.splashScreen.finish()

    def _init_window(self):
        self.setWindowTitle("Steam Show")
        self.setWindowIcon(QIcon(os.path.join("src", "icons", "favicon.ico")))
        self.setFixedSize(600, 900)

        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        center_point = screen.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())

        self.titleBar.iconLabel.hide()
        self.titleBar.maxBtn.hide()
        self.titleBar.setDoubleClickEnabled(False)

        setTheme(Theme.AUTO)
        setThemeColor(getSystemAccentColor(), save=False)

    def createInterfaces(self):
        self.home_interface = Home(self)
        self.convert_interface = Convert(self)
        self.deployment_interface = Deployment(self)
        self.editor_interface = Editor()
        self.message_interface = Message()
        self.char_interface = Char()
        self.level_interface = Level()
        #self.log_interface = Log()
        self.about_interface = About()
        self.login_interface = Login(self.user, self)

        self.addSubInterface(self.home_interface, None, "")
        self.addSubInterface(self.convert_interface, None, "")
        self.addSubInterface(self.deployment_interface, None, "")
        self.addSubInterface(self.editor_interface, None, "")
        self.addSubInterface(self.message_interface, None, "")
        self.addSubInterface(self.char_interface, None, "")
        self.addSubInterface(self.level_interface, None, "")
        #self.addSubInterface(self.log_interface, None, "")
        self.addSubInterface(self.about_interface, None, "")
        self.addSubInterface(self.login_interface, None, "")

    def switchInterface(self, interface: str):
        interfaces = {
            "home": self.home_interface,
            "convert": self.convert_interface,
            "deployment": self.deployment_interface,
            "editor": self.editor_interface,
            "message": self.message_interface,
            "char": self.char_interface,
            "level": self.level_interface,
            #"log": self.log_interface,
            "about": self.about_interface,
            "login": self.login_interface,
        }
        if interface in interfaces:
            self.switchTo(interfaces[interface])
            self.navigation.setCurrentItem(interface)
        else:
            print(f"Page not found: {interface}")

    def onUserInfoUpdated(self, info):
        self.navigation.updateMenu(info.get("status"))

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
