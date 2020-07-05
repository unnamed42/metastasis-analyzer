import numpy as np
import gc
import torch

from typing import Tuple

from PyQt5.QtCore import QObject, pyqtSignal

from app.backend import ct
from app.backend.utils import z
from app.ct.loaders import load_mhd

def _spacing(scan):
    space = list(scan.PixelSpacing) + [scan.SliceThickness]
    return tuple(float(v) for v in space)

class MainWindowModel(QObject):
    imagesChanged = pyqtSignal(int)

    def __init__(self, window: Tuple[int, int], path: str = None):
        super().__init__()

        self._wl, self._ww = window

        self._labels = None
        if path is not None:
            self.loadScans(path)
        else:
            self._images = None
            self._spacing = None
        self._model = torch.load("/home/h/ma/data/model.pt")
        self._model.eval()
        self._model.cpu()

    def loadDICOMScans(self, path: str):
        scans = ct.load_scans(path)
        self._hu = np.dstack([ct.get_pixel_hu(s) for s in scans])
        self._spacing = _spacing(scans[0])
        self._rewindow()

    def loadMHDScans(self, path: str):
        scans, spacing = load_mhd(path)
        self._hu = np.dstack(scans)
        self._spacing = spacing
        self._rewindow()

    def loadLabels(self, path: str):
        if not self.loaded():
            return
        labels = ct.load_label(path)
        images, labels = ct.filter_scans(self._images, labels)
        self._images = images
        self._labels = labels
        self.imagesChanged.emit(len(self))
        gc.collect()

    def _rewindow(self):
        """
        Reperform windowing.
        """
        if self._wl != 0 and self._ww != 0:
            windowed = (ct.windowing(h, self._wl, self._ww) for h in z(self._hu))
        else:
            windowed = (ct.as_grayscale(h) for h in z(self._hu))
        self._images = np.dstack(list(windowed))
        self.imagesChanged.emit(len(self))
        gc.collect()

    def imageAt(self, index: int):
        return self._images[:, :, index]

    def labelAt(self, index: int):
        return self._labels[:, :, index]

    def window(self):
        return (self._wl, self._ww)

    def setWindow(self, window: Tuple[int, int]):
        self._wl, self._ww = window
        self._rewindow()

    def __len__(self):
        return self._images.shape[-1] if self.loaded() else 0

    def loaded(self):
        return self._images is not None

    def spacing(self):
        return self._spacing
