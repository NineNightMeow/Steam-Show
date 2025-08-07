# 简介

使用 PyQt5 + OpenCV 开发，用于制作与部署 Steam 个人资料展柜

<img src="screenshot.png" alt="软件截图">

### 功能特点

-   视频（MP4、AVI、MOV 等格式）转换展柜 GIF 文件
-   内置部署功能，让你轻松部署到 Steam 个人资料展柜

### 开发

确保你的 Python 版本 >= 3.8

#### 安装依赖

```
pip install -r requirements.txt
```

#### 打包

本软件使用 Nuitka 进行打包

```
python -m nuitka --standalone --onefile --remove-output --windows-console-mode="disable" --enable-plugins="pyqt5" --output-filename="Steam-Show" --output-dir="dist" --main="main.py" --windows-icon-from-ico="src/icons/favicon.ico" 
```

**PyQt-Fluent-Widgets** 的使用方法请参考 [官方文档](https://qfluentwidgets.com/zh/pages/about)

> [!WARNING]
> 请不要混用 PyQt 与 PySide，否则可能会导致程序闪退 [详见](https://qfluentwidgets.com/zh/pages/install)

### 法律声明

本软件采用 CC BY-NC 4.0 许可证，软件著作者共同享有版权，仅供个人学习使用，禁止本体与衍生品用于任何商业用途
