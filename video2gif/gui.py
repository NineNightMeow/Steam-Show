from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog,
    QLineEdit, QMessageBox, QProgressBar, QComboBox
) 
from PySide6.QtCore import Qt, QTimer
from video2gif.processor import VideoProcessor
import os
#作案工具
class Video2GifApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP4文件一键转steam展框小工具-By Kuri&Hapy")
        self.setGeometry(300, 300, 600, 800)

        layout = QVBoxLayout(self)

        self.video_label = QLabel("选择视频文件:")
        layout.addWidget(self.video_label)
        self.video_path = QLineEdit()
        layout.addWidget(self.video_path)
        self.video_button = QPushButton("浏览")
        layout.addWidget(self.video_button)
        self.video_button.clicked.connect(self.load_video)

        self.output_label = QLabel("选择输出目录:")
        layout.addWidget(self.output_label)
        self.output_path = QLineEdit()
        layout.addWidget(self.output_path)
        self.output_button = QPushButton("浏览")
        layout.addWidget(self.output_button)
        self.output_button.clicked.connect(self.load_output_dir)

        self.width_label = QLabel("目标宽度 (px):")
        layout.addWidget(self.width_label)
        self.width_input = QLineEdit("630")
        layout.addWidget(self.width_input)

        self.split_label = QLabel("GIF 分割份数:")
        layout.addWidget(self.split_label)
        self.split_input = QLineEdit("5")
        layout.addWidget(self.split_input)

        self.max_size_label = QLabel("最大单个 GIF 大小 (MB):")
        layout.addWidget(self.max_size_label)
        self.max_size_input = QLineEdit("5")
        layout.addWidget(self.max_size_input)
        
        self.full_gif_name_label = QLabel("完整 GIF 文件名称:")
        layout.addWidget(self.full_gif_name_label)
        self.full_gif_name_input = QLineEdit("output.gif")
        layout.addWidget(self.full_gif_name_input)

        self.filename_label = QLabel("GIF 文件名前缀:")
        layout.addWidget(self.filename_label)
        self.filename_input = QLineEdit("split_gif")
        layout.addWidget(self.filename_input)
        
        self.hex_label =QLabel("修改 GIF 末位 16 进制数 (0-255) (默认21即可):")
        layout.addWidget(self.hex_label)
        self.hex_input = QLineEdit("21")
        layout.addWidget(self.hex_input)
        
        self.fps_label = QLabel("GIF 帧率 (FPS):")
        layout.addWidget(self.fps_label)
        self.fps_input = QLineEdit("15")  # 默认 15 FPS
        layout.addWidget(self.fps_input)

        self.rename_label = QLabel("文件重命名策略:")
        layout.addWidget(self.rename_label)
        self.rename_combo = QComboBox()
        self.rename_combo.addItems(["覆盖", "自动编号"])
        layout.addWidget(self.rename_combo)

        self.method_label = QLabel("选择转换方式:")
        layout.addWidget(self.method_label)
        self.method_combo = QComboBox()
        self.method_combo.addItems([ "FFmpeg"])
        layout.addWidget(self.method_combo)

        self.method_label = QLabel("是否启用临时预览")
        layout.addWidget(self.method_label)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Yes","No"])
        layout.addWidget(self.method_combo)

        self.start_button = QPushButton("开始转换")
        layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.start_conversion)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.fixed_text = QLineEdit("无名代码v_trim=_=>{return _},$J('#title').val(' '+Array.from(Array(126),_=>'').join(''));")
        self.fixed_text.setReadOnly(True)  # 设为只读
        self.fixed_text.setAlignment(Qt.AlignCenter)  # 居中
        layout.addWidget(self.fixed_text)
        
        self.fixed_text = QLineEdit("艺术作品代码$J('#image_width').val(1000).attr('id',''),$J('#image_height').val(1).attr('id','');")
        self.fixed_text.setReadOnly(True)  # 设为只读
        self.fixed_text.setAlignment(Qt.AlignCenter)  # 居中
        layout.addWidget(self.fixed_text)
        
        self.fixed_text = QLineEdit("工坊$J('[name=consumer_app_id]').val(480);$J('[name=file_type]').val(0);$J('[name=visibility]').val(0);")
        self.fixed_text.setReadOnly(True)  # 设为只读
        self.fixed_text.setAlignment(Qt.AlignCenter)  # 居中
        layout.addWidget(self.fixed_text)

        self.setLayout(layout)
        self.show()

    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov)")
        if file_path:
            self.video_path.setText(file_path)

    def load_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self,"选择输出目录")
        if dir_path:
            self.output_path.setText(dir_path)

    def start_conversion(self):
        try:
            target_width = int(self.width_input.text())
            split_parts = int(self.split_input.text())
            max_size_mb = float(self.max_size_input.text())
            filename_prefix = self.filename_input.text()
            full_gif_name = self.full_gif_name_input.text()
            rename_strategy = self.rename_combo.currentText()
            method = self.method_combo.currentText()
            hex_value = int(self.hex_input.text().strip(), 16) if self.hex_input.text().strip() else 21
            fps = int(self.fps_input.text())
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入正确的数值")
            return

        self.processor = VideoProcessor(
            self.video_path.text(), self.output_path.text(), target_width, split_parts, max_size_mb,
            filename_prefix, rename_strategy, method, hex_value, fps, full_gif_name
        )
        self.processor.progress.connect(self.progress_bar.setValue)
        self.processor.completed.connect(lambda path: QMessageBox.information(self, "完成", f"GIF 生成成功: {path}"))
        self.processor.error.connect(lambda err: QMessageBox.critical(self, "错误", err))
        self.processor.start()
