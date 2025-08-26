import os

from PySide6.QtCore import QStandardPaths


class App:
    name = "Steam Show"
    version = "1.0.0"

    appDataDir = os.path.join(
        QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), name
    )
    dirs = [
        ["config", os.path.join(appDataDir, "config")],
        ["cache", os.path.join(appDataDir, "cache")],
        ["temp", os.path.join(appDataDir, "temp")],
        ["logs", os.path.join(appDataDir, "logs")],
    ]

    for dir in dirs:
        if not os.path.exists(dir[1]):
            os.makedirs(dir[1])

    @classmethod
    def getName(cls):
        return cls.name

    @classmethod
    def getVersion(cls):
        return cls.version

    @classmethod
    def getPath(cls, path=None):
        if path in [d[0] for d in cls.dirs]:
            return cls.dirs[[d[0] for d in cls.dirs].index(path)][1]
        else:
            return cls.appDataDir
