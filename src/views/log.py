import sys
import os
import inspect

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import PushButton, TextBrowser, FluentIcon

from src.views.interface import Interface
from src.utils.translator import Translator


class LogStream:
    def __init__(self, append_callback):
        self.append_callback = append_callback

    def write(self, text):
        if text.strip():
            frame = inspect.currentframe()
            while frame:
                info = inspect.getframeinfo(frame)
                if info.filename != __file__ and not info.filename.endswith("io.py"):
                    module_name = os.path.splitext(os.path.basename(info.filename))[0]
                    break
                frame = frame.f_back
            else:
                module_name = "Unknown"

            text = f"[{module_name.capitalize()}] {text.strip()}"
            self.append_callback(text)

    def flush(self):
        pass


class Log(Interface):
    def __init__(self):
        super().__init__(
            title=Translator().log_title,
            subtitle=Translator().log_subtitle,
        )
        self.setObjectName("log")

        layout = QVBoxLayout(self.view)

        self.toolbar = QWidget(self)
        self.toolbarLayout = QHBoxLayout(self.toolbar)

        self.feedback_button = PushButton(FluentIcon.FEEDBACK, self.tr("Feedback"))
        self.feedback_button.clicked.connect(self.on_feedback)

        self.save_button = PushButton(FluentIcon.SAVE, self.tr("Save"))
        self.save_button.clicked.connect(self.save_log)

        self.toolbarLayout.addStretch()
        self.toolbarLayout.addWidget(self.feedback_button)
        self.toolbarLayout.addWidget(self.save_button)
        self.toolbar.setLayout(self.toolbarLayout)

        self.log = TextBrowser()
        self.log.setReadOnly(True)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.log)

        self.view.setLayout(layout)

        sys.stdout = LogStream(self.append_log)
        sys.stderr = LogStream(self.append_log)

    def append_log(self, text):
        self.log.append(text)

    def on_feedback(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/NineNightMeow/Steam-Show/issues")
        )

    def save_log(self):
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save"),
            "log.txt",
            self.tr("Text files") + " (*.txt)",
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.log.toPlainText())
