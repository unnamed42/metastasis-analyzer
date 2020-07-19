import numpy as np

from sklearn.cluster import KMeans
from skimage.measure import label, regionprops
from skimage.morphology import erosion, dilation, remove_small_objects

from backend.medical import z_score

def make_lung_mask(image):
    """Mask lung region for the given slice
    @param image: np.array, one slice of lung CT
    @return: mask image, np.array(dtype=bool) of same shape
    """
    rows = image.shape[0]
    cols = image.shape[1]
    image = z_score(image)

    middle = image[int(cols/5):int(cols/5*4), int(rows/5):int(rows/5*4)]
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
