# 概要

PySide6 + OpenCV を使用して開発された、Steam プロフィール展示用のツール

<img src="screenshot.png" alt="ソフトウェアスクリーンショット">

### 主な機能

-   動画（MP4、AVI、MOV などの形式）を展示用 GIF ファイルに変換
-   内蔵のデプロイ機能で、Steam プロフィール展示に簡単に設置可能

### 開発環境

Python バージョン >= 3.8 が必要

#### 依存関係のインストール

```
pip install -r requirements.txt
```

#### パッケージ化

本ソフトウェアは Nuitka を使用してパッケージ化しています

```
python -m nuitka --standalone --onefile --remove-output --windows-console-mode="disable" --enable-plugins="pyqt5" --output-filename="Steam-Show" --output-dir="dist" --main="main.py" --windows-icon-from-ico="src/icons/favicon.ico"
```

_PyQt-Fluent-Widgets_ の使用方法については、以下を参照してください **[公式ドキュメント](https://qfluentwidgets.com/pages/about)**

> [!WARNING]
> PyQt と PySide を混在させないでください。プログラムがクラッシュする可能性があります **[詳細](https://qfluentwidgets.com/pages/install)**