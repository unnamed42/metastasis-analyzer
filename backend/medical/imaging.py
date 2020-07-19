import numpy as np

from scipy.ndimage.interpolation import zoom

def z_score(data):
    return (data - data.mean()) / data.std()

def resample(images, spacing, new_spacing=(1, 1, 1)):
    """Resample image series to new spacing, by default is [1, 1, 1]
    @param images: 3D numpy array
    @param spacing: original spacing
    @param new_spacing: new spacing resampled to, [pixel_spacing_x, pixel_spacing_y, pixel_spacing_z]
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

    @param image: np.array shape=(any, any), dtype=float
    @return: normalized image, np.array shape=(64, 64), dtype=float
    """
    # do z-score normalization first
    zscore = z_score(images)
    # get shape to calc zoom factor
    shape = np.array(images.shape)
    new_shape = np.array([64, 64, images.shape[-1]])
    # invoke zoom, by default 3rd order interpolation
    return zoom(zscore, new_shape / shape)
