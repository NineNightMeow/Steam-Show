from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit
from qfluentwidgets import (
    PushButton,
    PrimaryPushButton,
    DropDownPushButton,
    LineEdit,
    RoundMenu,
    Action,
    GroupHeaderCardWidget,
    InfoBar,
    InfoBarPosition,
    TeachingTip,
    TeachingTipTailPosition,
    InfoBarIcon,
    FluentIcon,
)

from src.views.interface import Interface, Separator
from src.utils.translator import Translator
from src.utils.webview import Webview


class Deployment(Interface):
    def __init__(self):
        super().__init__(title=Translator().deployment_title)
        self.setObjectName("deployment")

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
        self.browser = Webview(self)
        self.browser.loadFinished.connect(self.onLoaded)
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)

        self.defaultUrl = "https://steamcommunity.com/sharedfiles/edititem/767/3/"
        self.browser.load(QUrl(self.defaultUrl))

        layout.addLayout(self.tool_bar)
        layout.addWidget(self.browser, 1)

        self.view.setLayout(layout)

    def onLoaded(self):
        self.browser.urlChanged.connect(self.onUrlChanged)
        self.browser.page().runJavaScript(
            'document.querySelector("#global_header").style.display = "none";'
        )
        self.browser.page().runJavaScript(
            'document.querySelector("#footer").style.display = "none";'
        )
        print("Successfully removed header and footer")
        self.browser.page().runJavaScript(
            'document.querySelector("#agree_terms").checked = true;'
        )
        print("Automatically checked agreement radio")

    def onUrlChanged(self, url):
        if url != self.defaultUrl:
            if "https://steamcommunity.com/login" in url:
                InfoBar(
                    title=self.tr("Please login first"),
                    content="",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.window(),
                )
            else:
                InfoBar.success(
                    title=self.tr("Successfully uploaded"),
                    content=self.tr("Reloading"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.window(),
                )
            self.browser.load(QUrl(self.defaultUrl))

    def onReload(self):
        self.browser.reload()

    def onUpload(self):
        self.browser.page().runJavaScript("document.querySelector('#file').click();")

    def send_script(self, script):
        self.browser.page().runJavaScript(script)
        print(f"Sending script:\n{script}")
        InfoBar.success(
            title=self.tr("Successfully executed"),
            content=self.tr("Script sent"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.window(),
        )

    def onSubmit(self):
        self.browser.page().runJavaScript("SubmitItem();")
