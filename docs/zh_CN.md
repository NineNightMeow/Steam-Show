<pre>
<a href="https://github.com/NineNightMeow/Steam-Show">← 回到仓库首页</a>
</pre>

# Steam Show

##### 使用 PySide6 开发的 GUI，用于制作与部署 Steam 个人资料展柜

### 简介

<img src="screenshot.png" alt="软件截图">

#### 功能特点

-   视频（MP4、AVI、MOV 等格式）转换展柜文件
-   内置部署功能，让你轻松应用到个人资料展柜
-   提供带预览功能的文本编辑器、等级计算器等实用工具

### 下载

可以在右侧的 [Releases](https://github.com/NineNightMeow/Steam-Show/releases) 页面下载最新版本

### 开发

确保你的 Python 版本 >= 3.8

PyQt-Fluent-Widgets 的使用方法请参考 [官方文档](https://qfluentwidgets.com/zh/pages/about)

> [!WARNING]
> 请确保你所安装的是 PySide6-Fluent-Widgets，否则可能会导致程序闪退  
> [详见](https://qfluentwidgets.com/zh/pages/install)

#### 安装依赖

```
pip install -r requirements.txt
```

#### 打包

本软件使用 Nuitka 进行打包

```
python -m nuitka --standalone --onefile --remove-output --windows-console-mode="disable" --enable-plugins="pyqt5" --output-filename="Steam-Show" --output-dir="dist" --main="main.py" --windows-icon-from-ico="src/icons/favicon.ico"
```

#### 翻译

翻译文件存放在 `src/i18n` 文件夹下，使用 Qt Linguist 工具进行翻译

### 贡献

欢迎提交 [Issues](https://github.com/NineNightMeow/Steam-Show/issues) 或 [Pull Requests](https://github.com/NineNightMeow/Steam-Show/pulls)

### 赞助

如果本软件对你有帮助，请考虑赞助作者以支持开发 🩷

### 许可证

本项目使用 [GPL-3.0 License](https://github.com/NineNightMeow/Steam-Show/blob/main/LICENSE) 许可证
