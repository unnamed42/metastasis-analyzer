# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WindowDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WindowDialog(object):
    def setupUi(self, WindowDialog):
        WindowDialog.setObjectName("WindowDialog")
        WindowDialog.resize(293, 239)
        self.gridLayout = QtWidgets.QGridLayout(WindowDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.widthEdit = QtWidgets.QSpinBox(WindowDialog)
        self.widthEdit.setMinimum(-2000)
        self.widthEdit.setMaximum(2000)
        self.widthEdit.setObjectName("widthEdit")
        self.gridLayout.addWidget(self.widthEdit, 2, 1, 1, 3)
        self.levelEdit = QtWidgets.QSpinBox(WindowDialog)
        self.levelEdit.setMinimum(-2000)
        self.levelEdit.setMaximum(2000)
        self.levelEdit.setObjectName("levelEdit")
        self.gridLayout.addWidget(self.levelEdit, 1, 1, 1, 3)
        self.buttonBox = QtWidgets.QDialogButtonBox(WindowDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 4)
        self.presetComboBox = QtWidgets.QComboBox(WindowDialog)
        self.presetComboBox.setObjectName("presetComboBox")
        self.gridLayout.addWidget(self.presetComboBox, 0, 1, 1, 3)
        self.label_1 = QtWidgets.QLabel(WindowDialog)
        self.label_1.setObjectName("label_1")
        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(WindowDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(WindowDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3.setBuddy(self.widthEdit)
        self.label_2.setBuddy(self.levelEdit)

        self.retranslateUi(WindowDialog)
        self.buttonBox.accepted.connect(WindowDialog.accept)
        self.buttonBox.rejected.connect(WindowDialog.reject)
        self.presetComboBox.currentIndexChanged['int'].connect(WindowDialog.selectionChanged)
        QtCore.QMetaObject.connectSlotsByName(WindowDialog)

    def retranslateUi(self, WindowDialog):
        _translate = QtCore.QCoreApplication.translate
        WindowDialog.setWindowTitle(_translate("WindowDialog", "设置窗位与窗宽"))
        self.label_1.setText(_translate("WindowDialog", "使用预设："))
        self.label_3.setText(_translate("WindowDialog", "窗宽："))
        self.label_2.setText(_translate("WindowDialog", "窗位："))
