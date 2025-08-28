import os
import json
import re

from PySide6.QtCore import QObject, Signal

from src.utils.webview import Webview
from src.app import App


class User(QObject):
    """用户信息"""

    infoUpdated = Signal(dict)
    backgroundUpdated = Signal(str)

    _instance = None
    _initialized = False

    _info = {
        "status": False,
        "id": "",
        "username": "",
        "nickname": "",
        "avatar": "",
        "avatarFull": "",
        "background": "",
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if User._initialized:
            return
        super().__init__(parent)
        User._initialized = True

        self.parent = parent

        # 路径 & 配置文件
        path = App.getPath("config")
        self.config = os.path.join(path, "user.json")
        if not os.path.exists(self.config):
            with open(self.config, "w") as f:
                json.dump(User._info, f)

        # 状态
        self._current_url = ""
        self._fetching_info = False
        self._fetching_bg = False

        # Webview
        self.webview = Webview(self.parent)
        self.webview.hide()
        self.webview.urlChanged.connect(self.onUrlChanged)
        self.webview.loadFinished.connect(self.onLoadFinished)

        # 加载用户信息
        self.load_user_info()
        if not User._info["status"]:
            self.getInfo()

    # ---------------- 公共接口 ----------------
    @classmethod
    def get(cls, key, default=None):
        return cls._info.get(key, default)

    @classmethod
    def set(cls, key, value):
        cls._info[key] = value
        if cls._instance:
            cls._instance.save_user_info()
            cls._instance.send_signal()

    @classmethod
    def all(cls):
        return dict(cls._info)

    # ---------------- 用户操作 ----------------
    def login(self) -> bool:
        self.parent.switchInterface("login")
        self.parent.login_interface.login()

    def logout(self) -> None:
        self.parent.switchInterface("login")
        self.parent.login_interface.logout()

    # ---------------- 获取信息 ----------------
    def getInfo(self):
        if "store.steampowered.com/account/" in self._current_url:
            if self._fetching_info:
                return
            self._fetching_info = True
            print("Getting user info...")
            self.webview.run(self._js_user_info(), self._on_info_result)
        else:
            self.webview.open("https://store.steampowered.com/account/")

    def getBg(self):
        if "profiles/" in self._current_url or "id/" in self._current_url:
            if self._fetching_bg:
                return
            self._fetching_bg = True
            print("Getting background image...")
            self.webview.run(self._js_background(), self._on_bg_result)
        else:
            if User._info["id"]:
                url = f"https://steamcommunity.com/profiles/{User._info['id']}"
                print(f"Opening profile page: {url}")
                self.webview.open(url)
            else:
                print("Failed to fetch background image: No user ID")

    # ---------------- 结果处理 ----------------
    def _on_info_result(self, result_json):
        self._fetching_info = False
        try:
            result = json.loads(result_json or "{}")
            if result.get("error"):
                print(f"Failed to get user info: {result['error']}")
                return

            if not result.get("isLoggedIn"):
                print("Not logged in")
                self._clear_user_info()
                return

            self._update_user_info(result)
            self.save_user_info()
            self.send_signal()

        except Exception as e:
            print(f"Failed to parse user info: {e}")
            self._clear_user_info()

    def _on_bg_result(self, result):
        self._fetching_bg = False
        if result:
            User._info["background"] = result
            self.backgroundUpdated.emit(result)
            print("Successfully fetched background image:", result)
        else:
            self.backgroundUpdated.emit("")
            print("Failed to fetch background image")

    # ---------------- 内部工具 ----------------
    def _update_user_info(self, result: dict):
        steamID = self._extract_steam_id(result.get("steamID", ""))
        username = self._extract_username(result.get("username", ""))
        nickname = result.get("nickname", username)
        avatar = result.get("avatar", "")

        User._info.update(
            {
                "status": bool(steamID and username),
                "id": steamID,
                "username": username,
                "nickname": nickname,
                "avatar": avatar,
                "avatarFull": avatar.replace(".jpg", "_full.jpg") if avatar else "",
            }
        )

    def _extract_steam_id(self, text):
        m = re.search(r"\d+", text)
        return m.group(0) if m else ""

    def _extract_username(self, text):
        m = re.search(r"^(.+?)'s Account$", text)
        return m.group(1) if m else text

    def _clear_user_info(self):
        User._info.update(
            {
                "status": False,
                "id": "",
                "username": "",
                "nickname": "",
                "avatar": "",
                "avatarFull": "",
                "background": "",
            }
        )
        self.save_user_info()
        self.send_signal()
        print("Successfully cleared user info")

    # ---------------- 存取 ----------------
    def save_user_info(self):
        with open(self.config, "w") as f:
            json.dump(User._info, f)
        print("Successfully saved user info")

    def load_user_info(self):
        try:
            with open(self.config, "r") as f:
                User._info = json.load(f)
            self.send_signal()
        except FileNotFoundError:
            print("Failed to load user info: File not found")

    def send_signal(self):
        print(f"╭─ User Info Updated: ───")
        for k, v in User._info.items():
            print(f"│ {k}: {v}")
        print(f"╰─────────────────")
        self.infoUpdated.emit(dict(User._info))

    # ---------------- 事件回调 ----------------
    def onUrlChanged(self, url):
        self._current_url = url.toString()
        if "login/" in self._current_url and User._info["status"]:
            self._clear_user_info()

    def onLoadFinished(self, success: bool):
        if success:
            if "account/" in self._current_url:
                self.getInfo()
            elif "profiles/" in self._current_url or "id/" in self._current_url:
                self.getBg()

    # ---------------- JS 脚本 ----------------
    def _js_user_info(self):
        return """
        (function() {
            try {
                var steamIDElement = document.querySelector(".youraccount_steamid");
                var headerElement = document.querySelector(".youraccount_pageheader");
                var avatarElement = document.querySelector(".user_avatar img");

                var steamID = steamIDElement ? steamIDElement.textContent.trim() : "";
                var username = headerElement ? headerElement.textContent.trim() : "";
                var nickname = avatarElement ? avatarElement.alt : "";
                var avatar = avatarElement ? avatarElement.src : "";

                var isLoggedIn = !document.querySelector(".youraccount_login");

                return JSON.stringify({
                    steamID: steamID,
                    username: username,
                    nickname: nickname,
                    avatar: avatar,
                    isLoggedIn: isLoggedIn
                });
            } catch (e) {
                return JSON.stringify({error: e.message});
            }
        })();
        """

    def _js_background(self):
        return """
        (function() {
            var bgElement = document.querySelectorAll(".has_profile_background")[1];
            if (bgElement) {
                var style = window.getComputedStyle(bgElement);
                var bgImage = style.backgroundImage;
                if (bgImage.startsWith('url("') && bgImage.endsWith('")')) {
                    return bgImage.slice(5, -2);
                }
            }
            return "";
        })();
        """
