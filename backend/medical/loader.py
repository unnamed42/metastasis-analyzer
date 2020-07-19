import numpy as np

from nrrd import read
from pydicom import read_file

from backend.utils import files

def load_scans(path: str):
    """Load every DICOM scans under directory
    @param path: path to scans
    """
    scans = [read_file(f) for f in files(path)]
    return process_scans(scans)

def process_scans(scans):
    if len(scans) <= 1:
        return scans
    scans.sort(key=lambda s: int(s.InstanceNumber))
    try:
        thick = np.abs(scans[0].ImagePositionPatient[2] - scans[1].ImagePositionPatient[2])
    except AttributeError:
        thick = np.abs(scans[0].SliceLocation - scans[1].SliceLocation)
    for s in scans:
        s.SliceThickness = thick
    return scans

def load_label(path: str):
    labels, options = read(path)
    # nrrd has different indexing order
    labels = np.swapaxes(labels, 0, 1)
    # label order is reversed compared to scans
    return np.flip(labels, 2)

def filter_scans(scans, labels):
    filtered_scans = []
    filtered_labels = []
    if isinstance(scans, list):
        scans = np.dstack(scans)
    length = scans.shape[-1]
    for i in range(length):
        if not np.any(labels[:, :, i]):
            continue
        filtered_scans.append(scans[:, :, i])
        filtered_labels.append(labels[:, :, i])
    return np.dstack(filtered_scans), np.dstack(filtered_labels)
