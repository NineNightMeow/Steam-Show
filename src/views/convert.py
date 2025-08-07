from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import (
    SegmentedWidget,
    PrimaryPushButton,
    LineEdit,
    SpinBox,
    Action,
    GroupHeaderCardWidget,
    StateToolTip,
    InfoBar,
    InfoBarPosition,
    FluentIcon,
)
from src.views.interface import Interface
from src.utils.translator import Translator
from src.utils.processor import VideoProcessor


class Convert(Interface):
    def __init__(self):
        super().__init__(title=Translator().convert_title)
        self.setObjectName("convert")

        layout = QVBoxLayout(self)

        self.selector = SegmentedWidget()

        self.selector.insertItem(
            index=0,
            routeKey="workshop",
            text=self.tr("Workshop"),
            onClick=None,
            icon=FluentIcon.TILES,
        )
        self.selector.insertItem(
            index=1,
            routeKey="artwork",
            text=self.tr("Artwork"),
            onClick=None,
            icon=FluentIcon.BRUSH,
        )

        self.selector.setCurrentItem("workshop")

        self.file_select_card = self.FileSelectCard(self)
        self.args_card = self.ArgsCard(self)

        self.start_button = PrimaryPushButton(self.tr("Start Conversion"))
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_conversion)

        layout.addWidget(self.selector)
        layout.addWidget(self.file_select_card)
        layout.addWidget(self.args_card)
        layout.addStretch()
        layout.addWidget(self.start_button)

        self.view.setLayout(layout)

        self.is_converting = False

        self.stateTooltip = StateToolTip("", "", self.window())
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.hide()

    class FileSelectCard(GroupHeaderCardWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setTitle(self.tr("Select Files"))

            INPUT_WIDTH = 300

            # 视频文件
            self.input_path = LineEdit()
            self.input_path.textChanged.connect(parent.validate_inputs)
            self.input_button = Action(
                FluentIcon.FOLDER, self.tr("Browse"), triggered=self.select_video
            )
            self.input_path.addAction(self.input_button, QLineEdit.TrailingPosition)

            # 输出目录
            self.output_path = LineEdit()
            self.output_path.textChanged.connect(parent.validate_inputs)
            self.output_button = Action(
                FluentIcon.FOLDER, self.tr("Browse"), triggered=self.select_output_dir
            )
            self.output_path.addAction(self.output_button, QLineEdit.TrailingPosition)

            self.input_path.setFixedWidth(INPUT_WIDTH)
            self.output_path.setFixedWidth(INPUT_WIDTH)

            self.addGroup(FluentIcon.VIDEO, self.tr("Video path"), "", self.input_path)
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
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setTitle(self.tr("Arguments"))

            INPUT_WIDTH = 150

            self.filename_input = LineEdit(self)
            self.filename_input.setText("output.gif")
            self.filename_input.textChanged.connect(parent.validate_inputs)

            self.prefix_input = LineEdit(self)
            self.prefix_input.setText("part")
            self.prefix_input.textChanged.connect(parent.validate_inputs)

            self.width_input = SpinBox(self)
            self.width_input.setRange(100, 10000)
            self.width_input.setValue(630)
            self.width_input.valueChanged.connect(parent.validate_inputs)

            self.split_input = SpinBox(self)
            self.split_input.setRange(1, 50)
            self.split_input.setValue(5)
            self.split_input.valueChanged.connect(parent.validate_inputs)

            self.max_size_input = SpinBox(self)
            self.max_size_input.setRange(1, 1000)
            self.max_size_input.setValue(5)
            self.max_size_input.valueChanged.connect(parent.validate_inputs)

            self.hex_input = SpinBox(self)
            self.hex_input.setRange(0, 255)
            self.hex_input.setValue(21)
            self.hex_input.valueChanged.connect(parent.validate_inputs)

            self.fps_input = SpinBox(self)
            self.fps_input.setRange(1, 60)
            self.fps_input.setValue(15)
            self.fps_input.valueChanged.connect(parent.validate_inputs)

            self.filename_input.setFixedWidth(INPUT_WIDTH)
            self.prefix_input.setFixedWidth(INPUT_WIDTH)
            self.width_input.setFixedWidth(INPUT_WIDTH)
            self.split_input.setFixedWidth(INPUT_WIDTH)
            self.max_size_input.setFixedWidth(INPUT_WIDTH)
            self.hex_input.setFixedWidth(INPUT_WIDTH)
            self.fps_input.setFixedWidth(INPUT_WIDTH)

            self.addGroup(
                FluentIcon.PHOTO, self.tr("Onefile name"), "", self.filename_input
            )
            self.addGroup(
                FluentIcon.LABEL, self.tr("Part prefix"), "", self.prefix_input
            )
            self.addGroup(FluentIcon.UNIT, self.tr("Width"), "", self.width_input)
            self.addGroup(FluentIcon.CUT, self.tr("Split parts"), "", self.split_input)
            self.addGroup(
                FluentIcon.CLIPPING_TOOL,
                self.tr("Max size (MB)"),
                "",
                self.max_size_input,
            )
            self.addGroup(FluentIcon.CODE, self.tr("Hex"), "", self.hex_input)
            self.addGroup(FluentIcon.SPEED_HIGH, self.tr("FPS"), "", self.fps_input)

    def validate_inputs(self):
        """验证输入"""
        if self.is_converting:
            return

        try:
            if (
                self.file_select_card.input_path.text()
                and self.file_select_card.output_path.text()
                and self.args_card.filename_input.text()
                and self.args_card.prefix_input.text()
            ):
                self.start_button.setEnabled(True)
            else:
                self.start_button.setEnabled(False)

        except ValueError:
            self.start_button.setEnabled(False)

    def start_conversion(self):
        self.is_converting = True
        self.start_button.setEnabled(False)
        main_window = self.window()
        if hasattr(main_window, "task_stack"):
            main_window.task_stack.append("convert_task")

        self.stateTooltip.setTitle(self.tr("Converting"))
        self.stateTooltip.setContent(self.tr("Wait for start"))
        self.stateTooltip.setState(False)
        self.stateTooltip.show()

        try:
            input_path = self.file_select_card.input_path.text()
            output_path = self.file_select_card.output_path.text()
            filename = self.args_card.filename_input.text()
            prefix = self.args_card.prefix_input.text()
            target_width = int(self.args_card.width_input.value())
            split_parts = int(self.args_card.split_input.value())
            max_size_mb = float(self.args_card.max_size_input.value())
            hex_value = (
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
            target_width,
            split_parts,
            max_size_mb,
            prefix,
            hex_value,
            fps,
            filename,
        )

        self.processor.progress.connect(self.update_progress)
        self.processor.completed.connect(self.conversion_completed)
        self.processor.error.connect(self.conversion_error)

        self.processor.start()

    def update_progress(self, text):
        """更新进度显示"""
        self.stateTooltip.setContent(text)

    def conversion_completed(self, output_path):
        """转换完成后的处理"""
        self.is_converting = False
        self.start_button.setEnabled(True)
        main_window = self.window()
        if hasattr(main_window, "task_stack"):
            if "convert_task" in main_window.task_stack:
                main_window.task_stack.remove("convert_task")

        self.stateTooltip.setTitle(self.tr("Conversion completed"))
        self.stateTooltip.setContent(f"{self.tr('Output path')}: {output_path}")
        self.stateTooltip.setState(True)

        QTimer.singleShot(2000, self.stateTooltip.hide)

    def conversion_error(self, error_msg):
        """转换错误处理"""
        self.is_converting = False
        self.start_button.setEnabled(True)
        self.stateTooltip.hide()
        main_window = self.window()
        if hasattr(main_window, "task_stack"):
            if "convert_task" in main_window.task_stack:
                main_window.task_stack.remove("convert_task")

        InfoBar.warning(
            title=self.tr("Conversion failed"),
            content=error_msg,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )
