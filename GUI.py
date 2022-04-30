# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GUI.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1072, 762)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.lineEdit)

        self.OK = QPushButton(self.centralwidget)
        self.OK.setObjectName(u"OK")

        self.verticalLayout.addWidget(self.OK)

        self.CANCEL = QPushButton(self.centralwidget)
        self.CANCEL.setObjectName(u"CANCEL")

        self.verticalLayout.addWidget(self.CANCEL)

        self.SHOW = QPushButton(self.centralwidget)
        self.SHOW.setObjectName(u"SHOW")

        self.verticalLayout.addWidget(self.SHOW)

        self.comboBox = QComboBox(self.centralwidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout.addWidget(self.comboBox)

        self.infoEdit = QTextEdit(self.centralwidget)
        self.infoEdit.setObjectName(u"infoEdit")
        sizePolicy.setHeightForWidth(self.infoEdit.sizePolicy().hasHeightForWidth())
        self.infoEdit.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.infoEdit)


        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 1)

        self.mainscrollArea = QScrollArea(self.centralwidget)
        self.mainscrollArea.setObjectName(u"mainscrollArea")
        self.mainscrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 768, 578))
        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.mainView = QGraphicsView(self.scrollAreaWidgetContents)
        self.mainView.setObjectName(u"mainView")

        self.horizontalLayout_2.addWidget(self.mainView)

        self.typeLayout = QGridLayout()
        self.typeLayout.setObjectName(u"typeLayout")
        self.typeLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.typeLayout.setContentsMargins(0, -1, 0, -1)

        self.horizontalLayout_2.addLayout(self.typeLayout)

        self.mainscrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.mainscrollArea, 1, 0, 1, 1)

        self.timeCounter = QLabel(self.centralwidget)
        self.timeCounter.setObjectName(u"timeCounter")

        self.gridLayout.addWidget(self.timeCounter, 2, 1, 1, 1)

        self.combArea = QScrollArea(self.centralwidget)
        self.combArea.setObjectName(u"combArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.combArea.sizePolicy().hasHeightForWidth())
        self.combArea.setSizePolicy(sizePolicy1)
        self.combArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 1046, 69))
        self.combArea.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout.addWidget(self.combArea, 0, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1072, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.OK.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.CANCEL.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.SHOW.setText(QCoreApplication.translate("MainWindow", u"Show", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"DFS", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"BFS", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"ASTAR", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"GREEDY", None))

        self.timeCounter.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

