# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 650)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout.setVerticalSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.sourceLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.sourceLineEdit.setReadOnly(True)
        self.sourceLineEdit.setObjectName("sourceLineEdit")
        self.horizontalLayout_3.addWidget(self.sourceLineEdit)
        self.sourceCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.sourceCheckBox.setObjectName("sourceCheckBox")
        self.horizontalLayout_3.addWidget(self.sourceCheckBox)
        self.sourcePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.sourcePushButton.setObjectName("sourcePushButton")
        self.horizontalLayout_3.addWidget(self.sourcePushButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.templateLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.templateLineEdit.setReadOnly(True)
        self.templateLineEdit.setObjectName("templateLineEdit")
        self.horizontalLayout.addWidget(self.templateLineEdit)
        self.templatePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.templatePushButton.setObjectName("templatePushButton")
        self.horizontalLayout.addWidget(self.templatePushButton)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.destinationLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.destinationLineEdit.setReadOnly(True)
        self.destinationLineEdit.setObjectName("destinationLineEdit")
        self.horizontalLayout_5.addWidget(self.destinationLineEdit)
        self.destinationPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.destinationPushButton.setObjectName("destinationPushButton")
        self.horizontalLayout_5.addWidget(self.destinationPushButton)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_5)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.deviceComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.deviceComboBox.setObjectName("deviceComboBox")
        self.horizontalLayout_6.addWidget(self.deviceComboBox)
        self.addPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.addPushButton.setObjectName("addPushButton")
        self.horizontalLayout_6.addWidget(self.addPushButton)
        self.changePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.changePushButton.setObjectName("changePushButton")
        self.horizontalLayout_6.addWidget(self.changePushButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.analyzePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.analyzePushButton.setObjectName("analyzePushButton")
        self.horizontalLayout_6.addWidget(self.analyzePushButton)
        self.generatePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.generatePushButton.setObjectName("generatePushButton")
        self.horizontalLayout_6.addWidget(self.generatePushButton)
        self.outputCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.outputCheckBox.setObjectName("outputCheckBox")
        self.horizontalLayout_6.addWidget(self.outputCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.messagesPlainTextEdit = QtWidgets.QPlainTextEdit(self.tab)
        self.messagesPlainTextEdit.setReadOnly(True)
        self.messagesPlainTextEdit.setObjectName("messagesPlainTextEdit")
        self.gridLayout_2.addWidget(self.messagesPlainTextEdit, 0, 0, 1, 3)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.tab)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 1, 2, 1, 1)
        self.loggingComboBox = QtWidgets.QComboBox(self.tab)
        self.loggingComboBox.setObjectName("loggingComboBox")
        self.loggingComboBox.addItem("")
        self.loggingComboBox.addItem("")
        self.loggingComboBox.addItem("")
        self.loggingComboBox.addItem("")
        self.gridLayout_2.addWidget(self.loggingComboBox, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout.setObjectName("gridLayout")
        self.structureTreeView = QtWidgets.QTreeView(self.tab_2)
        self.structureTreeView.setObjectName("structureTreeView")
        self.structureTreeView.header().setMinimumSectionSize(50)
        self.structureTreeView.header().setStretchLastSection(False)
        self.gridLayout.addWidget(self.structureTreeView, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setEnabled(True)
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.outputTextEdit = QtWidgets.QTextEdit(self.tab_3)
        self.outputTextEdit.setEnabled(False)
        self.outputTextEdit.setObjectName("outputTextEdit")
        self.verticalLayout_2.addWidget(self.outputTextEdit)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.outputCheckBox.clicked['bool'].connect(self.destinationLineEdit.setDisabled)
        self.outputCheckBox.clicked['bool'].connect(self.destinationPushButton.setDisabled)
        self.outputCheckBox.clicked['bool'].connect(self.outputTextEdit.setEnabled)
        self.pushButton.clicked.connect(self.messagesPlainTextEdit.clear)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pmuToFPGA"))
        self.label_2.setText(_translate("MainWindow", "Source"))
        self.sourceCheckBox.setText(_translate("MainWindow", "folder"))
        self.sourcePushButton.setText(_translate("MainWindow", "Browse"))
        self.label.setText(_translate("MainWindow", "Template"))
        self.templatePushButton.setText(_translate("MainWindow", "Browse"))
        self.destinationPushButton.setText(_translate("MainWindow", "Browse"))
        self.label_3.setText(_translate("MainWindow", "Destination"))
        self.addPushButton.setText(_translate("MainWindow", "Add"))
        self.changePushButton.setText(_translate("MainWindow", "Change"))
        self.analyzePushButton.setText(_translate("MainWindow", "Analyze"))
        self.generatePushButton.setText(_translate("MainWindow", "Run"))
        self.outputCheckBox.setText(_translate("MainWindow", "to Output"))
        self.pushButton.setText(_translate("MainWindow", "Clear"))
        self.loggingComboBox.setItemText(0, _translate("MainWindow", "DEBUG"))
        self.loggingComboBox.setItemText(1, _translate("MainWindow", "INFO"))
        self.loggingComboBox.setItemText(2, _translate("MainWindow", "WARNING"))
        self.loggingComboBox.setItemText(3, _translate("MainWindow", "ERROR"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Messages"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Structure"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Output"))

