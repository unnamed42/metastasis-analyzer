import numpy as np

from scipy.ndimage.interpolation import zoom

def filter_scans(scans, labels):
    filtered_scans = []
    filtered_labels = []
    length = scans.shape[-1]
    for i in range(length):
        if not np.any(labels[:, :, i]):
            continue
        filtered_scans.append(scans[:, :, length - i])
        filtered_labels.append(labels[:, :, i])
    return np.dstack(filtered_scans), np.dstack(filtered_labels)

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

def windowing(image, window_level, window_width):
    """
    DICOM windowing
    @param image: numpy array, usually result of get_pixel_hu
    @param window_level: number, window level
    @param window_width: number, window width
    @return: processed image of same size, dtype=np.uint8
    """
    min_visible = np.int16(window_level - (window_width / 2.0))
    max_visible = np.int16(window_level + (window_width / 2.0))
    visible = (image > min_visible) & (image < max_visible)

    ret = np.empty(image.shape, dtype=np.uint8)
    ret[image <= min_visible] = 0
    ret[image >= max_visible] = 255
    ret[visible] = np.interp(image[visible],
                             (min_visible, max_visible),
                             (0, 255)).astype(np.uint8)
    return ret

def resample(images, spacing, new_spacing, order=2):
    new_shape = np.round(images.shape * spacing / new_spacing)
    real_spacing = spacing * images.shape / new_shape
    resize_factor = new_shape / images.shape
    images = zoom(images, resize_factor, mode="nearest", order=order)
    return images, real_spacing
