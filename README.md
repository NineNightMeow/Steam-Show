# Introduction

Developed by PyQt5 + OpenCV, used to create and deploy Steam personal profile showcases

<img src="docs/screenshot.png" alt="screenshot">

### Features

-   Video(MP4, AVI, MOV, etc.) to GIF converter
-   Built-in deployment function, making it easy to deploy to Steam personal profile showcases

### Development

Ensure your Python version is >= 3.8

#### Install dependencies

```
pip install -r requirements.txt
```

#### Packing

This application uses Nuitka to pack the executable file

```
python -m nuitka --standalone --onefile --remove-output --windows-console-mode="disable" --enable-plugins="pyqt5" --output-filename="Steam-Show" --output-dir="dist" --main="main.py" --windows-icon-from-ico="src/icons/favicon.ico" 
```

Usage of **PyQt-Fluent-Widgets** [Docs](https://qfluentwidgets.com/pages/about)

> [!WARNING]
> Please do not mix PyQt and PySide, otherwise the program may crash [see](https://qfluentwidgets.com/pages/install)

### License

This software is licensed under the CC BY-NC 4.0 license. The software author and copyright holder reserves all rights, including but not limited to the right to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software.
