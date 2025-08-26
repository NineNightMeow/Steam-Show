import os
import asyncio
import aiohttp

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from aiohttp import ClientTimeout

from src.app import App


async def getAvatarAsync(avatar_url: str, size=(24, 24)) -> QImage:
    temp_dir = App.getPath("cache")
    default_avatar = os.path.join("src", "images", "default_avatar-avatar.png")

    avatar = QImage()

    if not avatar_url:
        if os.path.exists(default_avatar):
            avatar = QImage(default_avatar).scaled(
                size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        return avatar

    filename = os.path.basename(avatar_url)
    if os.path.exists(filename):
        avatar.load(filename)
        avatar = avatar.scaled(
            size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        return avatar

    try:
        timeout = ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with session.get(avatar_url, headers=headers) as response:
                response.raise_for_status()
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

                temp_dir = os.path.join(temp_dir, filename)
                with open(temp_dir, "wb") as f:
                    f.write(await response.read())

                avatar.load(temp_dir)
                avatar = avatar.scaled(
                    size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

    except aiohttp.ClientError as e:
        print(f"Failed to download avatar: {e}")
        if os.path.exists(default_avatar):
            avatar = QImage(default_avatar).scaled(
                size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
    except Exception as e:
        print(f"Error processing avatar: {e}")
        if os.path.exists(default_avatar):
            avatar = QImage(default_avatar).scaled(
                size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

    return avatar


def getAvatar(avatar_url: str, size=(24, 24)) -> QImage:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(getAvatarAsync(avatar_url, size))
