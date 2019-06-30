"""
Utility functions
"""

from os import walk, listdir, makedirs
from os.path import join, isdir
from errno import EEXIST

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

def first(iterable, pred=lambda x: True):
    try:
        return next(i for i in iterable if pred(i))
    except StopIteration:
        return None

def ls(path, *args, **kwargs):
    return next(walk(path, *args, **kwargs))

def files(path):
    root, _, files = ls(path)
    return [join(root, f) for f in files]

def filenames(path):
    _, _, files = ls(path)
    return files

def mkdir(path):
    try:
        makedirs(path)
    except OSError as e:
        if e.errno == EEXIST and isdir(path):
            pass
        else:
            raise
