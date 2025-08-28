import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
)
from qframelesswindow.webengine import FramelessWebEngineView

from src.app import App


class Webview(FramelessWebEngineView):
    _shared_profile = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("webview")
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self._setup_persistent_profile()

        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

    def _setup_persistent_profile(self):
        if Webview._shared_profile is None:
            data_dir = App.getPath("data")
            storage_path = os.path.join(data_dir, "webengine")

            os.makedirs(storage_path, exist_ok=True)

            Webview._shared_profile = QWebEngineProfile("persistent")
            Webview._shared_profile.setPersistentStoragePath(storage_path)
            Webview._shared_profile.setPersistentCookiesPolicy(
                QWebEngineProfile.ForcePersistentCookies
            )
            Webview._shared_profile.setCachePath(os.path.join(storage_path, "cache"))
            Webview._shared_profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)

        page = QWebEnginePage(Webview._shared_profile, self)
        self.setPage(page)

    def open(self, url: str):
        self.load(QUrl(url))

    def run(self, script: str, callback=None, console=False):
        if console:
            print("Run JavaScript:", script[:100])

        try:
            if callback:
                self.page().runJavaScript(script, 0, callback)
            else:
                return self.page().runJavaScript(script)
        except Exception as e:
            print("Error running JavaScript", e)
            if callback:
                callback(None)
            return None
