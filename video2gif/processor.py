import sys
import os
import subprocess
from PIL import Image, ImageSequence
from PySide6.QtCore import QThread, Signal


# 作案工具2.0
class VideoProcessor(QThread):
    progress = Signal(str)
    completed = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        input_path,
        output_dir,
        target_width,
        split_parts,
        max_size_mb,
        filename_prefix,
        hex_value=None,
        fps=15,
        full_gif_name="output.gif",
    ):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.target_width = target_width
        self.split_parts = split_parts
        self.max_size_mb = max_size_mb
        self.filename_prefix = filename_prefix
        self.hex_value = hex_value  # 16进制
        self.fps = fps  # 确保帧率一致
        self.full_gif_name = full_gif_name

        # 创建 output 文件夹
        self.output_dir = os.path.join(output_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

        # 获取 FFmpeg 路径（绝对位置）
        self.ffmpeg_path = self.add_ffmpeg_to_path()

    # 作案变量
    @staticmethod
    def add_ffmpeg_to_path():
        if getattr(sys, "frozen", False):
            base_dir = os.path.join(sys._MEIPASS, "ffmpeg")  # PyInstaller 运行时路径
        else:
            base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "ffmpeg")
            )

        ffmpeg_path = os.path.join(base_dir, "ffmpeg.exe")
        if not os.path.exists(ffmpeg_path):
            raise FileNotFoundError(f"未找到ffmpeg: {ffmpeg_path}")
        return ffmpeg_path

    def run(self):
        try:
            gif_path = os.path.join(self.output_dir, self.full_gif_name)

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            self.convert_with_ffmpeg(gif_path)

            self.split_gif(gif_path)
            self.completed.emit(gif_path)
        except Exception as e:
            self.error.emit(str(e))

    def convert_with_ffmpeg(self, output_path):
        # 使用 FFmpeg 进行 GIF 转换
        if os.path.exists(output_path):
            os.remove(output_path)  # 先删除重复文件（这里注意下）确保 ffmpeg可以写入
        ffmpeg_cmd = [
            self.ffmpeg_path,
            "-y",
            "-i",
            self.input_path,
            "-vf",
            f"fps={self.fps},scale={self.target_width}:-1:flags=lanczos",
            "-c:v",
            "gif",
            output_path,
        ]
        subprocess.run(ffmpeg_cmd, check=True)

    def split_gif(self, input_gif):
        # 分割 GIF 并确保帧率一致？
        gif = Image.open(input_gif)
        width, height = gif.size
        part_width = width // self.split_parts

        for i in range(self.split_parts):
            self.progress.emit(f"转换文件中 {i + 1}/{self.split_parts}")

            left, right = i * part_width, (i + 1) * part_width
            frames = [
                frame.crop((left, 0, right, height))
                for frame in ImageSequence.Iterator(gif)
            ]
            part_output = os.path.join(
                self.output_dir, f"{self.filename_prefix}_{i+1}.gif"
            )

            frames[0].save(
                part_output,
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=int(1000 / self.fps),
                disposal=2,
            )

            self.ensure_gif_fps(part_output)

            # 确保文件正确生成
            if not os.path.exists(part_output) or os.path.getsize(part_output) == 0:
                raise FileNotFoundError(f"GIF分割失败，文件 {part_output} 为空！")

            self.compress_gif(part_output)

            # 修改 GIF 末位字节
            if self.hex_value is not None:
                self.modify_gif_hex(part_output)

    def ensure_gif_fps(self, gif_path):
        """使用 FFmpeg 确保所有 GIF 帧率一致"""
        temp_output = gif_path.replace(".gif", "_fps_fixed.gif")
        command = [
            self.ffmpeg_path,
            "-y",
            "-i",
            gif_path,
            "-vf",
            f"fps={self.fps}",
            temp_output,
        ]
        subprocess.run(command, check=True)
        os.replace(temp_output, gif_path)

    def modify_gif_hex(self, input_gif):
        """修改 GIF 末位 16 进制数"""
        try:
            with open(input_gif, "r+b") as f:
                f.seek(-1, os.SEEK_END)
                f.write(bytes([self.hex_value]))
            print(f"GIF {input_gif} 末位字节修改成功: {self.hex_value:02x}")
        except Exception as e:
            print(f"修改 GIF16 进制失败: {e}")

    def compress_gif(self, input_gif):
        """如果 GIF 大小超过 max_size_mb，则使用 FFmpeg 进行压缩"""
        self.progress.emit(f"正在压缩文件")
        while os.path.getsize(input_gif) > self.max_size_mb * 1024 * 1024:
            print(f"GIF{input_gif} 超出 {self.max_size_mb}MB，正在压缩...")

            temp_output = input_gif.replace(".gif", "_compressed.gif")

            command = [
                self.ffmpeg_path,
                "-y",
                "-i",
                input_gif,
                "-vf",
                "fps=10,scale=iw/2:ih/2:flags=lanczos",  # 降低帧率&缩小尺寸
                "-b:v",
                "500k",
                "-gifflags",
                "+transdiff",
                "-y",
                temp_output,
            ]
            subprocess.run(command, check=True)

            # 替换原文件
            os.replace(temp_output, input_gif)

            # 重复检查大小
            if os.path.getsize(input_gif) <= self.max_size_mb * 1024 * 1024:
                print(
                    f"GIF {input_gif} 已压缩到 {os.path.getsize(input_gif) / 1024 / 1024:.2f}MB"
                )
                break
