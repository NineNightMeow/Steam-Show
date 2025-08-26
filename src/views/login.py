from PySide6.QtWidgets import QVBoxLayout

from src.views.interface import Interface
from src.utils.webview import Webview
from src.utils.translator import Translator


class Login(Interface):
    def __init__(self):
        super().__init__(title=Translator().login_title)
        self.setObjectName("login")

        layout = QVBoxLayout(self.view)

        self.webview = Webview(self.view)
        self.webview.urlChanged.connect(self.onUrlChanged)
        self.webview.open("https://store.steampowered.com/login/")

        layout.addWidget(self.webview, 1)
        self.view.setLayout(layout)

    def onUrlChanged(self):
        url = self.webview.url().toString()
        if not url.startswith("https://store.steampowered.com/login/"):
            self.window().switchInterface("home")
