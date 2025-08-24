import sys

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from src.views.window import MainWindow
from src.utils.translator import getLang, getLocale


if __name__ == "__main__":
    app = QApplication(sys.argv)

    langCode = QLocale.system().name()
    translator = QTranslator()
    translator.load(getLang(langCode), "src/i18n")
    fluentTranslator = FluentTranslator(getLocale(langCode))
    app.installTranslator(translator)
    app.installTranslator(fluentTranslator)

    window = MainWindow()

    sys.exit(app.exec())
