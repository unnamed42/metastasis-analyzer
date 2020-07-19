import numpy as np

from skimage.measure import regionprops, label

from backend.utils import z
from backend.medical import z_score

def get_pixel_hu(scan):
    """
    Convert pydicom scan to CT HU values,
    using the relationship: FinalPixel = RawPixel * Slope + Intercept
    @param pixels: one scan of pydicom
    @return: numpy array of same size, dtype=numpy.int16
    """
    image = scan.pixel_array.astype(np.int16)
    image[image == -2000] = 0

    intercept = scan.RescaleIntercept
    slope = scan.RescaleSlope
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)
    image += np.int16(intercept)
    return image

def scans_to_hu(scans):
    return np.dstack([get_pixel_hu(s) for s in scans])

def windowing(data, window_level, window_width):
    """
    DICOM windowing
    @param data: numpy array, usually result of get_pixel_hu
    @param window_level: number, window level
    @param window_width: number, window width
    @return: processed data of same size, dtype=np.uint8
    """
    min_visible = np.int16(window_level - (window_width / 2.0))
    max_visible = np.int16(window_level + (window_width / 2.0))

    black = data <= min_visible
    white = data >= max_visible
    visible = ~black & ~white

    ret = np.empty(data.shape, dtype=np.uint8)
    ret[black] = 0
    ret[white] = 255
    ret[visible] = np.interp(data[visible],
                             (min_visible, max_visible),
                             (0, 255)).astype(np.uint8)
    return ret

def crop(scans, labels):
    """Crop appropriate cube for training and testing
    @param scans: all labeled CT scans, np.array
    @param labels: labels, np.array(dtype=bool)
    @return: np.array(shape=(64, 64, ?))
    """
    if len(labels.shape) == 3:
        merged = np.sum(labels, axis=2).astype(bool)
        region = regionprops(label(merged))
    else:
        region = regionprops(label(labels))
    # reshape bounding box to bounding square
    minr, minc, maxr, maxc = region[0].bbox
    width = maxc - minc
    height = maxr - minr
    diff = abs(width - height)
    if width < height:
        maxc += diff
    elif width > height:
        maxr += diff
    # return scan(s) according to labels shape
    if len(labels.shape) == 3:
        return scans[minr:maxr, minc:maxc, :]
    else:
        return scans[minr:maxr, minc:maxc]
