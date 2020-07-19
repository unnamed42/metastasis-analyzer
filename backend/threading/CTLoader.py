import numpy as np

from pydicom import read_file

from PyQt5.QtCore import pyqtSignal

from backend.utils import files
from backend.medical import process_scans, get_pixel_hu
from backend.threading import Task

def _spacing(scan):
    space = list(scan.PixelSpacing) + [scan.SliceThickness]
    return tuple(float(v) for v in space)

class CTLoader(Task):
    amountChanged = pyqtSignal(int)
    progressChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__(self._execute)

    def setPath(self, path: str):
        self._path = path

    def _execute(self):
        total = files(self._path)
        self.amountChanged.emit(len(total))
        scans = []
        for (idx, path) in enumerate(total):
            dicom = read_file(path)
            dicom.pixel_hu = get_pixel_hu(dicom)
            scans.append(dicom)
            self.progressChanged.emit(idx + 1)
        scans = process_scans(scans)
        spacing = _spacing(scans[0])
        hu = np.dstack([scan.pixel_hu for scan in scans])
        return (hu, spacing)
