import torch
import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtGui import QPixmap, QImage, QKeySequence
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QRectF
from PyQt5.QtWidgets import QMainWindow, QLabel, QHBoxLayout, QDialog, QFileDialog

from .generated.Ui_MainWindow import Ui_MainWindow as Ui
from app.ui.WindowDialog import WindowDialog
from app.ui.MainWindowModel import MainWindowModel as Model
from app.backend.windowLevels import defaultLevels
from app.ct import make_lung_mask, getCAM

def _toQImage(ndarray: np.ndarray) -> QImage:
    """
    8-bit灰度图(numpy格式)转换为QImage
    """
    height, width = ndarray.shape
    # TODO: more memory efficient data passing
    #addr, rw = ndarray.__array_interface__["data"]
    #content = voidptr(addr, writeable=rw)
    content = ndarray.tobytes()
    return QImage(content, width, height, QImage.Format_Grayscale8)

def _toNumpyArray(pixmap: QPixmap) -> np.ndarray:
    """
    取出QPixmap中的图像，转换成numpy数组
    """
    size = pixmap.size()
    h, w = size.width(), size.height()
    image = pixmap.toImage()
    bytesArray = image.bits().tobytes()
    npImage = np.frombuffer(bytesArray, dtype=np.uint8).reshape((w, h, 4))
    return npImage

class CTArray:
    def __init__(self, modelPath: str, window):
        self._model = torch.load(modelPath)


class MainWindow(QMainWindow):
    cutStateChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        window = defaultLevels["lung"]

        self._ui = Ui()
        self._ui.setupUi(self)
        self._model = Model(window)
        self._vars = dict(window=defaultLevels["lung"])
        self._cutState = False

        # backend
        self._model.imagesChanged.connect(self._on_imagesChanged)
        self.cutStateChanged.connect(self._ui.imageView._on_cutStateChanged)
        self._ui.imageView.cutFinished.connect(self._on_predictSelected)

    def _ctAt(self, n: int):
        """
        Convert the n-th (n index is 1 based) CT grayscale
        image to QPixmap
        """
        grayscale = self._model.imageAt(n - 1)
        if self._ui.triggerLungSeg.isChecked():
            mask = make_lung_mask(grayscale)
            print(np.count_nonzero(mask))
            masked = np.where(mask == True, grayscale, 0)
            grayscale = masked
        return QPixmap.fromImage(_toQImage(grayscale))

    def keyPressEvent(self, event):
        if self._ui.imageView.isCutting() and event.matches(QKeySequence.Cancel):
            self.cutStateChanged.emit(False)

    @pyqtSlot()
    def on_predict(self):
        self.cutStateChanged.emit(True)

    @pyqtSlot()
    def _on_predictSelected(self):
        # print("fuck")
        widget = QDialog(self)
        layout = QHBoxLayout(widget)
        widget.setLayout(layout)
        # image = QPixmap("/home/h/thesis/image/result-fuck.png")
        image = self._ui.imageView.selectedImage()
        # image = _toNumpyArray(pixmap)
        # mask = getCAM(self._model.model, image)
        # mask[mask <= 0.6] = 0
        label = QLabel(widget)
        label.setPixmap(image)
        layout.addWidget(label)
        widget.exec_()

    @pyqtSlot(int)
    def _on_imagesChanged(self, imagesCount: int):
        self._ui.imageSpinBox.setMaximum(imagesCount)
        self._ui.imageSlider.setMaximum(imagesCount)
        currentIdx = min(self._ui.imageSlider.value(), imagesCount)
        self.on_sliceChanged(currentIdx)

    @pyqtSlot()
    def on_openDICOM(self):
        path = QFileDialog.getOpenFileName(self, "MHD", ".", "MHD Files (*.mhd)")
        #path = str(QFileDialog.getExistingDirectory(self, "选择DICOM序列所在文件夹"))
        path = str(path[0])
        if not path:
            return
        self._model.loadMHDScans(path)
        self._vars.update(path=path)

    @pyqtSlot()
    def on_openLabel(self):
        path = self._vars.get("path", "")
        path, _ = QFileDialog.getOpenFileName(self, "选择标签文件",
                                              path, "nrrd (*.nrrd)")
        path = str(path)
        if path:
            self._model.loadLabels(str(path))

    @pyqtSlot(int)
    def on_sliceChanged(self, index: int):
        if not self._model.loaded():
            return
        # synchronize slider and combobox value
        self._ui.imageSpinBox.setValue(index)
        self._ui.imageSlider.setValue(index)
        # set display image
        pixmap = self._ctAt(index)
        self._ui.imageView.setImage(pixmap)
        # reset scene to fit content
        rect = QRectF(.0, .0, pixmap.width(), pixmap.height())
        self._ui.imageView.setSceneRect(rect)

    @pyqtSlot()
    def on_setWindow(self):
        dialog = WindowDialog(self._model.window(), self)
        if dialog.exec_() == QDialog.Accepted:
            self._model.setWindow(dialog.window())
