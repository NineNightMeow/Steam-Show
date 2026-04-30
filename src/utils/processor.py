import os
import sys
import subprocess

from PIL import Image, ImageSequence
from PySide6.QtCore import QThread, Signal
from src.utils.translator import Translator


class Processor(QThread):
    progress = Signal(str)
    completed = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        input_path,
        output_dir,
        duration,
        split_cols,
        target_width,
        max_size,
        hex_val,
        fps,
        quality=80,
    ):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.duration = duration
        self.split_cols = split_cols
        self.target_width = target_width
        self.max_size = max_size
        self.hex_val = hex_val
        self.fps = fps
        self.quality = quality

        self.output_dir = os.path.join(output_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

        self.ffmpeg_path = self.add_ffmpeg_to_path()
        self.trans = Translator()

    @staticmethod
    def add_ffmpeg_to_path():
        if getattr(sys, "frozen", False):
            ffmpeg_path = os.path.join(
                os.path.dirname(sys.executable), "src", "utils", "ffmpeg.exe"
            )
            if not os.path.exists(ffmpeg_path):
                ffmpeg_path = os.path.join(sys._MEIPASS, "src", "utils", "ffmpeg.exe")
        else:
            ffmpeg_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
            )

        if not os.path.exists(ffmpeg_path):
            raise FileNotFoundError(f"ffmpeg not found: {ffmpeg_path}")

        return ffmpeg_path

    def tr(self, text):
        return self.trans.tr(text)

    def run(self):
        try:
            file_ext = os.path.splitext(self.input_path)[1].lower()

            if file_ext in (".png", ".jpg", ".jpeg"):
                self.process_image()
            elif file_ext == ".gif":
                self.process_gif()
            else:
                self.process_video()

            self.completed.emit(os.path.normpath(self.output_dir))
        except Exception as e:
            self.error.emit(str(e))

    def process_image(self):
        file_ext = os.path.splitext(self.input_path)[1].lower()

        img = Image.open(self.input_path)
        width, height = img.size

        new_height = int(height * (self.target_width / width))
        img = img.resize((self.target_width, new_height), Image.LANCZOS)

        part_width = self.target_width // self.split_cols

        for i in range(self.split_cols):
            self.progress.emit(f"{i + 1}/{self.split_cols} {self.tr('Splitting')}")

            left = i * part_width
            right = (i + 1) * part_width if i < self.split_cols - 1 else self.target_width

            part_img = img.crop((left, 0, right, new_height))
            part_output = os.path.join(
                self.output_dir, f"part_{i + 1}{file_ext}"
            )

            if file_ext == ".png":
                part_img.save(part_output, "PNG")
            else:
                part_img.save(part_output, "JPEG", quality=self.quality)

            if not os.path.exists(part_output) or os.path.getsize(part_output) == 0:
                raise FileNotFoundError(f"Fail to split image: {part_output}")

            if file_ext in (".jpg", ".jpeg"):
                self.compress_image(part_output, i + 1, self.split_cols)

    def process_gif(self):
        gif_path = os.path.join(self.output_dir, "temp.gif")

        if os.path.exists(gif_path):
            os.remove(gif_path)

        self.convert_to_gif(self.input_path, gif_path)
        self.split_gif(gif_path)

    def process_video(self):
        gif_path = os.path.join(self.output_dir, "temp.gif")

        if os.path.exists(gif_path):
            os.remove(gif_path)

        self.convert_with_ffmpeg(self.input_path, gif_path)
        self.split_gif(gif_path)

        if os.path.exists(gif_path):
            os.remove(gif_path)

    def convert_with_ffmpeg(self, input_path, output_path):
        if os.path.exists(output_path):
            os.remove(output_path)

        ffmpeg_cmd = [
            self.ffmpeg_path,
            "-y",
            "-i",
            input_path,
            "-t",
            str(self.duration),
            "-vf",
            f"fps={self.fps},scale={self.target_width}:-1:flags=lanczos",
            "-f",
            "gif",
            output_path,
        ]
        subprocess.run(ffmpeg_cmd, check=True)

    def convert_to_gif(self, input_path, output_path):
        if os.path.exists(output_path):
            os.remove(output_path)

        if input_path.lower().endswith(".gif"):
            img = Image.open(input_path)
            frames = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.copy()
                frame = frame.convert("P")
                frames.append(frame)

            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=img.info.get("duration", 100),
            )
        else:
            self.convert_with_ffmpeg(input_path, output_path)

    def split_gif(self, input_gif):
        gif = Image.open(input_gif)
        width, height = gif.size
        part_width = width // self.split_cols

        frame_duration = gif.info.get("duration", 1000 / self.fps)

        for i in range(self.split_cols):
            self.progress.emit(f"{i + 1}/{self.split_cols} {self.tr('Splitting')}")

            left = i * part_width
            right = (i + 1) * part_width if i < self.split_cols - 1 else width

            frames = [
                frame.crop((left, 0, right, height))
                for frame in ImageSequence.Iterator(gif)
            ]
            part_output = os.path.join(self.output_dir, f"part_{i + 1}.gif")

            frames[0].save(
                part_output,
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=int(frame_duration),
                disposal=2,
            )

            self.ensure_gif_fps(part_output)

            if not os.path.exists(part_output) or os.path.getsize(part_output) == 0:
                raise FileNotFoundError(f"Fail to split gif: {part_output}")

            if self.hex_val is not None:
                self.modify_gif_hex(part_output)

        all_parts = [
            os.path.join(self.output_dir, f"part_{j + 1}.gif")
            for j in range(self.split_cols)
        ]

        need_compress = any(
            os.path.getsize(p) > self.max_size * 1024 * 1024 for p in all_parts
        )

        if need_compress:
            for i, part_path in enumerate(all_parts, 1):
                self.progress.emit(f"{i}/{self.split_cols} {self.tr('Compressing')}")
                self.compress_gif(part_path)

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
        try:
            with open(input_gif, "r+b") as f:
                f.seek(-1, os.SEEK_END)
                f.write(bytes([self.hex_val]))
            print(f"Modified hex of {input_gif} to {self.hex_val:02x}")
        except Exception as e:
            print(f"Failed to modify hex: {e}")

    def compress_gif(self, input_gif):
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

            os.replace(temp_output, input_gif)

            if os.path.getsize(input_gif) <= self.max_size * 1024 * 1024:
                print(
                    f"Compressed {input_gif} to {os.path.getsize(input_gif) / 1024 / 1024:.2f}MB"
                )
                break

    def compress_image(self, input_image, index, total):
        file_ext = os.path.splitext(input_image)[1].lower()
        if file_ext not in (".jpg", ".jpeg"):
            return

        while os.path.getsize(input_image) > self.max_size * 1024 * 1024:
            print(f"File {input_image} is too large, compressing...")

            img = Image.open(input_image)
            width, height = img.size
            new_width = int(width * 0.9)
            new_height = int(height * 0.9)
            img = img.resize((new_width, new_height), Image.LANCZOS)

            quality = self.quality
            while quality > 10:
                img.save(input_image, "JPEG", quality=quality)
                if os.path.getsize(input_image) <= self.max_size * 1024 * 1024:
                    print(
                        f"Compressed {input_image} to {os.path.getsize(input_image) / 1024 / 1024:.2f}MB"
                    )
                    return
                quality -= 10

            if os.path.getsize(input_image) > self.max_size * 1024 * 1024:
                raise FileNotFoundError(f"Cannot compress {input_image} below {self.max_size}MB")
