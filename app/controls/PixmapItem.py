from PyQt5.QtCore import Qt, QRectF, QRect, QEvent, QCoreApplication
from PyQt5.QtGui import QPen, QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from typing import Optional

class PixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap)
        # selection states
        self._cutStart = False
        self._currentPos = None
        self._startPos = None
        self._cutFinish = False

        # QCoreApplication.instance().installEventFilter(self)

    def _on_cutStateChanged(self, cutStart: bool):
        self._cutStart = cutStart
        cursor = Qt.ArrowCursor if cutStart else Qt.CrossCursor
        self.setCursor(cursor)

    # def mousePressEvent(self, event):
    #     if event.button() != Qt.LeftButton:
    #         super().mousePressEvent(event)
    #         return
    #     self._startPos = event.pos()
    #     if self._currentPos:
    #         self._currentPos = None
    #     print("pressed")
    #     self.update()
    #     event.accept()
    def eventFilter(self, event: QEvent):
        if event.type() == QEvent.MouseMove:
            self.mouseMoveHandler(event)

    def mouseMoveHandler(self, event):
        print(event.buttons())
        if event.buttons() != Qt.LeftButton:
            # super().mouseMoveEvent(event)
            return
        if not self._startPos:
            self._startPos = event.pos()
        else:
            self._currentPos = event.pos()
        print("moved")
        self.update()
        event.accept()

    # def mouseMoveEvent(self, event):
    #     self._currentPos = event.pos()
    #     if not self._cutStart or self._isMidButton:
    #         self.moveBy(self._currentPos.x() - self._startPos.x(),
    #                     self._currentPos.y() - self._startPos.y())
    #         self._cutFinish = False
    #     self.update()

    # def mousePressEvent(self, event):
    #     super().mousePressEvent(event)
    #     self._startPos = event.pos()
    #     self._currentPos = None
    #     self._cutFinish = False
    #     self._isMidButton = event.button() == Qt.MidButton
    #     self.update()

    def paint(self, painter, style, widget):
        super().paint(painter, style, widget)
        if not self._cutStart or not self._currentPos or not self._startPos:
            return
        pen = QPen(Qt.SolidLine)
        pen.setColor(QColor(0, 0, 255))
        pen.setWidth(4)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 255, 70))
        painter.drawRect(QRectF(self._startPos, self._currentPos))
        self._cutFinish = True

    def selectedArea(self) -> Optional[QPixmap]:
        if not self._startPos or not self._currentPos:
            return None
        area = QRect(self._startPos.toPoint(), self._currentPos.toPoint())
        return self.pixmap().copy(area)
