from typing import Tuple

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox,
                             QGridLayout,
                             QLabel, QSpinBox, QComboBox)

from app.backend.windowLevels import defaultLevels
from app.ui.generated.Ui_WindowDialog import Ui_WindowDialog as Ui

class WindowDialog(QDialog):
    _names = {
        "bone": "骨头",
        "lung": "肺部",
        "brain": "脑部",
        "chest": "胸腔",
        "none": "无窗口化"
    }

    def __init__(self, window: Tuple[int, int], parent=None):
        super().__init__(parent)

        self._ui = Ui()
        self._ui.setupUi(self)
        self._setupItems()

        self._ui.presetComboBox.currentIndexChanged.connect(self._on_selectionChanged)

    def _setupItems(self):
        comboBox = self._ui.presetComboBox
        for (tissue, window) in defaultLevels.items():
            name = self._names[tissue]
            comboBox.addItem(name, window)
        # special value (0, 0) for no windowing
        comboBox.addItem(self._names["none"], (0, 0))

    @pyqtSlot(int)
    def _on_selectionChanged(self, idx: int):
        wl, ww = self.sender().currentData()
        self._ui.levelEdit.setValue(wl)
        self._ui.widthEdit.setValue(ww)

    def window(self) -> Tuple[int, int]:
        return (self._ui.levelEdit.value(),
                self._ui.widthEdit.value())

