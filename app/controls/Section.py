from PyQt5.QtCore import Qt, QAbstractAnimation, QParallelAnimationGroup, QPropertyAnimation, pyqtSlot
from PyQt5.QtWidgets import QWidget, QToolButton, QFrame, QScrollArea, QGridLayout, QSizePolicy

class _Ui:
    def __init__(self, widget):
        self.mainLayout = QGridLayout()
        self.toggleButton = QToolButton()
        self.headerLine = QFrame()
        self.toggleAnimation = QParallelAnimationGroup(widget)
        self.contentArea = QScrollArea()

    def setupUi(self, widget):
        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.ArrowType.RightArrow)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.headerLine.setFrameShape(QFrame.HLine)
        self.headerLine.setFrameShadow(QFrame.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.contentArea.setStyleSheet("QScrollArea { border: none; }")
        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

        # why do you need Union[QByteArray, bytes, bytearray] for 2nd argument?
        self.toggleAnimation.addAnimation(QPropertyAnimation(widget, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(widget, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

        self.mainLayout.setVerticalSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.toggleButton, 0, 0, 1, 1, Qt.AlignLeft)
        self.mainLayout.addWidget(self.headerLine, 0, 2, 1, 1)
        self.mainLayout.addWidget(self.contentArea, 1, 0, 1, 3)
        widget.setLayout(self.mainLayout)


class Section(QWidget):
    def __init__(self, title="", animationDuration=300, parent=None):
        super().__init__(parent)

        self._ui = _Ui(self)
        self._ui.setupUi(self)

        self.setTitle(title)
        self._animationDuration = animationDuration

        self._ui.toggleButton.clicked.connect(self._on_collapsed)

    @pyqtSlot(bool)
    def _on_collapsed(self, checked: bool):
        self._ui.toggleButton.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)
        self._ui.toggleAnimation.setDirection(QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward)
        self._ui.toggleAnimation.start()

    def setTitle(self, title: str):
        self._ui.toggleButton.setText(title)

    def setContentLayout(self, layout):
        self._ui.contentArea.setLayout(layout)
        collapsedHeight = self.sizeHint().height() - self._ui.contentArea.maximumHeight()
        contentHeight = layout.sizeHint().height()
        animations = self._ui.toggleAnimation
        for i in range(animations.animationCount() - 1):
            animation = animations.animationAt(i)
            animation.setDuration(self._animationDuration)
            animation.setStartValue(collapsedHeight)
            animation.setEndValue(collapsedHeight + contentHeight)
        animation = animations.animationAt(animations.animationCount() - 1)
        animation.setDuration(self._animationDuration)
        animation.setStartValue(0)
        animation.setEndValue(contentHeight)

