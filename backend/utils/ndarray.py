import numpy as np

def z(data, with_index=False):
    for i in range(data.shape[-1]):
        layer = data[:, :, i]
        yield (layer, i) if with_index else layer

def z_if(data, pred=lambda x: True, with_index=False):
    for i in range(data.shape[-1]):
        layer = data[:, :, i]
        if pred(layer):
            yield (layer, i) if with_index else layer

def arg_z(data, pred):
    """get z-axis layers that satisfy pred
    """
    for i in range(data.shape[-1]):
        if pred(data[:, :, i]):
            yield i

def gray(data):
    return np.dstack([data, data, data])

def red(data):
    zeros = np.zeros(data.shape)
    return np.dstack([data, zeros, zeros])
