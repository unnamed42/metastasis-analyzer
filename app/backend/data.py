import numpy as np

from pydicom import read_file
from nrrd import read

from app.backend.utils import files

def load_scans(path: str):
    scans = [read_file(f) for f in files(path)]
    if len(scans) <= 1:
        return scans
    scans.sort(key=lambda s: int(s.InstanceNumber))
    try:
        thickness = np.abs(scans[0].ImagePositionPatient[2] - scans[1].ImagePositionPatient[2])
    except AttributeError:
        thickness = np.abs(scans[0].SliceLocation - scans[1].SliceLocation)

    for s in scans:
        s.SliceThickness = thickness
    return scans

def load_labels(path: str):
    labels, options = read(path)
    # nrrd has different indexing order
    labels = np.swapaxes(labels, 0, 1)
    return labels.astype(bool)

def get_spacing(scan):
    return np.array([scan.SliceThickness] + scan.PixelSpacing, dtype=np.float32)
