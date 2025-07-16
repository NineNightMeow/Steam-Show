from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from video2gif.gui import Video2GifApp
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from video2gif.gui import Video2GifApp


def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "resources", relative_path)


def main():
    """主程序入口，启动 GUI 界面"""
    app = QApplication([])
    icon_path = get_resource_path("favicon.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = Video2GifApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
