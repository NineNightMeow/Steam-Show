from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from qfluentwidgets import PushButton, PrimaryPushButton, TextBrowser

from src.views.interface import Interface
from src.utils.translator import Translator
from src.utils.ascii import render


class Char(Interface):
    def __init__(self):
        super().__init__(
            title=Translator().char_title,
            subtitle=Translator().char_subtitle,
        )
        self.setObjectName("char")

        layout = QVBoxLayout()

        self.toolbar = QWidget(self)
        self.toolbarLayout = QHBoxLayout(self.toolbar)

        self.select_button = PushButton(self.tr("Select Image"))
        self.select_button.clicked.connect(self.select_image)

        self.generateButton = PrimaryPushButton(self.tr("Generate"))
        self.generateButton.clicked.connect(self.generate)
        self.generateButton.setEnabled(False)

        self.toolbarLayout.addWidget(self.select_button)
        self.toolbarLayout.addWidget(self.generateButton)

        self.priview = TextBrowser()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.priview, 1)

        self.view.setLayout(layout)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select Image"), "", "Image Files (*.jpg *.png)"
        )
        if file_path:
            self.file_path = file_path
            self.generateButton.setEnabled(True)

    def generate(self):
        if hasattr(self, "file_path"):
            ascii_art = render(
                image_path=self.file_path,
                ascii_width=100,
                threshold=127,
                invert=False,
                ditherer_name="floydSteinberg",
            )
            self.priview.setPlainText(ascii_art)
