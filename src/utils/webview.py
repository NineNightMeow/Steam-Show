from PyQt5.QtCore import Qt, QUrl
from qframelesswindow.webengine import FramelessWebEngineView


class Webview(FramelessWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("webview")

        self.setContextMenuPolicy(Qt.NoContextMenu)

    def open(self, url: str):
        self.load(QUrl(url))

    def run(self, script: str, console=False):
        if console:
            print("Run JavaScript:", script[:100])

        try:
            return self.page().runJavaScript(script)
        except Exception as e:
            print("Error running JavaScript", e)
            return
