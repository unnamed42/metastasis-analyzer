import numpy as np

from typing import Tuple

from matplotlib import pyplot as plt

def _array(mask, fill):
    zero = np.zeros(mask.shape, dtype=np.uint8)
    zero[mask] = fill
    return zero

def colored(data, color: Tuple[int, int, int]):
    r, g, b = color
    data = data.astype(bool)
    return np.dstack([_array(data, r), _array(data, g), _array(data, b)])

def red(data):
    return colored(data, (255, 0, 0))

def white(data):
    return colored(data, (255, 255, 255))

def gray(data):
    return np.dstack([data, data, data])

def toGray(data):
    return np.interp(data, (data.min(), data.max()),
                     (0, 255)).astype(np.uint8)

def layer(images, idx: int):
    image = images[:, :, idx]
    if not np.issubdtype(image.dtype, np.uint8):
        image = toGray(image)
    plt.figure()
    plt.axis("off")
    plt.imshow(image, cmap="gray")

def overlay(ct, label, alpha=0.4):
    plt.figure()
    plt.axis("off")
    plt.imshow(gray(ct), cmap="gray")
    plt.imshow(red(label), alpha=alpha)

def series(images, figsize=[12, 12], start_with=0, show_every=1):
    """
    Visualize this series of scans
    @param images: pixel array of DICOM scans
    @param rows: rows of displayed image matrix
    @param cols: columns of displayed image matrix
    @param start_with: display images start with index
    @param show_every: display every n image
    """
    z = images.shape[-1]
    rows = floor(sqrt((z - start_with) / show_every))

    fig, ax = plt.subplots(rows, rows, figsize=figsize)
    for i in range(rows * rows):
        idx = start_with + show_every * i
        if idx >= z:
            break
        plot = ax[int(i / rows), int(i % rows)]
        plot.set_title("slice {}".format(idx))
        plot.imshow(images[:, :, idx], cmap="gray")
        plot.axis("off")
    plt.show()
