from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from qfluentwidgets import (
    CaptionLabel,
    StrongBodyLabel,
    SpinBox,
    ElevatedCardWidget,
    IconWidget,
)

from src.views.interface import Interface
from src.utils.translator import Translator
from src.utils.calculator import Calc
from src.icons.icons import Icon


class Card(ElevatedCardWidget):
    def __init__(
        self,
        icon=None,
        name: str = "",
        count: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self.icon = IconWidget(icon, self)
        self.name = CaptionLabel(name, self)
        self.count = StrongBodyLabel(str(count), self)

        self.icon.setFixedSize(50, 50)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.icon, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.name, 0, Qt.AlignHCenter | Qt.AlignBottom)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.count, 0, Qt.AlignHCenter | Qt.AlignTop)

    def setCount(self, count: int):
        self.count.setText(str(count))


class Level(Interface):
    def __init__(self):
        super().__init__(
            title=Translator().level_title,
            subtitle=Translator().level_subtitle,
        )
        self.setObjectName("level")

        layout = QVBoxLayout()

        self.args = QWidget()
        self.args_layout = QHBoxLayout(self.args)

        self.current_level = QWidget()
        self.current_level_layout = QVBoxLayout(self.current_level)

        self.current_input = SpinBox()
        self.current_input.setRange(0, 10000)
        self.current_input.setValue(0)
        self.current_input.valueChanged.connect(self.calc)

        self.current_level_layout.addWidget(CaptionLabel(self.tr("Current Level")))
        self.current_level_layout.addWidget(self.current_input)

        self.target_level = QWidget()
        self.target_level_layout = QVBoxLayout(self.target_level)

        self.target_input = SpinBox()
        self.target_input.setRange(0, 10000)
        self.target_input.setValue(100)
        self.target_input.valueChanged.connect(self.calc)

        self.target_level_layout.addWidget(CaptionLabel(self.tr("Target Level")))
        self.target_level_layout.addWidget(self.target_input)

        self.args_layout.addWidget(self.current_level)
        self.args_layout.addWidget(self.target_level)

        self.tip = CaptionLabel()
        self.tip.setStyleSheet("color:red;")
        self.tip.setContentsMargins(10, 0, 10, 10)

        self.result = QWidget()
        self.result_layout = QGridLayout(self.result)
        self.result_layout.setColumnStretch(0, 1)
        self.result_layout.setColumnStretch(1, 1)

        self.exp_card = Card(Icon.fromName("Reward20Regular"), self.tr("Exp needed"))
        self.sets_card = Card(Icon.fromName("PlayingCards20Regular"), self.tr("Sets needed"))
        self.friends_card = Card(Icon.fromName("People20Regular"), self.tr("Friends Count"))
        self.showcase_card = Card(
            Icon.fromName("AppRecent20Regular"), self.tr("Showcase Unlocked")
        )

        self.result_layout.addWidget(self.exp_card, 0, 0)
        self.result_layout.addWidget(self.sets_card, 0, 1)
        self.result_layout.addWidget(self.friends_card, 1, 0)
        self.result_layout.addWidget(self.showcase_card, 1, 1)

        layout.addWidget(self.args)
        layout.addWidget(self.tip)
        layout.addWidget(self.result)
        layout.addStretch(1)

        self.view.setLayout(layout)

        self.calc()

    def calc(self):
        current = self.current_input.value()
        target = self.target_input.value()

        if current == 0:
            self.tip.setText(self.tr("You must cost $5 to upgrade to level 1"))
            return

        if current > target:
            self.tip.setText(
                self.tr("Current level cannot be greater than target level")
            )
            return

        self.tip.setText("")

        result = Calc(current, target)

        self.exp_card.setCount(result["exp"])
        self.sets_card.setCount(result["sets"])
        self.friends_card.setCount(result["friends"])
        self.showcase_card.setCount(result["showcase"])
