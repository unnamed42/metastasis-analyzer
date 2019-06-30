from PyQt5.QtGui import QImage

from sip import voidptr

def toQImage(data):
    """
    Convert numpy 8-bit grayscale image to QImage
    """
    height, width = data.shape
    # TODO: more memory efficient data passing
    #addr, rw = data.__array_interface__["data"]
    #content = voidptr(addr, writeable=rw)
    content = data.tobytes()
    return QImage(content, width, height, QImage.Format_Grayscale8)
