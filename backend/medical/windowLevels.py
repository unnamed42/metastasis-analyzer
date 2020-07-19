# CT window levels, tuple (window level, window width)
# from https://www.radiantviewer.com/dicom-viewer-manual/change_brightness_contrast.htm
windowLevels1 = {
    "bone": (300, 1500),
    "lung": (-400, 1500),
    "brain": (40, 80),
    "chest": (40, 400)
}

# another CT window settings, from
# https://radiopaedia.org/articles/windowing-ct#nav_typical-window-width-and-level-values
windowLevels2 = {
    "bone": (400, 1800),
    "lung": (-600, 1500),
    "brain": (40, 80),
    "chest": (50, 350)
}

# even another CT window settings, from
# www.sohu.com/a/112237736_416084
windowLevels3 = {
    "bone": (600, 1400),
    "lung": (-600, 700),
    "brain": (35, 60),
    "chest": (0, 350)
}

defaultLevels = windowLevels1
