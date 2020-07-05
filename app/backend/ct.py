import numpy as np

from nrrd import read
from pydicom import read_file

from sklearn.cluster import KMeans
from skimage.measure import label, regionprops
from skimage.morphology import erosion, dilation, remove_small_objects
from scipy.ndimage.interpolation import zoom

from app.backend.utils import files, z

def _z_score(data):
    return (data - data.mean()) / data.std()

def load_scans(path: str):
    """Load every DICOM scans under directory
    @param path: path to scans
    """
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

def load_label(path: str):
    labels, options = read(path)
    # nrrd has different indexing order
    labels = np.swapaxes(labels, 0, 1)
    return labels.astype(bool)

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

def spacing(dicom):
    params = list(dicom.PixelSpacing) + [dicom.SliceThickness]
    return np.array(params, dtype=np.float32)

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
    visible = (data > min_visible) & (data < max_visible)

    ret = np.empty(data.shape, dtype=np.uint8)
    ret[data <= min_visible] = 0
    ret[data >= max_visible] = 255
    ret[visible] = np.interp(data[visible],
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

def make_lung_mask(image, crop=True):
    """Mask lung region for the given slice
    @param image: np.array, one slice of lung CT
    @return: mask image, np.array(dtype=bool) of same shape
    """
    rows = image.shape[0]
    cols = image.shape[1]
    image = _z_score(image)

    if crop:
        middle = image[int(cols/5):int(cols/5*4), int(rows/5):int(rows/5*4)]
    else:
        middle = image
    mean = np.mean(middle)
    image[image == np.min(image)] = mean
    image[image == np.max(image)] = mean

    kmeans = KMeans(n_clusters=2).fit(np.reshape(middle, [np.prod(middle.shape), 1]))
    centers = sorted(kmeans.cluster_centers_.flatten())
    threshold = np.mean(centers)
    thres_image = np.where(image < threshold, 1.0, 0.0)

    eroded = erosion(thres_image, np.ones([3, 3]))
    dilated = dilation(eroded, np.ones([8, 8]))
    labels = label(dilated)

    good_labels = []
    for prop in regionprops(labels):
        b = prop.bbox
        if b[2] - b[0] < rows/10*9 and b[3] - b[1] < cols/10*9 and b[0] > rows/5 and b[2] < cols/5*4:
            good_labels.append(prop.label)

    mask = np.ndarray([rows, cols], dtype=np.int8)
    mask[:] = 0
    for n in good_labels:
        mask += np.where(labels == n, 1, 0)
    mask = dilation(mask, np.ones([10, 10]))
    return remove_small_objects(mask.astype(bool), min_size=1600)

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
