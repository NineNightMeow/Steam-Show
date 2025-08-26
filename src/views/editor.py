import os

from PySide6.QtCore import Qt
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from qfluentwidgets import (
    CaptionLabel,
    SubtitleLabel,
    Action,
    TransparentDropDownPushButton,
    SwitchButton,
    LineEdit,
    PlainTextEdit,
    RoundMenu,
    CommandBar,
    MessageBoxBase,
)

from src.views.interface import Interface
from src.utils.translator import Translator
from src.utils.webview import Webview
from src.icons.icons import Icon


class URLDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr("Create a link"))
        self.urlLineEdit = LineEdit()

        self.urlLineEdit.setPlaceholderText(self.tr("Enter a URL"))
        self.urlLineEdit.setClearButtonEnabled(True)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        self.widget.setMinimumWidth(350)


class Editor(Interface):
    def __init__(self):
        super().__init__(title=Translator().editor_title)
        self.setObjectName("editor")

        layout = QVBoxLayout(self)

        # 编辑区域
        # 命令栏
        self.edit_command_bar = CommandBar(self)

        # 标题按钮
        self.title_button = TransparentDropDownPushButton(
            Icon.fromName("TextCaseTitle20Regular"), self.tr("Title")
        )

        self.title_menu = RoundMenu(parent=self)
        self.title_menu.addActions(
            [
                Action(
                    text="H1",
                    triggered=lambda: self.setLabel("h1"),
                ),
                Action(
                    text="H2",
                    triggered=lambda: self.setLabel("h2"),
                ),
                Action(
                    text="H3",
                    triggered=lambda: self.setLabel("h3"),
                ),
            ]
        )

        self.title_button.setMenu(self.title_menu)

        # 添加命令
        self.edit_command_bar.addActions(
            [
                Action(
                    Icon.fromName("TextAlignLeft20Regular"),
                    self.tr("Left"),
                    triggered=lambda: self.setAlign("left"),
                ),
                Action(
                    Icon.fromName("TextAlignCenter20Regular"),
                    self.tr("Center"),
                    triggered=lambda: self.setAlign("center"),
                ),
                Action(
                    Icon.fromName("TextAlignRight20Regular"),
                    self.tr("Right"),
                    triggered=lambda: self.setAlign("right"),
                ),
            ]
        )

        self.edit_command_bar.addSeparator()

        self.edit_command_bar.addWidget(self.title_button)
        self.edit_command_bar.addActions(
            [
                Action(
                    Icon.fromName("TextBold20Regular"),
                    self.tr("Bold"),
                    triggered=lambda: self.setLabel("b"),
                ),
                Action(
                    Icon.fromName("TextItalic20Regular"),
                    self.tr("Italic"),
                    triggered=lambda: self.setLabel("i"),
                ),
                Action(
                    Icon.fromName("TextUnderline20Regular"),
                    self.tr("Underline"),
                    triggered=lambda: self.setLabel("u"),
                ),
                Action(
                    Icon.fromName("TextStrikethrough20Regular"),
                    self.tr("Strike"),
                    triggered=lambda: self.setLabel("strike"),
                ),
                Action(
                    Icon.fromName("EyeOff20Regular"),
                    self.tr("Spoiler"),
                    triggered=lambda: self.setLabel("spoiler"),
                ),
                Action(
                    Icon.fromName("Link20Regular"),
                    self.tr("Link"),
                    triggered=lambda: self.createLink(),
                ),
            ]
        )

        # 编辑框
        self.edit_input = PlainTextEdit(self)
        self.edit_input.textChanged.connect(self.updatePreview)
        self.edit_input.verticalScrollBar().valueChanged.connect(self.syncScroll)

        # 预览区域
        # 命令栏
        self.preview_command_bar = CommandBar(self)

        # 预览按钮
        self.preview_button = TransparentDropDownPushButton(
            Icon.fromName("Live20Regular"), self.tr("Preview")
        )

        self.preview_menu = RoundMenu(parent=self)

        self.preview_enabled = QWidget()
        self.preview_enabled_layout = QHBoxLayout(self.preview_enabled)

        self.preview_switch = SwitchButton()
        self.preview_switch.checkedChanged.connect(
            lambda checked: self.setPreviewEnabled(checked)
        )
        self.preview_switch.setChecked(True)
        self.preview_switch.setOffText("")
        self.preview_switch.setOnText("")

        self.preview_enabled_layout.addWidget(CaptionLabel(self.tr("Preview")))
        self.preview_enabled_layout.addStretch()
        self.preview_enabled_layout.addWidget(self.preview_switch)

        self.sync_scroll_enabled = QWidget()
        self.sync_scroll_enabled_layout = QHBoxLayout(self.sync_scroll_enabled)

        self.sync_scroll_switch = SwitchButton()
        self.sync_scroll_switch.checkedChanged.connect(
            lambda checked: self.setSyncScrollEnabled(checked)
        )
        self.sync_scroll_switch.setChecked(True)
        self.sync_scroll_switch.setOffText("")
        self.sync_scroll_switch.setOnText("")

        self.sync_scroll_enabled_layout.addWidget(CaptionLabel(self.tr("Sync Scroll")))
        self.sync_scroll_enabled_layout.addStretch()
        self.sync_scroll_enabled_layout.addWidget(self.sync_scroll_switch)

        self.preview_enabled.setFixedSize(160, 40)
        self.sync_scroll_enabled.setFixedSize(160, 40)

        self.preview_menu.addWidget(self.preview_enabled, selectable=False)
        self.preview_menu.addSeparator()
        self.preview_menu.addWidget(self.sync_scroll_enabled, selectable=False)

        self.preview_button.setMenu(self.preview_menu)

        self.preview_command_bar.addWidget(self.preview_button)

        # Webview
        self.webview = Webview(self)
        self.loadPreviewPage()

        # 布局
        self.splitter = QSplitter(Qt.Vertical, self)

        self.splitter.addWidget(self.edit_command_bar)
        self.splitter.addWidget(self.edit_input)
        self.splitter.addWidget(self.preview_command_bar)
        self.splitter.addWidget(self.webview)
        self.splitter.setSizes([1, 400, 1, 400])

        layout.addWidget(self.splitter, 1)

        self.view.setLayout(layout)

    def setAlign(self, align: str):
        """设置对齐方式"""
        cursor = self.edit_input.textCursor()
        # 获取选中的文本，如果没有选中则处理整个文档
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            cursor.movePosition(cursor.StartOfLine)
            start_line_pos = cursor.position()
            cursor.setPosition(end)
            cursor.movePosition(cursor.EndOfLine)
            end_line_pos = cursor.position()

            cursor.setPosition(start_line_pos)
            cursor.setPosition(end_line_pos, cursor.KeepAnchor)
            selected_text = cursor.selectedText()

            fill_type = "insert"
        else:
            cursor.select(cursor.Document)
            selected_text = cursor.selectedText()
            cursor.clearSelection()

            fill_type = "replace"

        # 按行分割文本
        lines = selected_text.split("\u2029")  # QTextEdit中使用U+2029作为行分隔符

        processed_lines = []
        for line in lines:
            # 移除行首的占位符和多余空格
            clean_line = line.lstrip()
            clean_line = " ".join(clean_line.split())  # 删除所有超过1个的空格

            # 提取标签和内容
            import re

            tag_match = re.match(
                r"^(\[[a-zA-Z0-9=]+\])(.*?)(\[/[a-zA-Z0-9]+\])?$", clean_line
            )

            if tag_match:
                # 有标签的情况
                opening_tag = tag_match.group(1)
                content = tag_match.group(2)
                closing_tag = (
                    tag_match.group(3)
                    if tag_match.group(3)
                    else f"[/{opening_tag[1:-1]}]"
                )

                # 移除内容中的标签，计算纯文本长度
                text_without_inner_tags = re.sub(r"\[/?[a-zA-Z0-9=]+\]", "", content)

                # 根据标签类型确定最大长度
                if opening_tag.startswith("[h1"):
                    max_length = 46
                elif opening_tag.startswith("[h2"):
                    max_length = 51
                elif opening_tag.startswith("[h3"):
                    max_length = 58
                else:
                    max_length = 70

                # 计算需要添加的全角空格数量
                text_length = len(text_without_inner_tags)
                if align == "left":
                    spaces_needed = 0
                elif align == "center":
                    spaces_needed = (max_length - text_length) // 2
                elif align == "right":
                    spaces_needed = max_length - text_length
                else:
                    spaces_needed = 0

                # 添加全角空格到标签内部
                fullwidth_spaces = "\u3000" * spaces_needed

                # 构建对齐后的行（空格放在标签内部）
                aligned_line = f"{opening_tag}{fullwidth_spaces}{content}{closing_tag}"

            else:
                # 没有标签的普通文本
                text_without_tags = re.sub(r"\[/?[a-zA-Z0-9=]+\]", "", clean_line)
                max_length = 70

                # 计算需要添加的全角空格数量
                text_length = len(text_without_tags)
                if align == "left":
                    spaces_needed = 0
                elif align == "center":
                    spaces_needed = (max_length - text_length) // 2
                elif align == "right":
                    spaces_needed = max_length - text_length
                else:
                    spaces_needed = 0

                # 添加全角空格
                fullwidth_spaces = "\u3000" * spaces_needed
                aligned_line = f"{fullwidth_spaces}{clean_line}"

            processed_lines.append(aligned_line)

        # 合并处理后的行
        result_text = "\u2029".join(processed_lines)

        # 替换原始文本
        if fill_type == "replace":
            self.edit_input.setPlainText(result_text)
        else:
            cursor.insertText(result_text)

    def setLabel(self, label: str):
        """设置标签"""
        text = self.edit_input.textCursor().selectedText()
        self.edit_input.insertPlainText(f"[{label}]{text}[/{label}]")

    def createLink(self):
        """创建链接"""
        text = self.edit_input.textCursor().selectedText()
        dialog = URLDialog(self.window())
        if dialog.exec():
            url = dialog.urlLineEdit.text()
            self.edit_input.insertPlainText(f"[url={url}]{text}[/url]")

    def loadPreviewPage(self):
        """加载HTML预览页面"""
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        html_path = os.path.join(base_dir, "src", "utils", "editor.html")
        html_url = QUrl.fromLocalFile(html_path)
        self.webview.open(html_url)

    def updatePreview(self):
        """更新预览内容"""
        if not self.preview_enabled:
            return

        text = self.edit_input.toPlainText()
        processed_text = text.replace("\n", "\\n")
        script = f'parseText("{processed_text}");'
        self.webview.run(script)

    def syncScroll(self, value):
        """同步滚动进度"""
        if not self.sync_scroll_enabled or not self.preview_enabled:
            return

        scroll_bar = self.edit_input.verticalScrollBar()
        max_scroll = scroll_bar.maximum()
        if max_scroll > 0:
            scroll_ratio = value / max_scroll
            self.webview.run(f"syncScroll({scroll_ratio});")

    def setPreviewEnabled(self, enabled):
        """设置预览功能"""
        if not hasattr(self, "webview"):
            return

        self.preview_enabled = enabled
        if enabled:
            self.webview.show()
            self.updatePreview()
            self.splitter.setSizes([1, 400, 1, 400])
        else:
            self.webview.hide()
            self.splitter.setSizes([1, 400, 1, 0])

    def setSyncScrollEnabled(self, enabled):
        """设置同步滚动"""
        if not hasattr(self, "webview"):
            return

        self.sync_scroll_enabled = enabled
