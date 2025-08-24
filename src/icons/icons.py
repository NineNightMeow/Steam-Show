from qfluentwidgets import FluentFontIconBase, Theme
import os


class Icon(FluentFontIconBase):
    def path(self, theme=Theme.AUTO):
        return self.getPath("FluentSystemIcons.ttf")

    def iconNameMapPath(self):
        return self.getPath("FluentSystemIcons.json")

    def getPath(self, file):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        return os.path.join(base_dir, "src", "icons", file)
