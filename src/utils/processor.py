import sys
import os
import subprocess

from PIL import Image, ImageSequence
from PySide6.QtCore import QThread, Signal


class Processor(QThread):
    progress = Signal(str)
    completed = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        input_path,
        output_dir,
        duration,
        split_parts,
        target_width,
        max_size,
        hex,
        fps,
    ):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.duration = duration
        self.split_parts = split_parts
        self.target_width = target_width
        self.max_size = max_size
        self.hex = hex
        self.fps = fps

        # 创建输出文件夹
        self.output_dir = os.path.join(output_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

        # 获取 FFmpeg 路径
        self.ffmpeg_path = self.add_ffmpeg_to_path()

    @staticmethod
    def add_ffmpeg_to_path():
        """获取 ffmpeg 可执行文件路径"""
        if getattr(sys, "frozen", False):
            # PyInstaller 打包后路径
            ffmpeg_path = os.path.join(
                os.path.dirname(sys.executable), "src", "utils", "ffmpeg.exe"
            )
            if not os.path.exists(ffmpeg_path):
                # 尝试临时目录
                ffmpeg_path = os.path.join(sys._MEIPASS, "src", "utils", "ffmpeg.exe")
        else:
            # 开发环境路径
            ffmpeg_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
            )

        if not os.path.exists(ffmpeg_path):
            raise FileNotFoundError(f"ffmpeg not found: {ffmpeg_path}")

        return ffmpeg_path

    def run(self):
        try:
            gif_path = os.path.join(self.output_dir, "output.gif")

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            self.convert_with_ffmpeg(gif_path)

            self.split_gif(gif_path)
            self.completed.emit(os.path.normpath(self.output_dir))
        except Exception as e:
            self.error.emit(str(e))

    def convert_with_ffmpeg(self, output_path):
        if os.path.exists(output_path):
            os.remove(output_path)
        ffmpeg_cmd = [
            self.ffmpeg_path,
            "-y",
            "-i",
            self.input_path,
            "-t",
            str(self.duration),
            "-vf",
            f"fps={self.fps},scale={self.target_width}:-1:flags=lanczos",
            "-f",
            "gif",
            output_path,
        ]
        subprocess.run(ffmpeg_cmd, check=True)

    def split_gif(self, input_gif):
        gif = Image.open(input_gif)
        width, height = gif.size
        part_width = width // self.split_parts

        for i in range(self.split_parts):
            self.progress.emit(f"{i + 1}/{self.split_parts} {self.tr('Converting')}")

            left, right = i * part_width, (i + 1) * part_width
            frames = [
                frame.crop((left, 0, right, height))
                for frame in ImageSequence.Iterator(gif)
            ]
            part_output = os.path.join(self.output_dir, f"part_{i+1}.gif")

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
                raise FileNotFoundError(f"Fail to split gif: {part_output} is empty")

            self.compress_gif(part_output, i + 1, self.split_parts)

            # 修改 GIF 末位字节
            if self.hex is not None:
                self.modify_gif_hex(part_output)

    def ensure_gif_fps(self, gif_path):
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
                f.write(bytes([self.hex]))
            print(f"Successfully modified hex of {input_gif} to {self.hex:02x}")
        except Exception as e:
            print(f"Failed to modify hex: {e}")

    def compress_gif(self, input_gif, index, total):
        """超过 max_size 压缩"""
        self.progress.emit(f"{index}/{total} {self.tr('Compressing')}")
        while os.path.getsize(input_gif) > self.max_size * 1024 * 1024:
            print(f"File {input_gif} is too large, compressing...")

            temp_output = input_gif.replace(".gif", "_compressed.gif")

            command = [
                self.ffmpeg_path,
                "-y",
                "-i",
                input_gif,
                "-vf",
                "fps=10,scale=iw/2:ih/2:flags=lanczos",
                "-b:v",
                "500k",
                "-gifflags",
                "+transdiff",
                temp_output,
            ]
            subprocess.run(command, check=True)

            # 替换原文件
            os.replace(temp_output, input_gif)

            # 重复检查大小
            if os.path.getsize(input_gif) <= self.max_size * 1024 * 1024:
                print(
                    f"Successfully compressed {input_gif} to {os.path.getsize(input_gif) / 1024 / 1024:.2f}MB"
                )
                break
