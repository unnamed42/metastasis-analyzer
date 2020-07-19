from typing import Tuple

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox,
                             QGridLayout,
                             QLabel, QSpinBox, QComboBox)

from backend.medical.windowLevels import defaultLevels

from .ui import Ui_WindowDialog as Ui

class View(QDialog):
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
        self._setupItems(window)

    def _setupItems(self, window):
        comboBox = self._ui.presetComboBox
        # special value (0, 0) for no windowing
        comboBox.addItem(self._names["none"], (0, 0))
        eqIdx = -1
        for (i, (tissue, win)) in enumerate(defaultLevels.items()):
            name = self._names[tissue]
            comboBox.addItem(name, win)
            if win == window:
                eqIdx = i
        if eqIdx == -1:
            comboBox.addItem("当前设置", window)
            comboBox.setCurrentIndex(comboBox.count() - 1)
        else:
            # we have a none window before actual windows
            comboBox.setCurrentIndex(eqIdx + 1)

    @pyqtSlot(int)
    def selectionChanged(self, idx: int):
        wl, ww = self.sender().currentData()
        self._ui.levelEdit.setValue(wl)
        self._ui.widthEdit.setValue(ww)

    def window(self) -> Tuple[int, int]:
        return (self._ui.levelEdit.value(),
                self._ui.widthEdit.value())
