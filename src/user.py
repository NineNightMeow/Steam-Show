from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from qfluentwidgets import SubtitleLabel, IndeterminateProgressBar, MessageBoxBase

from src.utils.webview import Webview


class LogoutDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr("Logging out"))
        self.progressBar = IndeterminateProgressBar(self)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.progressBar)
        self.yesButton.hide()

        self.widget.setMinimumWidth(350)


class User(QObject):
    """用户信息"""

    infoUpdated = pyqtSignal()
    loginStatusChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loginStatus: bool = False
        self.steamID: str = ""
        self.username: str = ""
        self.nickname: str = ""
        self.avatar: str = ""

        self.webview = Webview(parent)
        self.webview.hide()
        self.webview.urlChanged.connect(self.onUrlChanged)
        self.webview.loadFinished.connect(lambda: QTimer.singleShot(1500, self.getInfo))
        self.webview.open("https://store.steampowered.com/account/")

    def login(self) -> bool:
        """登录"""
        if not self.loginStatus:
            self.webview.open("https://steamcommunity.com/login/")
            return True
        return False

    def logout(self) -> None:
        """注销"""
        # dialog = LogoutDialog(self)
        # if not dialog.exec():
        #    return

        self.webview.run("Logout();")
        self._clearUserInfo()
        print("Successfully logged out")

    def getInfo(self) -> bool:
        """获取用户信息"""
        if not "store.steampowered.com/account/" in self.webview.url().toString():
            return

        print("Getting user info...")
        try:
            import re

            steam_id_text = (
                self.webview.run(
                    """
            document.querySelector(".youraccount_steamid").textContent;
            """
                )
                or ""
            )
            match = re.search(r"\d+", steam_id_text)
            self.steamID = match.group(0) if match else ""
            print(f"SteamID: {self.steamID}")

            username_text = (
                self.webview.run(
                    """
            document.querySelector(".youraccount_pageheader").textContent;
            """
                )
                or ""
            )
            match = re.search(r"^(.+?)'s Account$", username_text)
            self.username = match.group(1) if match else ""
            print(f"Username: {self.username}")

            self.nickname = (
                self.webview.run(
                    """
            document.querySelector(".user_avatar img").alt;
            """
                )
                or ""
            )
            print(f"Nickname: {self.nickname}")

            self.avatar = (
                self.webview.run(
                    """
            document.querySelector(".user_avatar img").src;
            """
                )
                or ""
            )
            print(f"Avatar: {self.avatar}")

            # 验证登录状态
            old_status = self.loginStatus
            self.loginStatus = bool(self.steamID and self.username)

            self.infoUpdated.emit()
            if old_status != self.loginStatus:
                self.loginStatusChanged.emit(self.loginStatus)

            return self.loginStatus

        except Exception as e:
            print(f"获取用户信息失败: {e}")
            old_status = self.loginStatus
            self.loginStatus = False
            if old_status != self.loginStatus:
                self.loginStatusChanged.emit(self.loginStatus)
            return False

    def getLoginStatus(self) -> bool:
        return self.loginStatus

    def getSteamID(self) -> str:
        return self.steamID

    def getUsername(self) -> str:
        return self.username

    def getNickname(self) -> str:
        return self.nickname

    def getAvatar(self) -> str:
        return self.avatar

    def onUrlChanged(self, url) -> None:
        current_url = url.toString()

        if "login" in current_url:
            self._clearUserInfo()
        else:
            self.webview.open("https://store.steampowered.com/account/")

    def _clearUserInfo(self) -> None:
        """清空用户信息"""
        old_status = self.loginStatus
        self.loginStatus = False
        self.steamID = ""
        self.username = ""
        self.nickname = ""
        self.avatar = ""

        if old_status != self.loginStatus:
            self.loginStatusChanged.emit(self.loginStatus)
        self.infoUpdated.emit()

    @property
    def is_authenticated(self) -> bool:
        """检查认证状态"""
        return self.loginStatus and all([self.steamID, self.username])
