import os
import asyncio
import aiohttp

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QBrush, QColor
from aiohttp import ClientTimeout
from qfluentwidgets import isDarkTheme

from src.app import App


async def getAvatarAsync(url: str, alt: str = "", size=(24, 24)) -> QImage:
    temp_dir = App.getPath("cache")
    default_avatar = os.path.join("src", "images", "default-avatar.png")

    avatar = QImage()
    filename = os.path.basename(url) if url else None
    cache_path = os.path.join(temp_dir, filename) if filename else None

    if not url:
        if os.path.exists(default_avatar):
            avatar = QImage(default_avatar).scaled(
                size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
    elif cache_path and os.path.exists(cache_path):
        avatar.load(cache_path)
        avatar = avatar.scaled(
            size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
    else:
        try:
            timeout = ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    if cache_path:
                        with open(cache_path, "wb") as f:
                            f.write(await response.read())

                        avatar.load(cache_path)
                        avatar = avatar.scaled(
                            size[0],
                            size[1],
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation,
                        )
        except Exception as e:
            print(f"Failed to load avatar: {e}")
            if os.path.exists(default_avatar):
                avatar = QImage(default_avatar).scaled(
                    size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

    final_img = QImage(size[0], size[1], QImage.Format_ARGB32)
    final_img.fill(Qt.transparent)

    painter = QPainter(final_img)
    painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(80, 80, 80) if isDarkTheme() else QColor(240, 240, 240))
    painter.drawEllipse(0, 0, final_img.width(), final_img.height())

    if not avatar.isNull():
        mask = QImage(size[0], size[1], QImage.Format_ARGB32)
        mask.fill(Qt.transparent)
        mask_painter = QPainter(mask)
        mask_painter.setRenderHints(QPainter.Antialiasing)
        mask_painter.setBrush(QBrush(avatar))
        mask_painter.setPen(Qt.NoPen)
        mask_painter.drawEllipse(0, 0, size[0], size[1])
        mask_painter.end()

        painter.drawImage(0, 0, mask)
    elif alt:
        painter.setPen(QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0))
        painter.drawText(
            final_img.rect(),
            Qt.AlignCenter,
            alt[:1],
        )

    painter.end()
    return final_img


def getAvatar(url: str, alt: str = "", size=(24, 24)) -> QImage:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(getAvatarAsync(url, alt, size))
