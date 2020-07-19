from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, pyqtProperty, QRectF, QRect
from PyQt5.QtGui import QPixmap, QColor, QPen, QPainter, QBrush
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QApplication

from typing import Optional

_SELECTED_BTN = Qt.RightButton

class GraphicsView(QGraphicsView):

    cutFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.viewport().setMouseTracking(True)
        # Set Anchors
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        # image scene and item
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setImage(QPixmap())
        self._pixmap.setZValue(-1)
        self.clear()

    def clear(self):
        self._rect = None
        self._cutStart = False
        self._startPos = None
        self._currentPos = None
        if self._pixmap is not None:
            self._pixmap.setPixmap(QPixmap())

    def setImage(self, pixmap: Optional[QPixmap]):
        if pixmap is not None:
            self._pixmap = QGraphicsPixmapItem(pixmap)
            self._scene.addItem(self._pixmap)
        else:
            self._pixmap.setPixmap(pixmap)
        return self._pixmap

    @pyqtProperty(bool)
    def isCutting(self) -> bool:
        return self._cutStart

    def _makeRectItem(self, start, end) -> QGraphicsItem:
        pen = QPen(Qt.SolidLine)
        pen.setColor(QColor(0, 0, 255))
        pen.setWidth(2)
        brush = QBrush(QColor(0, 0, 255, 70))
        rect = self._scene.addRect(QRectF(start, end), pen, brush)
        rect.setFlag(QGraphicsItem.ItemIsMovable, True)
        return rect

    def _updateRect(self):
        if not self._rect:
            self._rect = self._makeRectItem(self._startPos, self._currentPos)
        else:
            self._rect.setRect(self.selectedArea())
        self._rect.setZValue(18)

    def selectedArea(self) -> QRectF:
        return QRectF(self._startPos, self._currentPos)

    def selectedImage(self) -> QPixmap:
        return self._pixmap.pixmap().copy(self.selectedArea().toRect())

    @pyqtSlot(bool)
    def _on_cutStateChanged(self, signal: bool):
        self._cutStart = not self._cutStart
        if not signal:
            self._cutStart = False

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers != Qt.ControlModifier:
            return
        # Zoom Factor
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor
        # Save the scene pos
        oldPos = self.mapToScene(event.pos())
        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)
        # Get the new position
        newPos = self.mapToScene(event.pos())
        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
        # done, do not propagate
        event.accept()

    def _getPos(self, event):
        return self.mapToScene(event.pos())

    def mousePressEvent(self, event):
        if event.button() != _SELECTED_BTN:
            super().mousePressEvent(event)
            return
        self._startPos = self._getPos(event)
        self._currentPos = self._startPos
        self._updateRect()
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() != _SELECTED_BTN:
            super().mouseMoveEvent(event)
            return
        self._currentPos = self._getPos(event)
        # print(self._currentPos, self._startPos)
        self._updateRect()
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() != _SELECTED_BTN:
            super().mousePressEvent(event)
            return
        if self._startPos is not None and self._currentPos is not None and self._startPos != self._currentPos:
            self.cutFinished.emit()
        self._cutStart = False
        event.accept()

    @pyqtProperty(QGraphicsScene)
    def scene(self):
        return self._scene
