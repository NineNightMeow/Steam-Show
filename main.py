from PySide6.QtWidgets import QApplication
from video2gif.gui import Video2GifApp
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from video2gif.gui import Video2GifApp

def main():
    """主程序入口，启动 GUI 界面"""
    app = QApplication([])
    window = Video2GifApp()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
