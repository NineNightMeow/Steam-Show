import os

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QFileDialog
from qfluentwidgets import (
    PrimaryPushButton,
    LineEdit,
    SpinBox,
    CompactSpinBox,
    IconWidget,
    Action,
    GroupHeaderCardWidget,
    SegmentedWidget,
    FluentIcon,
)
from src.views.interface import Interface, InfoTip, StateTip
from src.utils.translator import Translator
from src.utils.processor import VideoProcessor
from src.icons.icons import Icon


class FileCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Select Files"))

        INPUT_WIDTH = 300

        # 视频文件
        self.input_path = LineEdit()
        self.input_path.textChanged.connect(parent.validate)
        self.input_button = Action(
            FluentIcon.FOLDER, self.tr("Browse"), triggered=self.select_video
        )
        self.input_path.addAction(self.input_button, QLineEdit.TrailingPosition)

        # 输出目录
        self.output_path = LineEdit()
        self.output_path.textChanged.connect(parent.validate)
        self.output_button = Action(
            FluentIcon.FOLDER, self.tr("Browse"), triggered=self.select_output_dir
        )
        self.output_path.addAction(self.output_button, QLineEdit.TrailingPosition)

        self.input_path.setFixedWidth(INPUT_WIDTH)
        self.output_path.setFixedWidth(INPUT_WIDTH)

        self.addGroup(FluentIcon.MOVIE, self.tr("Video path"), "", self.input_path)
        self.addGroup(
            FluentIcon.IMAGE_EXPORT, self.tr("Output path"), "", self.output_path
        )

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select file"),
            "",
            self.tr("Video files (*.mp4 *.avi *.mkv *.mov)"),
        )
        if file_path:
            self.input_path.setText(file_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, self.tr("Select folder"))
        if dir_path:
            self.output_path.setText(dir_path)


class ArgsCard(GroupHeaderCardWidget):
    def __init__(self, type: str = "workshop", parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Arguments"))

        if type == "workshop":
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
            self.row_icon = IconWidget(
                Icon.fromName("ArrowBidirectionalUpDown20Regular")
            )
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
            self.max_size_input.setRange(1, 1000)
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

            self.addGroup(
                FluentIcon.VIDEO,
                self.tr("Duration"),
                "Units: s",
                self.duration_input,
            )
            self.addGroup(
                FluentIcon.CLIPPING_TOOL,
                self.tr("Size"),
                "Units: px",
                self.size_inputs,
            )
            self.addGroup(
                FluentIcon.CUT,
                self.tr("Split parts"),
                "",
                self.split_inputs,
            )
            self.addGroup(
                FluentIcon.ZIP_FOLDER,
                self.tr("Max size"),
                "Units: MB",
                self.max_size_input,
            )
            self.addGroup(FluentIcon.CODE, self.tr("Hex"), "", self.hex_input)
            self.addGroup(FluentIcon.SPEED_HIGH, self.tr("FPS"), "", self.fps_input)


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
            onClick=lambda: self.switchType("workshop"),
            icon=FluentIcon.TILES,
        )
        self.selector.insertItem(
            index=1,
            routeKey="artwork",
            text=self.tr("Artwork"),
            onClick=lambda: self.switchType("artwork"),
            icon=FluentIcon.BRUSH,
        )

        self.file_card = FileCard(self)
        self.args_card = ArgsCard(self)

        self.start_button = PrimaryPushButton(self.tr("Start Conversion"))
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_conversion)

        self.layout.addWidget(self.selector)
        self.layout.addWidget(self.file_card)
        self.layout.addWidget(self.args_card)
        self.layout.addStretch()
        self.layout.addWidget(self.start_button)

        self.view.setLayout(self.layout)

        self.selector.setCurrentItem("workshop")
        self.switchType("workshop")
        self.is_converting = False

    def switchType(self, type):
        if hasattr(self, "args_card") and self.args_card:
            self.layout.removeWidget(self.args_card)
            self.args_card.deleteLater()
            self.args_card = None

        self.args_card = ArgsCard(type, self)
        self.layout.insertWidget(2, self.args_card)

    def validate(self):
        """验证输入"""
        if self.is_converting:
            return

        try:
            # 检查路径是否为空
            if (
                not self.file_card.input_path.text()
                or not self.file_card.output_path.text()
            ):
                self.start_button.setEnabled(False)
                return

            if not os.path.exists(self.file_card.input_path.text()):
                self.start_button.setEnabled(False)
                InfoTip(
                    type="error",
                    title=self.tr("File not found"),
                    massage=self.tr("The selected video file does not exist"),
                    parent=self.window,
                )
                return

            # 检查文件类型
            video_extensions = [".mp4", ".avi", ".mkv", ".mov"]
            file_extension = os.path.splitext(self.file_card.input_path.text())[
                1
            ].lower()
            if file_extension not in video_extensions:
                self.start_button.setEnabled(False)
                InfoTip(
                    type="error",
                    title=self.tr("Invalid file type"),
                    massage=self.tr(
                        "Please select a valid video file (MP4, AVI, MKV, MOV)"
                    ),
                    parent=self.window,
                )
                return

            self.start_button.setEnabled(True)

        except Exception as e:
            print(f"Validation error: {e}")
            self.start_button.setEnabled(False)

    def start_conversion(self):
        """开始转换"""
        self.is_converting = True
        self.start_button.setEnabled(False)

        if hasattr(self.window, "task_stack"):
            self.window.task_stack.append("convert_task")

        self.StateTip = StateTip("Converting", "Wait for start", self.window)

        try:
            input_path = self.file_card.input_path.text()
            output_path = self.file_card.output_path.text()
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

        self.processor = VideoProcessor(
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
