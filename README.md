<pre align="center">
<a href="docs/zh_CN.md">简体中文</a> | <a href="docs/zh_TW.md">繁體中文</a> | <a href="docs/ja_JP.md">日本語</a>
</pre>

# Introduction

Developed by PySide6 + OpenCV, used to create and deploy Steam personal profile showcases

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

Usage of _PyQt-Fluent-Widgets_ **[Docs](https://qfluentwidgets.com/pages/about)**

> [!WARNING]
> Please do not mix PyQt and PySide, for the program may crash **[SEE](https://qfluentwidgets.com/pages/install)**
