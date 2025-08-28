from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout

from src.views.interface import Interface
from src.utils.webview import Webview
from src.utils.translator import Translator


class Login(Interface):
    def __init__(self, user=None, parent=None):
        super().__init__(title=Translator().login_title)
        self.setObjectName("login")

        self.user = user
        self.window = parent

        layout = QVBoxLayout(self.view)

        self.webview = Webview(self.view)
        self.webview.loadFinished.connect(self.onLoadFinished)

        layout.addWidget(self.webview, 1)
        self.view.setLayout(layout)

        self._loggin_out = False
        self.user.infoUpdated.connect(self.onInfoUpdated)

    def onLoadFinished(self, success: bool):
        if not success:
            return

        self.webview.run(
            'document.querySelector(".responsive_header").style.display = "none";'
        )

        current_url = self.webview.url().toString()

        if "/login" in current_url:
            if self.user.get("status"):
                self.user._clear_user_info()

        elif "store.steampowered.com" in current_url:
            if self.user.get("status") and self._loggin_out:
                try:
                    self.webview.run("Logout();")
                    QTimer.singleShot(1000, self.user.getInfo)
                except Exception as e:
                    print("Logout script failed:", e)
            elif not self.user.get("status"):
                self.user.getInfo()

    def onInfoUpdated(self, info):
        if self._loggin_out:
            if not info.get("status"):
                print("Logout success")
                self._loggin_out = False
                self.login()
            return

        if info.get("status"):
            self.window.switchInterface("home")
        else:
            self.login()

    def login(self):
        if (
            not self.user.get("status")
            and "/login" not in self.webview.url().toString()
        ):
            self.webview.open("https://store.steampowered.com/login/")

    def logout(self):
        if (
            self.user.get("status")
            and "/login" not in self.webview.url().toString()
            and "store.steampowered.com" not in self.webview.url().toString()
        ):
            self._loggin_out = True
            self.webview.open("https://store.steampowered.com/")
