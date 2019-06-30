# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.imageView = QtWidgets.QGraphicsView(self.centralwidget)
        self.imageView.setObjectName("imageView")
        self.horizontalLayout.addWidget(self.imageView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.imageSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.imageSpinBox.setMinimum(1)
        self.imageSpinBox.setMaximum(100)
        self.imageSpinBox.setObjectName("imageSpinBox")
        self.verticalLayout.addWidget(self.imageSpinBox)
        self.imageSlider = QtWidgets.QSlider(self.centralwidget)
        self.imageSlider.setMinimum(1)
        self.imageSlider.setMaximum(100)
        self.imageSlider.setSingleStep(5)
        self.imageSlider.setOrientation(QtCore.Qt.Vertical)
        self.imageSlider.setInvertedAppearance(True)
        self.imageSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.imageSlider.setTickInterval(20)
        self.imageSlider.setObjectName("imageSlider")
        self.verticalLayout.addWidget(self.imageSlider)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 35))
        self.menubar.setObjectName("menubar")
        self.menu_F = QtWidgets.QMenu(self.menubar)
        self.menu_F.setObjectName("menu_F")
        self.menu_V = QtWidgets.QMenu(self.menubar)
        self.menu_V.setObjectName("menu_V")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.openAction = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("document-open")
        self.openAction.setIcon(icon)
        self.openAction.setObjectName("openAction")
        self.labelAction = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("document-open")
        self.labelAction.setIcon(icon)
        self.labelAction.setObjectName("labelAction")
        self.exitAction = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("application-exit")
        self.exitAction.setIcon(icon)
        self.exitAction.setObjectName("exitAction")
        self.setWindowAction = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.setWindowAction.setIcon(icon)
        self.setWindowAction.setObjectName("setWindowAction")
        self.menu_F.addAction(self.openAction)
        self.menu_F.addAction(self.labelAction)
        self.menu_F.addSeparator()
        self.menu_F.addAction(self.exitAction)
        self.menu_V.addAction(self.setWindowAction)
        self.menubar.addAction(self.menu_F.menuAction())
        self.menubar.addAction(self.menu_V.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "肺癌转移识别系统"))
        self.menu_F.setTitle(_translate("MainWindow", "文件(&F)"))
        self.menu_V.setTitle(_translate("MainWindow", "视图(&V)"))
        self.openAction.setText(_translate("MainWindow", "打开DICOM(&O)"))
        self.openAction.setStatusTip(_translate("MainWindow", "选择文件夹，加载其中的DICOM序列"))
        self.labelAction.setText(_translate("MainWindow", "打开标签文件(&L)"))
        self.labelAction.setStatusTip(_translate("MainWindow", "打开对应的标签文件"))
        self.exitAction.setText(_translate("MainWindow", "退出(&Q)"))
        self.exitAction.setStatusTip(_translate("MainWindow", "退出程序"))
        self.setWindowAction.setText(_translate("MainWindow", "设置窗位与窗宽(&W)"))
        self.setWindowAction.setStatusTip(_translate("MainWindow", "设置窗位与窗宽值，并重新处理图像"))


