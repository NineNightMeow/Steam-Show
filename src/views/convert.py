import os
import requests

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QFileDialog
from qfluentwidgets import (
    ToolButton,
    PrimaryPushButton,
    LineEdit,
    SpinBox,
    CompactSpinBox,
    IconWidget,
    Action,
    ToolTipFilter,
    ToolTipPosition,
    CardGroupWidget,
    GroupHeaderCardWidget,
    SegmentedWidget,
    FluentIcon,
)
from src.views.interface import Interface, InfoTip, StateTip
from src.utils.translator import Translator
from src.utils.processor import Processor
from src.icons.icons import Icon
from src.app import App
from src.user import User


class FilesCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Select Files"))
        self.parent = parent

        INPUT_WIDTH = 300

        input_type = "*.png *.jpg *.jpeg *.gif *.mp4 *.avi *.mkv *.mov"
        background_type = "*.png *.jpg *.jpeg"
        foreground_type = "*.png *.jpg *.jpeg *.gif *.mp4 *.avi *.mkv *.mov"

        # 视频文件
        self.input_path = LineEdit()
        self.input_path.setFixedWidth(INPUT_WIDTH)
        self.input_button = Action(
            FluentIcon.FOLDER,
            self.tr("Browse"),
            triggered=lambda: self.select_file(self.input_path, input_type),
        )
        self.input_path.addAction(self.input_button, QLineEdit.TrailingPosition)

        # 前景图片/视频
        self.foreground_path = LineEdit()
        self.foreground_path.setFixedWidth(INPUT_WIDTH)
        self.foreground_button = Action(
            FluentIcon.FOLDER,
            self.tr("Browse"),
            triggered=lambda: self.select_file(self.foreground_path, foreground_type),
        )
        self.foreground_path.addAction(
            self.foreground_button, QLineEdit.TrailingPosition
        )

        # 背景图片
        self.background_path_widget = QWidget(self)
        self.background_path_widget.setFixedWidth(INPUT_WIDTH)
        self.background_path_layout = QHBoxLayout(self.background_path_widget)
        self.background_path_layout.setContentsMargins(0, 0, 0, 0)
        self.background_path_layout.setSpacing(10)

        self.steam_button = ToolButton(Icon.fromName("ArrowDownload20Regular"))
        self.steam_button.setToolTip(self.tr("Get Steam background"))
        self.steam_button.installEventFilter(
            ToolTipFilter(
                self.steam_button,
                showDelay=300,
                position=ToolTipPosition.TOP,
            )
        )
        self.steam_button.clicked.connect(self.get_steam_bg)

        self.background_path = LineEdit()
        self.background_button = Action(
            FluentIcon.FOLDER,
            self.tr("Browse"),
            triggered=lambda: self.select_file(self.background_path, background_type),
        )
        self.background_path.addAction(
            self.background_button, QLineEdit.TrailingPosition
        )
        self.background_path_layout.addWidget(self.steam_button)
        self.background_path_layout.addWidget(self.background_path)

        # 输出目录
        self.output_path = LineEdit()
        self.output_path.setFixedWidth(INPUT_WIDTH)
        self.output_button = Action(
            FluentIcon.FOLDER, self.tr("Browse"), triggered=self.select_output_dir
        )
        self.output_path.addAction(self.output_button, QLineEdit.TrailingPosition)

        self.input_group = CardGroupWidget(
            Icon.fromName("FilmstripImage20Regular"),
            self.tr("Input path"),
            self.tr("Video or image"),
        )
        self.foreground_group = CardGroupWidget(
            Icon.fromName("FilmstripImage20Regular"),
            self.tr("Foreground path"),
            self.tr("Video or image"),
        )
        self.background_group = CardGroupWidget(
            Icon.fromName("Image20Regular"),
            self.tr("Background path"),
            self.tr("Static image"),
        )
        self.output_group = CardGroupWidget(
            Icon.fromName("SaveImage20Regular"),
            self.tr("Output path"),
            "",
        )

        for line_edit in [
            self.input_path,
            self.foreground_path,
            self.background_path,
            self.output_path,
        ]:
            line_edit.textChanged.connect(parent.verify_input)

        self.input_group.addWidget(self.input_path)
        self.foreground_group.addWidget(self.foreground_path)
        self.background_group.addWidget(self.background_path_widget)
        self.output_group.addWidget(self.output_path)

        self.vBoxLayout.addWidget(self.input_group)
        self.vBoxLayout.addWidget(self.foreground_group)
        self.vBoxLayout.addWidget(self.background_group)
        self.vBoxLayout.addWidget(self.output_group)

    def select_file(self, target, file_type):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select file"), "", file_type
        )
        if file_path:
            target.setText(file_path)

    def select_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, self.tr("Select folder"))
        if dir_path:
            self.output_path.setText(dir_path)

    def get_steam_bg(self):
        InfoTip(
            message=self.tr("Getting Steam background..."), parent=self.parent.window
        )
        self.user = User(self.parent)
        self.user.getBg()
        self.user.backgroundUpdated.connect(lambda url: self.insert_bg(url))

    def insert_bg(self, bg_url):
        if bg_url:
            temp_dir = App.getPath("temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            file_name = bg_url.split("/")[-1]
            file_path = os.path.join(temp_dir, file_name)
            if not os.path.exists(file_path):
                response = requests.get(bg_url, stream=True)
                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
            self.background_path.setText(file_path)

            InfoTip(
                type="success",
                message=self.tr("Successfully downloaded Steam background"),
                parent=self.parent.window,
            )

    def updateContents(self, type: str = "workshop"):
        if type == "workshop":
            self.input_group.show()
            self.foreground_group.hide()
            self.background_group.hide()
        elif type == "artwork":
            self.input_group.hide()
            self.foreground_group.show()
            self.background_group.show()

        if User.get("status"):
            self.steam_button.show()
        else:
            self.steam_button.hide()


class ArgsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Arguments"))

        INPUT_WIDTH = 200

        self.duration_input = SpinBox(self)
        self.duration_input.setRange(1, 10000)
        self.duration_input.setValue(10)

        SIZE_INPUT_WIDTH = 95

        self.size_inputs = QWidget(self)
        self.size_layout = QHBoxLayout(self.size_inputs)
        self.size_layout.setContentsMargins(0, 0, 0, 0)
        self.size_layout.setSpacing(10)

        self.size_width = QWidget(self)
        self.size_width_layout = QHBoxLayout(self.size_width)
        self.size_width_layout.setContentsMargins(0, 0, 0, 0)
        self.size_width_layout.setSpacing(5)
        self.width_icon = IconWidget(Icon.fromName("AutoFitWidth20Regular"))
        self.width_icon.setFixedSize(16, 16)
        self.width_spin = CompactSpinBox(self)
        self.width_spin.setRange(1, 9999)
        self.width_spin.setValue(630)
        self.size_width_layout.addWidget(self.width_icon)
        self.size_width_layout.addWidget(self.width_spin)

        self.size_height = QWidget(self)
        self.size_height_layout = QHBoxLayout(self.size_height)
        self.size_height_layout.setContentsMargins(0, 0, 0, 0)
        self.size_height_layout.setSpacing(5)
        self.height_icon = IconWidget(Icon.fromName("AutoFitHeight20Regular"))
        self.height_icon.setFixedSize(16, 16)
        self.height_spin = CompactSpinBox(self)
        self.height_spin.setRange(1, 9999)
        self.height_spin.setValue(360)
        self.size_height_layout.addWidget(self.height_icon)
        self.size_height_layout.addWidget(self.height_spin)

        self.size_width.setFixedWidth(SIZE_INPUT_WIDTH)
        self.size_height.setFixedWidth(SIZE_INPUT_WIDTH)
        self.size_layout.addWidget(self.size_width)
        self.size_layout.addWidget(self.size_height)

        SPLIT_INPUT_WIDTH = 95

        self.split_inputs = QWidget(self)
        self.split_layout = QHBoxLayout(self.split_inputs)
        self.split_layout.setContentsMargins(0, 0, 0, 0)
        self.split_layout.setSpacing(10)

        self.split_row = QWidget(self)
        self.split_row_layout = QHBoxLayout(self.split_row)
        self.split_row_layout.setContentsMargins(0, 0, 0, 0)
        self.split_row_layout.setSpacing(5)
        self.row_icon = IconWidget(Icon.fromName("ArrowBidirectionalUpDown20Regular"))
        self.row_icon.setFixedSize(16, 16)
        self.row_spin = CompactSpinBox(self)
        self.row_spin.setRange(1, 3)
        self.row_spin.setValue(1)
        self.split_row_layout.addWidget(self.row_icon)
        self.split_row_layout.addWidget(self.row_spin)

        self.split_col = QWidget(self)
        self.split_col_layout = QHBoxLayout(self.split_col)
        self.split_col_layout.setContentsMargins(0, 0, 0, 0)
        self.split_col_layout.setSpacing(5)
        self.col_icon = IconWidget(
            Icon.fromName("ArrowBidirectionalLeftRight20Regular")
        )
        self.col_icon.setFixedSize(16, 16)
        self.col_spin = CompactSpinBox(self)
        self.col_spin.setRange(1, 5)
        self.col_spin.setValue(5)
        self.split_col_layout.addWidget(self.col_icon)
        self.split_col_layout.addWidget(self.col_spin)

        self.split_row.setFixedWidth(SPLIT_INPUT_WIDTH)
        self.split_col.setFixedWidth(SPLIT_INPUT_WIDTH)
        self.split_layout.addWidget(self.split_row)
        self.split_layout.addWidget(self.split_col)

        self.max_size_input = SpinBox(self)
        self.max_size_input.setRange(1, 5)
        self.max_size_input.setValue(5)

        self.hex_input = SpinBox(self)
        self.hex_input.setRange(0, 255)
        self.hex_input.setValue(21)

        self.fps_input = SpinBox(self)
        self.fps_input.setRange(1, 60)
        self.fps_input.setValue(15)

        self.duration_input.setFixedWidth(INPUT_WIDTH)
        self.size_inputs.setFixedWidth(INPUT_WIDTH)
        self.split_inputs.setFixedWidth(INPUT_WIDTH)
        self.max_size_input.setFixedWidth(INPUT_WIDTH)
        self.hex_input.setFixedWidth(INPUT_WIDTH)
        self.fps_input.setFixedWidth(INPUT_WIDTH)

        self.duration_group = CardGroupWidget(
            Icon.fromName("Clock20Regular"),
            self.tr("Duration"),
            self.tr("Units: s"),
        )
        self.size_group = CardGroupWidget(
            Icon.fromName("Resize20Regular"),
            self.tr("Size"),
            self.tr("Units: px"),
        )
        self.split_group = CardGroupWidget(
            Icon.fromName("ImageSplit20Regular"),
            self.tr("Split parts"),
            "",
        )
        self.max_size_group = CardGroupWidget(
            Icon.fromName("FolderZip20Regular"),
            self.tr("Max size"),
            self.tr("Units: MB"),
        )
        self.hex_group = CardGroupWidget(
            Icon.fromName("Hexagon20Regular"),
            self.tr("Hex"),
            "",
        )
        self.fps_group = CardGroupWidget(
            Icon.fromName("TopSpeed20Regular"),
            self.tr("FPS"),
            "",
        )

        self.duration_group.addWidget(self.duration_input)
        self.size_group.addWidget(self.size_inputs)
        self.split_group.addWidget(self.split_inputs)
        self.max_size_group.addWidget(self.max_size_input)
        self.hex_group.addWidget(self.hex_input)
        self.fps_group.addWidget(self.fps_input)

        self.vBoxLayout.addWidget(self.duration_group)
        self.vBoxLayout.addWidget(self.size_group)
        self.vBoxLayout.addWidget(self.split_group)
        self.vBoxLayout.addWidget(self.max_size_group)
        self.vBoxLayout.addWidget(self.hex_group)
        self.vBoxLayout.addWidget(self.fps_group)

    def updateContents(
        self,
        type: str = "workshop",
        file_type: str = "image",
    ):
        if type == "workshop":
            self.split_group.show()
        elif type == "artwork":
            self.split_group.hide()

        if file_type == "image":
            self.duration_group.hide()
            self.fps_group.hide()
        elif file_type == "video":
            self.duration_group.show()
            self.fps_group.show()


class Convert(Interface):
    def __init__(self, window):
        super().__init__(title=Translator().convert_title)
        self.setObjectName("convert")

        self.window = window

        self.layout = QVBoxLayout(self)

        self.selector = SegmentedWidget()

        self.selector.insertItem(
            index=0,
            routeKey="workshop",
            text=self.tr("Workshop"),
            onClick=lambda: self.updateCards("workshop"),
            icon=FluentIcon.TILES,
        )
        self.selector.insertItem(
            index=1,
            routeKey="artwork",
            text=self.tr("Artwork"),
            onClick=lambda: self.updateCards("artwork"),
            icon=FluentIcon.BRUSH,
        )

        self.files_card = FilesCard(parent=self)
        self.args_card = ArgsCard(parent=self)

        self.start_button = PrimaryPushButton(self.tr("Start Conversion"))
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_conversion)

        self.layout.addWidget(self.selector)
        self.layout.addWidget(self.files_card)
        self.layout.addWidget(self.args_card)
        self.layout.addStretch()
        self.layout.addWidget(self.start_button)

        self.view.setLayout(self.layout)

        self.selector.setCurrentItem("workshop")
        self.updateCards("workshop")
        self.is_converting = False

    def updateCards(self, type):
        self.start_button.setEnabled(False)

        if hasattr(self, "files_card"):
            self.files_card.updateContents(type)
        if hasattr(self, "args_card"):
            self.args_card.updateContents(type)

        self.verify_input()

    def verify_input(self):
        """验证输入框"""
        type = self.selector.currentRouteKey()
        file_type = "image"
        accepted = True

        input_path = self.files_card.input_path.text()
        foreground_path = self.files_card.foreground_path.text()
        background_path = self.files_card.background_path.text()
        output_path = self.files_card.output_path.text()

        if type == "workshop":
            if not input_path:
                accepted = False
            if not os.path.exists(input_path):
                accepted = False
            if input_path.endswith(
                (".png", ".jpg", ".jpeg", ".gif", ".mp4", ".avi", ".mkv", ".mov")
            ):
                if input_path.endswith((".mp4", ".avi", ".mkv", ".mov")):
                    file_type = "video"
            else:
                accepted = False
        elif type == "artwork":
            if not foreground_path or not background_path:
                accepted = False
            if not os.path.exists(foreground_path):
                accepted = False
            if not os.path.exists(background_path):
                accepted = False
            if foreground_path.endswith(
                (".png", ".jpg", ".jpeg", ".gif", ".mp4", ".avi", ".mkv", ".mov")
            ):
                if foreground_path.endswith((".mp4", ".avi", ".mkv", ".mov")):
                    file_type = "video"
            else:
                accepted = False

        self.args_card.updateContents(type=type, file_type=file_type)

        if output_path:
            if not os.path.exists(output_path):
                accepted = False
        else:
            accepted = False

        if accepted:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def start_conversion(self):
        """开始转换"""
        type = self.selector.currentRouteKey()

        self.is_converting = True
        self.start_button.setEnabled(False)

        if hasattr(self.window, "task_stack"):
            self.window.task_stack.append("convert_task")

        self.StateTip = StateTip("Converting", "Wait for start", self.window)

        try:
            input_path = self.files_card.input_path.text()
            foreground_path = self.files_card.foreground_path.text()
            background_path = self.files_card.background_path.text()
            output_path = self.files_card.output_path.text()
            duration = int(self.args_card.duration_input.value())
            width = int(self.args_card.size_width.value())
            height = int(self.args_card.size_height.value())
            rows = int(self.args_card.split_row.value())
            cols = int(self.args_card.split_col.value())
            max_size = float(self.args_card.max_size_input.value())
            hex = (
                int(self.args_card.hex_input.text().strip(), 16)
                if self.args_card.hex_input.text().strip()
                else 21
            )
            fps = int(self.args_card.fps_input.value())
        except ValueError:
            return

        if type == "workshop":
            self.processor = Processor(
                type,
                input_path,
                output_path,
                duration,
                width,
                height,
                rows,
                cols,
                max_size,
                hex,
                fps,
            )
        elif type == "artwork":
            self.processor = Processor(
                type,
                foreground_path,
                background_path,
                output_path,
                duration,
                width,
                height,
                rows,
                cols,
                max_size,
                hex,
                fps,
            )

        self.processor.progress.connect(self.update_progress)
        self.processor.completed.connect(self.conversion_completed)
        self.processor.error.connect(self.conversion_error)

        self.processor.start()

    def update_progress(self, text):
        """更新进度显示"""
        if self.StateTip:
            self.StateTip.update(None, text)

    def conversion_completed(self, output_path):
        """转换完成后的处理"""
        self.is_converting = False
        self.start_button.setEnabled(True)
        if hasattr(self.window, "task_stack"):
            if "convert_task" in self.window.task_stack:
                self.window.task_stack.remove("convert_task")

        if self.StateTip:
            self.StateTip.update(
                self.tr("Conversion completed"),
                f"{self.tr('Output path')}: {output_path}",
            )
            self.StateTip.close()

        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    def conversion_error(self, error_msg):
        """转换错误处理"""
        print(error_msg)

        self.is_converting = False
        self.start_button.setEnabled(True)
        if self.StateTip:
            self.StateTip.hide()
        if hasattr(self.window, "task_stack"):
            if "convert_task" in self.window.task_stack:
                self.window.task_stack.remove("convert_task")

        InfoTip(
            title=self.tr("Conversion failed"),
            massage=error_msg,
            parent=self.window,
        )
