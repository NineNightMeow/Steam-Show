from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from video2gif.processor import VideoProcessor


# 作案工具
class Video2GifApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steam 展框制作工具")

        # 设置窗口大小
        self.setFixedSize(600, 800)

        # 移动到屏幕中心
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        center_point = screen.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())

        # 跟随系统主题
        self.setAttribute(Qt.WA_StyleSheet)

        # 主题样式
        self.base_style = """
            QLabel {
                font-size: 14px;
            }
            
            QLabel[class="title"] {
                font-size: 18px;
                font-weight: bold;
            }
            
            QPushButton {
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
            }

            QPushButton[class="start"] {
                padding: 15px;
            }
            
            QLineEdit {
                padding: 8px;
                border-radius: 4px;
            }
        """

        # 浅色主题
        self.light_style = (
            self.base_style
            + """
            QWidget {
                color: #333333;
                background-color: #f5f5f5;
            }
            
            QLabel[class="title"] {
                color: #364c63;
            }
            
            QPushButton {
                color: white;
                background-color: #364c63;
            }
            
            QPushButton:hover {
                background-color: #243342;
            }

            QPushButton:disabled {
                color: rgba(255, 255, 255, 0.5);
                background-color: rgba(54, 76, 99, 0.5);
            }
            
            QLineEdit {
                border: 1px solid #bdc3c7;
                background-color: white;
            }

            QFrame[class="separator"] {
                border-top: 1px solid #bdc3c7;
            }
        """
        )

        # 深色主题
        self.dark_style = (
            self.base_style
            + """
            QWidget {
                color: #ffffff;
                background-color: #2d2d2d;
            }
            
            QPushButton {
                background-color: #3d3d3d;
            }

            QPushButton:hover {
                background-color: #4d4d4d;
            }

            QPushButton:disabled {
                color: rgba(255, 255, 255, 0.5);
                background-color: rgba(61, 61, 61, 0.5);
            }
            
            QLineEdit {
                border: 1px solid #555555;
                background-color: #3d3d3d;
                color: white;
            }

            QFrame[class="separator"] {
                border-top: 1px solid #555555;
            }
        """
        )

        # 监听系统主题变化
        app = QApplication.instance()
        app.paletteChanged.connect(self.update_theme)

        # 初始化主题
        self.update_theme()

        layout = QVBoxLayout(self)

        # 文件选择
        file_select_layout = QVBoxLayout()

        file_select_title = QLabel("选择文件")
        file_select_title.setProperty("class", "title")

        input_layout = QVBoxLayout()
        input_path_layout = QHBoxLayout()
        output_layout = QVBoxLayout()
        output_path_layout = QHBoxLayout()

        # 视频文件选择
        self.input_label = QLabel("视频文件")
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("视频文件路径")
        self.input_button = QPushButton("浏览")
        self.input_button.clicked.connect(self.load_video)

        input_path_layout.addWidget(self.input_path)
        input_path_layout.addWidget(self.input_button)

        input_layout.addWidget(self.input_label)
        input_layout.addLayout(input_path_layout)

        # 输出目录选择
        self.output_label = QLabel("输出目录")
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("输出目录路径")
        self.output_button = QPushButton("浏览")
        self.output_button.clicked.connect(self.load_output_dir)

        output_path_layout.addWidget(self.output_path)
        output_path_layout.addWidget(self.output_button)

        output_layout.addWidget(self.output_label)
        output_layout.addLayout(output_path_layout)

        file_select_layout.addWidget(file_select_title)
        file_select_layout.addLayout(input_layout)
        file_select_layout.addLayout(output_layout)

        # 参数设置
        args_layout = QVBoxLayout()

        args_title = QLabel("设置参数")
        args_title.setProperty("class", "title")

        target_width_layout = QHBoxLayout()
        split_parts_layout = QHBoxLayout()
        max_size_mb_layout = QHBoxLayout()
        hex_value_layout = QHBoxLayout()
        fps_layout = QHBoxLayout()
        filename_prefix_layout = QHBoxLayout()
        full_gif_name_layout = QHBoxLayout()

        # input 宽度
        input_width = 200

        self.width_label = QLabel("目标宽度")
        self.width_input = QLineEdit("630")
        self.width_input.setPlaceholderText("单位：px")

        self.split_label = QLabel("分割份数")
        self.split_input = QLineEdit("5")
        self.split_input.setPlaceholderText("5")

        self.max_size_label = QLabel("单个文件最大大小")
        self.max_size_input = QLineEdit("5")
        self.max_size_input.setPlaceholderText("单位：MB")

        self.hex_label = QLabel("末位 HEX 值")
        self.hex_input = QLineEdit("21")
        self.hex_input.setPlaceholderText("0~255")

        self.fps_label = QLabel("帧率")
        self.fps_input = QLineEdit("15")
        self.fps_input.setPlaceholderText("15")

        self.full_gif_name_label = QLabel("单文件名称")
        self.full_gif_name_input = QLineEdit("output.gif")
        self.full_gif_name_input.setPlaceholderText("output.gif")

        self.filename_label = QLabel("分文件前缀")
        self.filename_input = QLineEdit("split_gif")
        self.filename_input.setPlaceholderText("split_gif")

        target_width_layout.addWidget(self.width_label)
        target_width_layout.addWidget(self.width_input)

        split_parts_layout.addWidget(self.split_label)
        split_parts_layout.addWidget(self.split_input)

        max_size_mb_layout.addWidget(self.max_size_label)
        max_size_mb_layout.addWidget(self.max_size_input)

        hex_value_layout.addWidget(self.hex_label)
        hex_value_layout.addWidget(self.hex_input)

        fps_layout.addWidget(self.fps_label)
        fps_layout.addWidget(self.fps_input)

        full_gif_name_layout.addWidget(self.full_gif_name_label)
        full_gif_name_layout.addWidget(self.full_gif_name_input)

        filename_prefix_layout.addWidget(self.filename_label)
        filename_prefix_layout.addWidget(self.filename_input)

        self.width_input.setFixedWidth(input_width)
        self.split_input.setFixedWidth(input_width)
        self.max_size_input.setFixedWidth(input_width)
        self.hex_input.setFixedWidth(input_width)
        self.fps_input.setFixedWidth(input_width)
        self.filename_input.setFixedWidth(input_width)
        self.full_gif_name_input.setFixedWidth(input_width)

        self.input_path.textChanged.connect(self.validate_inputs)
        self.output_path.textChanged.connect(self.validate_inputs)
        self.width_input.textChanged.connect(self.validate_inputs)
        self.split_input.textChanged.connect(self.validate_inputs)
        self.max_size_input.textChanged.connect(self.validate_inputs)
        self.filename_input.textChanged.connect(self.validate_inputs)
        self.hex_input.textChanged.connect(self.validate_inputs)
        self.fps_input.textChanged.connect(self.validate_inputs)

        args_layout.addWidget(args_title)
        args_layout.addLayout(target_width_layout)
        args_layout.addLayout(split_parts_layout)
        args_layout.addLayout(max_size_mb_layout)
        args_layout.addLayout(hex_value_layout)
        args_layout.addLayout(fps_layout)
        args_layout.addLayout(full_gif_name_layout)
        args_layout.addLayout(filename_prefix_layout)

        # 开始转换
        self.start_button = QPushButton("开始转换")
        self.start_button.clicked.connect(self.start_conversion)
        self.start_button.setProperty("class", "start")
        self.start_button.setEnabled(False)

        # 常用代码
        common_code_layout = QVBoxLayout()

        common_code_title = QLabel("常用代码")
        common_code_title.setProperty("class", "title")

        # label 宽度
        label_width = 100

        # 无名代码
        noname_layout = QHBoxLayout()
        self.noname_label = QLabel("无名代码")
        self.noname_text = QLineEdit(
            "v_trim=_=>{return _},$J('#title').val(' '+Array.from(Array(126),_=>'').join(''));"
        )
        self.noname_text.setReadOnly(True)
        self.noname_copy = QPushButton("复制")
        self.noname_copy.clicked.connect(
            lambda: self.copy_to_clipboard(self.noname_text.text())
        )

        # 艺术作品代码
        artwork_layout = QHBoxLayout()
        self.artwork_label = QLabel("艺术作品代码")
        self.artwork_text = QLineEdit(
            "$J('#image_width').val(1000).attr('id',''),$J('#image_height').val(1).attr('id','');"
        )
        self.artwork_text.setReadOnly(True)
        self.artwork_copy = QPushButton("复制")
        self.artwork_copy.clicked.connect(
            lambda: self.copy_to_clipboard(self.artwork_text.text())
        )

        # 创意工坊代码
        workshop_layout = QHBoxLayout()
        self.workshop_label = QLabel("创意工坊代码")
        self.workshop_text = QLineEdit(
            "$J('[name=consumer_app_id]').val(480);$J('[name=file_type]').val(0);$J('[name=visibility]').val(0);"
        )
        self.workshop_text.setReadOnly(True)
        self.workshop_copy = QPushButton("复制")
        self.workshop_copy.clicked.connect(
            lambda: self.copy_to_clipboard(self.workshop_text.text())
        )

        self.noname_label.setFixedWidth(label_width)
        self.artwork_label.setFixedWidth(label_width)
        self.workshop_label.setFixedWidth(label_width)

        noname_layout.addWidget(self.noname_label)
        noname_layout.addWidget(self.noname_text)
        noname_layout.addWidget(self.noname_copy)

        artwork_layout.addWidget(self.artwork_label)
        artwork_layout.addWidget(self.artwork_text)
        artwork_layout.addWidget(self.artwork_copy)

        workshop_layout.addWidget(self.workshop_label)
        workshop_layout.addWidget(self.workshop_text)
        workshop_layout.addWidget(self.workshop_copy)

        common_code_layout.addWidget(common_code_title)
        common_code_layout.addLayout(noname_layout)
        common_code_layout.addLayout(artwork_layout)
        common_code_layout.addLayout(workshop_layout)

        # 布局
        def create_separator():
            """创建分割线"""
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setProperty("class", "separator")
            return separator

        layout.addLayout(file_select_layout)
        layout.addLayout(args_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(create_separator())
        layout.addLayout(common_code_layout)

        self.setLayout(layout)
        self.show()

        self.is_converting = False

    def update_theme(self):
        """更新主题样式"""
        app = QApplication.instance()
        palette = app.palette()
        window_color = palette.color(QPalette.Window)

        # 根据系统主题设置样式
        if window_color.lightness() > 128:
            self.setStyleSheet(self.light_style)
        else:
            self.setStyleSheet(self.dark_style)

    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov)"
        )
        if file_path:
            self.input_path.setText(file_path)

    def load_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_path.setText(dir_path)

    def start_conversion(self):
        self.is_converting = True
        self.start_button.setEnabled(False)
        self.start_button.setText("准备开始转换")

        try:
            target_width = int(self.width_input.text())
            split_parts = int(self.split_input.text())
            max_size_mb = float(self.max_size_input.text())
            filename_prefix = self.filename_input.text()
            hex_value = (
                int(self.hex_input.text().strip(), 16)
                if self.hex_input.text().strip()
                else 21
            )
            fps = int(self.fps_input.text())
            full_gif_name = self.full_gif_name_input.text()
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入正确的数值")
            return

        self.processor = VideoProcessor(
            self.input_path.text(),
            self.output_path.text(),
            target_width,
            split_parts,
            max_size_mb,
            filename_prefix,
            hex_value,
            fps,
            full_gif_name,
        )

        self.processor.progress.connect(self.update_progress)
        self.processor.completed.connect(self.conversion_completed)
        self.processor.error.connect(self.conversion_error)

        self.processor.start()

    def validate_inputs(self):
        """验证所有输入是否有效"""
        if self.is_converting:
            return

        try:
            # 检查必填字段
            if not self.input_path.text() or not self.output_path.text():
                self.start_button.setEnabled(False)
                return

            # 验证数值输入
            int(self.width_input.text())
            int(self.split_input.text())
            float(self.max_size_input.text())
            if self.hex_input.text():
                int(self.hex_input.text(), 16)
            int(self.fps_input.text())

            self.start_button.setEnabled(True)

        except ValueError:
            self.start_button.setEnabled(False)

    def update_progress(self, text):
        """更新进度显示"""
        self.start_button.setText(text)

    def conversion_completed(self, output_path):
        """转换完成后的处理"""
        self.is_converting = False
        self.start_button.setEnabled(True)
        self.start_button.setText("开始转换")
        QMessageBox.information(self, "成功", f"转换完成!\n输出目录: {output_path}")

    def conversion_error(self, error_msg):
        """转换错误处理"""
        self.start_button.setEnabled(True)
        self.start_button.setText("开始转换")
        QMessageBox.critical(self, "错误", f"转换失败: {error_msg}")

    def copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "提示", "已复制到剪贴板")

    def closeEvent(self, event):
        """关闭事件"""
        if self.is_converting:
            reply = QMessageBox.question(
                self,
                "确认退出",
                "正在转换中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()
