from PyQt5.QtCore import QObject


class Translator(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.convert_title = self.tr("Convert")
        self.deployment_title = self.tr("Deployment")
        self.log_title = self.tr("Log")
        self.log_subtitle = self.tr("Please send logs here to the developers")
        self.about_title = self.tr("About")
