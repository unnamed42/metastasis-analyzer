from os import walk, listdir, makedirs
from os.path import join, isdir
from errno import EEXIST

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

