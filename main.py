import sys
import os

from PyQt5.QtCore import QUrl, QSize, QLocale, QTranslator
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (
    SplashScreen,
    FluentWindow,
    NavigationItemPosition,
    MessageBox,
    FluentIcon,
    FluentTranslator,
    Theme,
    SystemThemeListener,
    setTheme,
)

from src.views.convert import Convert
from src.views.deployment import Deployment
from src.views.log import Log
from src.views.about import About


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self._init_window()

        self.task_stack = []

        self.splashScreen = SplashScreen(
            QIcon(os.path.join("src", "icons", "splash_icon.png")), self
        )
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
        self.setWindowIcon(QIcon(os.path.join("src", "icons", "favicon.ico")))

        self.setFixedSize(600, 900)
        self.titleBar.maxBtn.hide()
        self.titleBar.setDoubleClickEnabled(False)

        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        center_point = screen.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())
        setTheme(Theme.AUTO)

    def createSubInterface(self):
        self.convert = Convert()
        self.deployment = Deployment()
        self.log = Log()
        self.about = About()

    def initNavigation(self):
        self.addSubInterface(self.convert, FluentIcon.SYNC, self.tr("Convert"))
        self.addSubInterface(
            self.deployment, FluentIcon.COMMAND_PROMPT, self.tr("Deployment")
        )
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
            FluentIcon.MESSAGE,
            self.tr("Log"),
            position=NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.addSeparator(position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.about,
            FluentIcon.INFO,
            self.tr("About"),
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setExpandWidth(200)

    def openFeedback(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/NineNightMeow/Steam-Show/issues")
        )

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    translator = QTranslator()
    translator.load(QLocale.system().name(), "src/i18n")
    app.installTranslator(translator)
    app.installTranslator(FluentTranslator())

    window = MainWindow()

    sys.exit(app.exec())
