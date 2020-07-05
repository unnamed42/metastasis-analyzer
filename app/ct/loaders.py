import numpy as np

from nrrd import read
from pydicom import read_file

import SimpleITK as sitk

from app.backend.utils import files

def _dicom_spacing(dicom):
    params = list(dicom.PixelSpacing) + [dicom.SliceThickness]
    return np.array(params, dtype=np.float32)

def load_dicom(path: str):
    """将位于 path 下的所有DICOM序列文件读入成为完整的CT序列。要求所有DICOM确实
    属于同一个序列。
    @param path: path to scans
    @return: CT序列, CT像素大小
    """
    scans = [read_file(f) for f in files(path)]
    if len(scans) <= 1:
        return scans
    scans.sort(key=lambda s: int(s.InstanceNumber))
    try:
        thickness = np.abs(scans[0].ImagePositionPatient[2] - scans[1].ImagePositionPatient[2])
    except AttributeError:
        thickness = np.abs(scans[0].SliceLocation - scans[1].SliceLocation)

    if len(scans) == 0:
        return [], (0,0,0)

    for s in scans:
        s.SliceThickness = thickness
    spacing = _dicom_spacing(scans[0])
    return scans, spacing

def load_mhd(path: str):
    """将位于 path 的mhd和raw代表的CT序列读入。
    @return: CT序列, CT像素大小
    """
    mhd = sitk.ReadImage(path)
    scans = sitk.GetArrayFromImage(mhd)
    spacing = tuple(reversed(mhd.GetSpacing()))

    return scans, spacing
