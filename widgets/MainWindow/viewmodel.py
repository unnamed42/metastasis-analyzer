import cv2
import numpy as np

from typing import Tuple

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt5.QtGui import QPainter, QPen, QFont, QImage, QPixmap, QBrush, qRgba

from backend.medical import defaultLevels, make_lung_mask, load_label, windowing, crop
from backend.utils import Cache
from backend.threading import onceTask, CTLoader
from backend.cnn import model, heatmapAndProb, GBPAndProb

_DEFAULT = defaultLevels["lung"]

def _QImageOverlay(background, foreground):
    image = QImage(background.size(), QImage.Format_ARGB32_Premultiplied)
    painter = QPainter(image)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.fillRect(image.rect(), Qt.transparent)
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    painter.fillRect(background.rect(), QBrush(background))
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    painter.fillRect(foreground.rect(), QBrush(foreground))
    painter.end()
    return image

def _QImageWriteText(image, text):
    painter = QPainter(image)
    painter.setPen(QPen(Qt.red))
    painter.setFont(QFont("Sans", 10, QFont.Bold))
    painter.drawText(0, 12, text)
    painter.end()
    return image

def _imageCvt(source, idx: int):
    if not source.loaded:
        return QPixmap()
    data = source._imageAt(idx)
    # TODO: data passing without copying
    # TODO: convert 8bit grayscale to 24bit to avoid format incompatibilities
    image = QImage(data.tobytes(), *data.shape[::-1], QImage.Format_Grayscale8)
    return QPixmap.fromImage(image)

def _labelCvt(source, idx: int):
    if not source.labelsLoaded:
        return QPixmap()
    label = source._labelAt(idx)
    nonzero = np.transpose(np.nonzero(label))
    if nonzero.size == 0:
        return QPixmap()
    image = QImage(*label.shape[::-1], QImage.Format_ARGB32)
    image.fill(0)
    # set pixels for each non-zero position
    # transformation is very slow if we calculate for each pixel
    for (row, col) in nonzero:
        # should be bool
        value = label[row, col]
        # alpha = 0.4 e.g. 102
        pixel = qRgba(value * 255, 0, 0, 102 if value else 0)
        # why are they np.int64?
        image.setPixel(col.item(), row.item(), pixel)
    return QPixmap.fromImage(image)

def _maskCvt(source, idx: int):
    if not source.loaded:
        return QPixmap()
    data = source._imageAt(idx)
    mask = make_lung_mask(data)
    image = QImage(*data.shape[::-1], QImage.Format_ARGB32)
    image.fill(qRgba(0, 0, 0, 255)) # black background
    pixel = qRgba(0, 0, 0, 0) # transparent background
    for (row, col) in np.transpose(np.nonzero(mask)):
        image.setPixel(col.item(), row.item(), pixel)
    return QPixmap.fromImage(image)

def _heatmapCvt(source, idx: int, mode="gradcam"):
    if not source.loaded or not source.labelsLoaded or not source.cnnLoaded:
        return QPixmap()
    label = source._labelAt(idx)
    if not np.any(label):
        return QPixmap()
    data = source._imageAt(idx)
    roi = cv2.resize(crop(data, label), (64, 64))
    if mode == "gradcam":
        heat, prob = heatmapAndProb(source._cnn, np.dstack([roi] * 3), 0.5)
    elif mode == "gbp":
        heat, prob = GBPAndProb(source._cnn, np.dstack([roi] * 3))
    # visualize results
    if mode == "gradcam":
        heat = cv2.resize(heat, (64, 64))
    im1 = QImage(roi.tobytes(), *roi.shape[::-1], QImage.Format_Grayscale8)
    if mode == "gbp":
        heat = np.require(heat, np.uint8, "C")
    im2 = QImage(heat, heat.shape[1], heat.shape[0], QImage.Format_RGBA8888)
    image = _QImageOverlay(im1, im2)

    cv2.imwrite(f"/home/h/explain/roi-{idx}.png", roi)
    if mode == "gradcam":
        image.save(f"/home/h/explain/{mode}-{idx}.png")
    elif mode == "gbp":
        cv2.imwrite(f"/home/h/explain/{mode}-{idx}.png", heat)

    image = _QImageWriteText(image, "p=%.3f" % prob)
    return QPixmap.fromImage(image)

def _heatmapGeneration(image, mode="gradcam"):
    if not image:
        return QPixmap()
    roi = cv2.resize(image, (64, 64))
    if mode == "gradcam":
        heat, prob = heatmapAndProb(source._cnn, np.dstack([roi] * 3), 0.5)
    elif mode == "gbp":
        heat, prob = GBPAndProb(source._cnn, np.dstack([roi] * 3))
    # visualize results
    if mode == "gradcam":
        heat = cv2.resize(heat, (64, 64))
    im1 = QImage(roi.tobytes(), *roi.shape[::-1], QImage.Format_Grayscale8)
    if mode == "gbp":
        heat = np.require(heat, np.uint8, "C")
    im2 = QImage(heat, heat.shape[1], heat.shape[0], QImage.Format_RGBA8888)
    image = _QImageOverlay(im1, im2)

    cv2.imwrite(f"/home/h/explain/roi-{idx}.png", roi)
    if mode == "gradcam":
        image.save(f"/home/h/explain/{mode}-{idx}.png")
    elif mode == "gbp":
        cv2.imwrite(f"/home/h/explain/{mode}-{idx}.png", heat)

    image = _QImageWriteText(image, "p=%.3f" % prob)
    return QPixmap.fromImage(image)

class ViewModel(QObject):
    # images size changed
    imagesChanged = pyqtSignal(int)

    def __init__(self, window: Tuple[int, int] = _DEFAULT):
        super().__init__()

        # CT stats
        self._path = ""
        self._window = window
        # for less memory consumption and faster startup
        self._cacheImg = Cache(self, _imageCvt)
        self._cacheLbl = Cache(self, _labelCvt)
        self._cacheMsk = Cache(self, _maskCvt)
        self._cacheCAM = Cache(self, lambda source, idx: _heatmapCvt(source, idx, "gradcam"))
        self.imagesChanged.connect(self._resetCache)
        # async CT loader
        self.ctLoader = CTLoader()
        self.ctLoader.callback(self._scansLoaded)
        # asynchronously load model
        task = onceTask(self, model)
        task.callback(lambda cnn : setattr(self, "_cnn", cnn))
        task.start()

    def loadScans(self, path: str):
        self._path = path
        self.ctLoader.setPath(path)
        self.ctLoader.start()

    def loadLabels(self, path: str):
        self._labels = load_label(path)
        self._cacheLbl.reset(len(self))
        # return the first labeled slice, 0-based index
        for i in range(self._labels.shape[-1]):
            if np.any(self._labels[:, :, i]):
                return i
        # should not be possible
        return -1

    def heatmap(self, selection):
        return _heatmapGeneration(selection)

    @pyqtSlot(object)
    def _scansLoaded(self, result):
        (hu, spacing) = result
        self._hu = hu
        self._spacing = spacing
        self._labels = None
        self.imagesChanged.emit(len(self))

    """
    Data access for internal use
    """

    def _imageAt(self, idx: int):
        item = self._hu[:, :, idx]
        if self._window == (0, 0):
            return np.interp(item, (-2000, 2000), (0, 255)).astype(np.uint8)
        else:
            return windowing(item, *self._window)

    def _labelAt(self, idx: int):
        return self._labels[:, :, idx]

    """
    Data access for GUI display
    """

    def imageAt(self, idx: int):
        return self._cacheImg[idx]

    def labelAt(self, idx: int):
        return self._cacheLbl[idx]

    def maskAt(self, idx: int):
        return self._cacheMsk[idx]

    def heatmapAt(self, idx: int):
        return self._cacheCAM[idx]

    @pyqtSlot(int)
    def _resetCache(self, length: int):
        self._cacheImg.reset(length)
        self._cacheMsk.reset(length)
        self._cacheCAM.reset(length)

    @pyqtProperty(tuple)
    def window(self):
        return self._window

    @window.setter
    def window(self, window: Tuple[int, int]):
        if self._window != window:
            self._window = window
            self.imagesChanged.emit(len(self))

    @pyqtProperty(bool)
    def loaded(self):
        return self._hu is not None

    @pyqtProperty(bool)
    def labelsLoaded(self):
        return self._labels is not None

    @pyqtProperty(bool)
    def cnnLoaded(self):
        return self._cnn is not None

    def canTakeHeatmap(self, idx):
        if not (self.loaded and self.labelsLoaded and self.cnnLoaded):
            return False
        label = self._labelAt(idx)
        return np.any(label)

    @pyqtProperty(str)
    def path(self):
        return self._path

    @pyqtProperty(list)
    def spacing(self):
        return self._spacing

    def __len__(self):
        hu = self._hu
        return hu.shape[-1] if hu is not None else 0
