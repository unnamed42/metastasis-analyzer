import numpy as np

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSlot, Qt, QRectF
from PyQt5.QtWidgets import (QMainWindow, qApp, QWidget,
                             QGraphicsPixmapItem, QGraphicsScene,
                             QDialog, QFileDialog)

from app.ui.WindowDialog import WindowDialog
from app.ui.MainWindowModel import MainWindowModel as Model
from app.ui.generated.Ui_MainWindow import Ui_MainWindow as Ui
from app.backend.windowLevels import defaultLevels

def _toQImage(ndarray):
    """
    Convert numpy 8-bit grayscale image to QImage
    """
    height, width = ndarray.shape
    # TODO: more memory efficient data passing
    #addr, rw = ndarray.__array_interface__["data"]
    #content = voidptr(addr, writeable=rw)
    content = ndarray.tobytes()
    return QImage(content, width, height, QImage.Format_Grayscale8)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        window = defaultLevels["lung"]

        self._ui = Ui()
        self._setupUi()
        self._model = Model(window)
        self._vars = dict(window=defaultLevels["lung"])

        # backend
        self._model.imagesChanged.connect(self._on_imagesChanged)
        # menubar
        self._ui.exitAction.triggered.connect(qApp.quit)
        self._ui.openAction.triggered.connect(self._on_openDICOM)
        self._ui.labelAction.triggered.connect(self._on_openLabel)
        self._ui.setWindowAction.triggered.connect(self._on_setWindow)
        # image slice change
        self._ui.imageSpinBox.valueChanged.connect(self._on_changeSlice)
        self._ui.imageSlider.valueChanged.connect(self._on_changeSlice)

    def _setupUi(self):
        self._ui.setupUi(self)
        self._ui.imageDisplay = None # set later in slots
        self._ui.imageScene = QGraphicsScene(self)
        self._ui.imageView.setScene(self._ui.imageScene)

    def _ctAt(self, n: int):
        """
        Convert the n-th (n index is 1 based) CT grayscale
        image to QPixmap
        """
        grayscale = self._model.imageAt(n - 1)
        return QPixmap.fromImage(_toQImage(grayscale))

    @pyqtSlot(int)
    def _on_imagesChanged(self, imagesCount: int):
        self._ui.imageSpinBox.setMaximum(imagesCount)
        self._ui.imageSlider.setMaximum(imagesCount)
        currentIdx = min(self._ui.imageSlider.value(), imagesCount)
        self._on_changeSlice(currentIdx)

    @pyqtSlot()
    def _on_openDICOM(self):
        path = str(QFileDialog.getExistingDirectory(self, "选择DICOM序列所在文件夹"))
        if path:
            self._model.loadScans(path)
            self._vars.update(path=path)

    @pyqtSlot()
    def _on_openLabel(self):
        path = self._vars.get("path", "")
        path, _ = QFileDialog.getOpenFileName(self, "选择标签文件",
                                              path, "nrrd (*.nrrd)")
        path = str(path)
        if path:
            self._model.loadLabels(str(path))

    @pyqtSlot(int)
    def _on_changeSlice(self, index: int):
        if not self._model.loaded():
            return
        # synchronize slider and combobox value
        self._ui.imageSpinBox.setValue(index)
        self._ui.imageSlider.setValue(index)
        # set display image
        pixmap = self._ctAt(index)
        display = self._ui.imageDisplay
        if display is None:
            pixmapItem = self._ui.imageScene.addPixmap(pixmap)
            self._ui.imageDisplay = pixmapItem
        else:
            display.setPixmap(pixmap)
        # reset scene to fit content
        rect = QRectF(.0, .0, pixmap.width(), pixmap.height())
        self._ui.imageView.setSceneRect(rect)

    @pyqtSlot()
    def _on_setWindow(self):
        dialog = WindowDialog(self._model.window(), self)
        if dialog.exec_() == QDialog.Accepted:
            self._model.setWindow(dialog.window())
