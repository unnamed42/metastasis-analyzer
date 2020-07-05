import numpy as np

from skimage.measure import label, regionprops

def z_score(data):
    return (data - data.mean()) / data.std()

def windowing(hu_array, window_level=-400, window_width=1500):
    """
    DICOM windowing
    @param hu_array: numpy array, usually result of get_pixel_hu
    @param window_level: number, window level
    @param window_width: number, window width
    @return: processed hu_array of same size, dtype=np.uint8
    """
    min_visible = np.int16(window_level - (window_width / 2.0))
    max_visible = np.int16(window_level + (window_width / 2.0))
    visible = (hu_array > min_visible) & (hu_array < max_visible)

    ret = np.empty(hu_array.shape, dtype=np.uint8)
    ret[hu_array <= min_visible] = 0
    ret[hu_array >= max_visible] = 255
    ret[visible] = np.interp(hu_array[visible],
                             (min_visible, max_visible),
                             (0, 255)).astype(np.uint8)
    return ret

def resample(images, spacing, new_spacing=(1, 1, 1)):
    """Resample HU images to new spacing, by default is [1, 1, 1]
    @param images: HU values
    @param spacing: original DICOM spacing
    @param new_spacing: new spacing resampled to, [pixel_spacing_x, pixel_spacing_y, slice_thickness]
    """
    spacing = np.array(list(spacing))
    new_spacing = np.array(list(new_spacing))

    resize_factor = spacing / new_spacing
    new_real_shape = images.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / images.shape
    new_spacing = spacing / real_resize_factor

    images = zoom(images, real_resize_factor)
    return images

def normalize(images):
    """
    Normalize image for further use

    @param image: tumor CT image, np.array shape=(any, any), dtype=float
    @return: normalized image, np.array shape=(64, 64), dtype=float
    """
    # do z-score normalization first
    z_score = _z_score(images)
    # get shape to calc zoom factor
    shape = np.array(images.shape)
    new_shape = np.array([64, 64, images.shape[-1]])
    # invoke zoom, by default 3rd order interpolation
    return zoom(z_score, new_shape / shape)

def crop_one(scan, label_):
    regions = regionprops(label(label_))
    minr, minc, maxr, maxc = regions[0].bbox
    # reshape bounding box to bounding square
    width = maxc - minc
    height = maxr - minr
    diff = abs(width - height)
    if width < height:
        maxc += diff
    elif width > height:
        maxr += diff
    return normalize(scan[minr:maxr, minc:maxc])

def crop(scans, labels):
    """Crop appropriate cube for training and testing
    @param scans: all labeled CT scans, np.array
    @param labels: labels, np.array(dtype=bool)
    @return: np.array(shape=(64, 64, ?))
    """
    # merge all labels into one
    merged = np.sum(labels, axis=2).astype(bool)
    regions = regionprops(label(merged))
    minr, minc, maxr, maxc = regions[0].bbox
    # reshape bounding box to bounding square
    width = maxc - minc
    height = maxr - minr
    diff = abs(width - height)
    if width < height:
        maxc += diff
    elif width > height:
        maxr += diff
    # rescale into 64x64xN cubes
    return normalize(scans[minr:maxr, minc:maxc, :])

# CT window levels, tuple (window level, window width)
# from https://www.radiantviewer.com/dicom-viewer-manual/change_brightness_contrast.htm
window_levels_1 = {
    "bone": (300, 1500),
    "lung": (-400, 1500),
    "brain": (40, 80),
    "chest": (40, 400)
}

# another CT window settings, from
# https://radiopaedia.org/articles/windowing-ct#nav_typical-window-width-and-level-values
window_levels_2 = {
    "bone": (400, 1800),
    "lung": (-600, 1500),
    "brain": (40, 80),
    "chest": (50, 350)
}

# even another CT window settings, from
# www.sohu.com/a/112237736_416084
window_levels_3 = {
    "bone": (600, 1400),
    "lung": (-600, 700),
    "brain": (35, 60),
    "chest": (0, 350)
}
