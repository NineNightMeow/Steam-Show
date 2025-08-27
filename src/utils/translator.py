from PySide6.QtCore import QObject, QLocale


def getLang(langCode: str) -> str:
    lang_map = {
        "en_US": "en",
        "zh_CN": "zh_CN",
        "zh_SG": "zh_CN",
        "zh_HK": "zh_TW",
        "zh_MO": "zh_TW",
        "zh_TW": "zh_TW",
        "ja": "ja_JP",
    }
    return lang_map.get(langCode, "en")


def getLocale(langCode: str) -> QLocale:
    locale_map = {
        "en": QLocale(QLocale.English, QLocale.UnitedStates),
        "zh_CN": QLocale(QLocale.Chinese, QLocale.China),
        "zh_TW": QLocale(QLocale.Chinese, QLocale.HongKong),
        "ja_JP": QLocale(QLocale.Japanese, QLocale.Japan),
    }
    return locale_map.get(
        getLang(langCode), QLocale(QLocale.English, QLocale.UnitedStates)
    )


class Translator(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.functions = self.tr("Functions")
        self.tools = self.tr("Tools")
        self.feedback = self.tr("Feedback")
        self.not_logged_in = self.tr("Not logged in")
        self.home_title = self.tr("Home")
        self.home_subtitle = self.tr("Welcome to Steam Show")
        self.convert_title = self.tr("Convert")
        self.deployment_title = self.tr("Deployment")
        self.editor_title = self.tr("Editor")
        self.message_title = self.tr("Batch Messages")
        self.char_title = self.tr("ASCII Art")
        self.char_subtitle = self.tr("Generate an ASCII art from a picture")
        self.level_title = self.tr("Level Calculator")
        self.level_subtitle = self.tr("Calculate experience needs to level up")
        self.log_title = self.tr("Log")
        self.log_subtitle = self.tr("Please send logs here to the developers")
        self.about_title = self.tr("About")
        self.login_title = self.tr("Login")
