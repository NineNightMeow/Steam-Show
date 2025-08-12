from qframelesswindow.webengine import FramelessWebEngineView


class Webview(FramelessWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("webview")

    def run(self, script):
        self.page().runJavaScript(script)
        print(f"Successfully runned script:\n{script}")
