"""
Slider with value shown. from https://gist.github.com/EricTRocks/2aa65a50f346ad65ec264da189ad0d03
"""
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QFontMetrics
from PyQt5.QtWidgets import QSlider

__stylesheet = """
QSlider::groove:vertical {
        background-color: #222;
        width: 30px;
}
QSlider::handle:vertical {
    border: 1px #438f99;
    border-style: outset;
    margin: -2px 0;
    width: 30px;
    height: 3px;
    background-color: #438f99;
}
QSlider::sub-page:vertical {
    background: #4B4B4B;
}
QSlider::groove:horizontal {
        background-color: #222;
        height: 30px;
}
QSlider::handle:horizontal {
    border: 1px #438f99;
    border-style: outset;
    margin: -2px 0;
    width: 3px;
    height: 30px;
    background-color: #438f99;
}
QSlider::sub-page:horizontal {
    background: #4B4B4B;
}
"""

class Slider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def paintEvent(self, event):
        QSlider.paintEvent(self, event)

        currValue = str(self.value() / 1000.0)
        roundValue = round(float(currValue), 2)

        painter = QPainter(self)
        painter.setPen(QPen(Qt.white))

        fontMetrics = QFontMetrics(self.font())
        boundingRect = fontMetrics.boundingRect(str(roundValue))
        fontWidth = boundingRect.width()
        fontHeight = boundingRect.height()

        rect = self.geometry()
        orientation = self.orientation()
        if orientation == Qt.Horizontal or orientation == Qt.Vertical:
            x = rect.width() - fontWidth - 5
            y = rect.height() * 0.75
            painter.drawText(QPoint(rect.width() / 2.0 - fontWidth / 2.0, rect.height() - 5),
                             str(roundValue))

        painter.drawRect(rect)
