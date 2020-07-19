import numpy as np

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot, Qt, QRectF
from PyQt5.QtWidgets import (QMainWindow, qApp, QWidget, QHBoxLayout, QLabel,
                             QGraphicsScene, QProgressBar,
                             QDialog, QFileDialog, QMessageBox)

from imageio import imread

from widgets import WindowDialog
from backend.threading import Task, Tasks

from .ui import Ui_MainWindow as Ui
from .viewmodel import ViewModel

def imageShow(ctx, image):
    widget = QDialog(ctx)
    layout = QHBoxLayout(widget)
    widget.setLayout(layout)
    label = QLabel(widget)
    label.setPixmap(image)
    layout.addWidget(label)
    widget.exec_()

def _toNumpyArray(pixmap: QPixmap) -> np.ndarray:
    """
    取出QPixmap中的图像，转换成numpy数组
    """
    #size = pixmap.size()
    #h, w = size.width(), size.height()
    #image = pixmap.toImage()
    #image.bits()
    #print(image.bits() is None)
    #bytesArray = image.bits().tobytes()
    #npImage = np.frombuffer(bytesArray, dtype=np.uint8).reshape((w, h, 4))
    #return npImage
    pixmap.save("/home/h/tmp.png", "PNG")
    image = imread("/home/h/tmp.png")
    return image

class View(QMainWindow):
    def __init__(self):
        super().__init__()

        self._ui = Ui()
        self._ctx = ViewModel()
        self._ui.setupUi(self)
        self._moreUi()
        self._tasks = Tasks()
        # backend
        self._ctx.imagesChanged.connect(self._on_imagesChanged)
        # statusbar
        self._ctx.ctLoader.amountChanged.connect(self._on_loaderAmountChanged)
        self._ctx.ctLoader.progressChanged.connect(self._on_loaderProgressChanged)
        self._ctx.ctLoader.result.connect(self._on_loaderDone)
        # displayed items
        self._ui.labelChecked.toggled.connect(lambda on: self._ui.labelDisplay.setVisible(on))
        self._ui.maskChecked.toggled.connect(lambda on: self._ui.maskDisplay.setVisible(on))
        self._ui.predictChecked.toggled.connect(lambda on: self._ui.heatmapDisplay.setVisible(on))

    def _moreUi(self):
        # image display area
        scene = self._ui.imageView.scene
        self._ui.imageScene = scene
        self._ui.imageView.setScene(self._ui.imageScene)
        self._ui.imageDisplay = scene.addPixmap(QPixmap())
        self._ui.labelDisplay = scene.addPixmap(QPixmap())
        self._ui.maskDisplay  = scene.addPixmap(QPixmap())
        self._ui.heatmapDisplay = scene.addPixmap(QPixmap())
        self._ui.heatmapDisplay.setZValue(20)
        self._ui.labelDisplay.setZValue(15)
        self._ui.maskDisplay.setZValue(10)
        # status bar
        self._ui.progressBar = QProgressBar()
        self._ui.progressBar.setTextVisible(False)
        self._ui.progressBar.setMinimum(0)
        self.statusBar().addPermanentWidget(self._ui.progressBar)
        self._ui.progressBar.hide()

    @pyqtSlot(int)
    def _on_loaderAmountChanged(self, amount: int):
        self._ui.progressBar.setMaximum(amount)
        self._ui.progressBar.show()

    @pyqtSlot(int)
    def _on_loaderProgressChanged(self, progress: int):
        message = f"已加载文件 {progress}/{self._ui.progressBar.maximum()}"
        self._ui.progressBar.setValue(progress)
        self.statusBar().showMessage(message)

    @pyqtSlot()
    def _on_loaderDone(self):
        self._ui.progressBar.hide()
        self.statusBar().clearMessage()

    @pyqtSlot(int)
    def _on_imagesChanged(self, imagesCount: int):
        self._ui.imageSpinBox.setMaximum(imagesCount)
        self._ui.imageSlider.setMaximum(imagesCount)
        currentIdx = min(self._ui.imageSlider.value(), imagesCount)
        self.sliceChanged(currentIdx)

    @pyqtSlot()
    def openDICOM(self):
        path = str(QFileDialog.getExistingDirectory(self, "选择DICOM序列所在文件夹"))
        if not path:
            return
        self._ctx.loadScans(path)

    @pyqtSlot()
    def openLabel(self):
        path = self._ctx.path
        path, _ = QFileDialog.getOpenFileName(self, "选择标签文件",
                                              path, "nrrd (*.nrrd)")
        if not path:
            return
        self._ctx.loadLabels(path)

    @pyqtSlot(int)
    def sliceChanged(self, index: int):
        if not self._ctx.loaded:
            return
        self._ui.imageView.clear()
        # synchronize slider and combobox value
        # do not trigger valueChanged
        self._ui.imageSpinBox.blockSignals(True)
        self._ui.imageSlider.blockSignals(True)
        self._ui.imageSpinBox.setValue(index)
        self._ui.imageSlider.setValue(index)
        self._ui.imageSpinBox.blockSignals(False)
        self._ui.imageSlider.blockSignals(False)
        index = index - 1
        # set display image
        pixmap = self._ctx.imageAt(index)
        self._ui.imageDisplay.setPixmap(pixmap)
        # set label image
        if self._ctx.labelsLoaded and self._ui.labelChecked.isChecked():
            label = self._ctx.labelAt(index)
            self._ui.labelDisplay.setPixmap(label)
        # set mask image
        if self._ctx.loaded and self._ui.maskChecked.isChecked():
            mask = self._ctx.maskAt(index)
            self._ui.maskDisplay.setPixmap(mask)
        if self._ui.predictChecked.isChecked():
            # infinity progress
            self._ui.progressBar.setMaximum(0)
            self._ui.progressBar.setValue(0)
            self._ui.progressBar.show()
            self.statusBar().showMessage("计算中")
            self.centralWidget().setEnabled(False)
            # calculate in background thread
            task = self._tasks.create(self._ctx.heatmapAt, index)
            task.callback(self._on_predictCalculated)
            task.start()
        # reset scene to fit content
        rect = QRectF(.0, .0, pixmap.width(), pixmap.height())
        self._ui.imageView.setSceneRect(rect)

    @pyqtSlot()
    def cropped(self):
        index = self._ui.imageSpinBox.value() - 1
        self._ui.progressBar.setMaximum(0)
        self._ui.progressBar.setValue(0)
        self._ui.progressBar.show()
        self.statusBar().showMessage("计算中")
        self.centralWidget().setEnabled(False)
        task = self._tasks.create(self._ctx.heatmapAt, index)
        task.callback(self._on_predictCalculated)
        task.start()

    @pyqtSlot(object)
    def _on_predictCalculated(self, heatmap: QPixmap):
        self.centralWidget().setEnabled(True)
        self.statusBar().clearMessage()
        self._ui.progressBar.hide()
        if heatmap is not None:
            imageShow(self, heatmap)

    @pyqtSlot()
    def showSetWindow(self):
        dialog = WindowDialog(self._ctx.window, self)
        if dialog.exec_() == QDialog.Accepted:
            self._ctx.window = dialog.window()
