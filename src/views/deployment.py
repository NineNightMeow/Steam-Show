from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    PushButton,
    PrimaryPushButton,
    DropDownPushButton,
    RoundMenu,
    Action,
    FluentIcon,
)

from src.views.interface import Interface, InfoTip, Separator
from src.utils.translator import Translator
from src.utils.webview import Webview


class Deployment(Interface):
    def __init__(self, window):
        super().__init__(title=Translator().deployment_title)
        self.setObjectName("deployment")

        self.window = window

        layout = QVBoxLayout(self)

        # 工具栏
        self.tool_bar = QHBoxLayout()

        self.refresh_button = PushButton(FluentIcon.SYNC, self.tr("Refresh"))
        self.upload_button = PushButton(FluentIcon.FOLDER, self.tr("Upload"))
        self.submit_button = PrimaryPushButton(FluentIcon.SEND, self.tr("Submit"))

        self.refresh_button.clicked.connect(self.onReload)
        self.upload_button.clicked.connect(self.onUpload)
        self.submit_button.clicked.connect(self.onSubmit)

        self.command_menu = DropDownPushButton(FluentIcon.CODE, self.tr("Commands"))

        menu = RoundMenu(parent=self.command_menu)
        menu.addAction(
            Action(
                FluentIcon.HIDE,
                self.tr("Anonymous"),
                triggered=lambda: self.send_script(
                    "$J('[name=consumer_app_id]').val(480);$J('[name=file_type]').val(0);$J('[name=visibility]').val(0);"
                ),
            )
        )
        menu.addAction(
            Action(
                FluentIcon.PHOTO,
                self.tr("Artworks"),
                triggered=lambda: self.send_script(
                    "$J('#image_width').val(1000).attr('id',''),$J('#image_height').val(1).attr('id','');"
                ),
            )
        )
        menu.addAction(
            Action(
                FluentIcon.TILES,
                self.tr("Workshop"),
                triggered=lambda: self.send_script(
                    "$J('[name=consumer_app_id]').val(480);$J('[name=file_type]').val(0);$J('[name=visibility]').val(0);"
                ),
            )
        )
        menu.addAction(
            Action(
                FluentIcon.DICTIONARY,
                self.tr("Guide"),
                triggered=lambda: self.send_script(
                    "$J('[name=consumer_app_id]').val(480);$J('[name=file_type]').val(9);$J('[name=visibility]').val(0);"
                ),
            )
        )
        menu.addAction(
            Action(
                FluentIcon.CAMERA,
                self.tr("Screenshot"),
                triggered=lambda: self.send_script(
                    "$J('#image_width').val(1000).attr('id',''),$J('#image_height').val(1).attr('id',''),$J('[name=file_type]').val(5);"
                ),
            )
        )

        self.command_menu.setMenu(menu)

        self.tool_bar.addWidget(self.refresh_button)
        self.tool_bar.addWidget(Separator())
        self.tool_bar.addWidget(self.upload_button)
        self.tool_bar.addWidget(self.command_menu)
        self.tool_bar.addWidget(self.submit_button)

        # Webview
        self.webview = Webview(self.view)
        self.webview.loadFinished.connect(self.onLoaded)

        self.defaultUrl = "https://steamcommunity.com/sharedfiles/edititem/767/3/"
        self.webview.open(self.defaultUrl)

        layout.addLayout(self.tool_bar)
        layout.addWidget(self.webview, 1)

        self.view.setLayout(layout)

    def onLoaded(self):
        self.webview.urlChanged.connect(self.onUrlChanged)
        self.webview.run(
            'document.querySelector("#global_header").style.display = "none";'
        )
        self.webview.run('document.querySelector("#footer").style.display = "none";')
        self.webview.run('document.querySelector("#agree_terms").checked = true;')

    def onUrlChanged(self, url):
        if url != self.defaultUrl:
            if "https://steamcommunity.com/login" in url:
                InfoTip(
                    type="error",
                    title=self.tr("Please login first"),
                    parent=self.window,
                )
            else:
                InfoTip(
                    type="success",
                    title=self.tr("Successfully uploaded"),
                    message=self.tr("Reloading"),
                    parent=self.window,
                )
            self.webview.open(self.defaultUrl)

    def onReload(self):
        self.webview.reload()

    def onUpload(self):
        self.webview.run("document.querySelector('#file').click();")

    def send_script(self, script):
        print("Sent script to webview")
        self.webview.run(script, console=True)

        InfoTip(
            type="success",
            title=self.tr("Successfully executed"),
            message=self.tr("Script sent"),
            parent=self.window,
        )

    def onSubmit(self):
        self.webview.run("SubmitItem();")
