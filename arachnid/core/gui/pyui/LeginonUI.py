# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/robertlanglois/workspace/arachnida/src/arachnid/core/gui/pyui/LeginonUI.ui'
#
# Created: Sun Dec 15 10:08:11 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from ..util.qt4_loader import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(396, 421)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.loginStackedWidget = QtGui.QStackedWidget(self.widget)
        self.loginStackedWidget.setObjectName("loginStackedWidget")
        self.welcomePage = QtGui.QWidget()
        self.welcomePage.setObjectName("welcomePage")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.welcomePage)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.widget_2 = QtGui.QWidget(self.welcomePage)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget_2)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QtGui.QLabel(self.widget_2)
        font = QtGui.QFont()
        font.setFamily("Baskerville")
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.widget_3 = QtGui.QWidget(self.widget_2)
        self.widget_3.setObjectName("widget_3")
        self.gridLayout_2 = QtGui.QGridLayout(self.widget_3)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_6 = QtGui.QLabel(self.widget_3)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)
        self.entryLimitSpinBox = QtGui.QSpinBox(self.widget_3)
        self.entryLimitSpinBox.setMinimum(1)
        self.entryLimitSpinBox.setMaximum(100000)
        self.entryLimitSpinBox.setObjectName("entryLimitSpinBox")
        self.gridLayout_2.addWidget(self.entryLimitSpinBox, 1, 1, 1, 1)
        self.reloadTableToolButton = QtGui.QToolButton(self.widget_3)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/mini/mini/arrow_refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reloadTableToolButton.setIcon(icon)
        self.reloadTableToolButton.setObjectName("reloadTableToolButton")
        self.gridLayout_2.addWidget(self.reloadTableToolButton, 1, 2, 1, 1)
        self.changeUserPushButton = QtGui.QPushButton(self.widget_3)
        self.changeUserPushButton.setObjectName("changeUserPushButton")
        self.gridLayout_2.addWidget(self.changeUserPushButton, 0, 1, 1, 1)
        self.verticalLayout_4.addWidget(self.widget_3)
        self.verticalLayout_3.addWidget(self.widget_2)
        self.projectTableView = QtGui.QTableView(self.welcomePage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.projectTableView.sizePolicy().hasHeightForWidth())
        self.projectTableView.setSizePolicy(sizePolicy)
        self.projectTableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.projectTableView.setProperty("showDropIndicator", False)
        self.projectTableView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.projectTableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.projectTableView.setObjectName("projectTableView")
        self.verticalLayout_3.addWidget(self.projectTableView)
        self.loginStackedWidget.addWidget(self.welcomePage)
        self.loginPage = QtGui.QWidget()
        self.loginPage.setObjectName("loginPage")
        self.gridLayout = QtGui.QGridLayout(self.loginPage)
        self.gridLayout.setContentsMargins(0, 0, 0, 3)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(self.loginPage)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.leginonHostnameLineEdit = QtGui.QLineEdit(self.loginPage)
        self.leginonHostnameLineEdit.setObjectName("leginonHostnameLineEdit")
        self.gridLayout.addWidget(self.leginonHostnameLineEdit, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.loginPage)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 7, 0, 1, 1)
        self.usernameLineEdit = QtGui.QLineEdit(self.loginPage)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.gridLayout.addWidget(self.usernameLineEdit, 7, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.loginPage)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.projectHostnameLineEdit = QtGui.QLineEdit(self.loginPage)
        self.projectHostnameLineEdit.setObjectName("projectHostnameLineEdit")
        self.gridLayout.addWidget(self.projectHostnameLineEdit, 3, 1, 1, 1)
        self.passwordLineEdit = QtGui.QLineEdit(self.loginPage)
        self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.gridLayout.addWidget(self.passwordLineEdit, 8, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.loginPage)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 8, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 11, 1, 1, 1)
        self.loginPushButton = QtGui.QPushButton(self.loginPage)
        self.loginPushButton.setObjectName("loginPushButton")
        self.gridLayout.addWidget(self.loginPushButton, 10, 0, 1, 1)
        self.leginonDBNameLineEdit = QtGui.QLineEdit(self.loginPage)
        self.leginonDBNameLineEdit.setObjectName("leginonDBNameLineEdit")
        self.gridLayout.addWidget(self.leginonDBNameLineEdit, 1, 2, 1, 1)
        self.projectDBNameLineEdit = QtGui.QLineEdit(self.loginPage)
        self.projectDBNameLineEdit.setObjectName("projectDBNameLineEdit")
        self.gridLayout.addWidget(self.projectDBNameLineEdit, 3, 2, 1, 1)
        self.label_8 = QtGui.QLabel(self.loginPage)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 0, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.loginPage)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 2, 1, 1)
        self.loginStackedWidget.addWidget(self.loginPage)
        self.verticalLayout_2.addWidget(self.loginStackedWidget)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(Form)
        self.loginStackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.leginonHostnameLineEdit, self.projectHostnameLineEdit)
        Form.setTabOrder(self.projectHostnameLineEdit, self.usernameLineEdit)
        Form.setTabOrder(self.usernameLineEdit, self.passwordLineEdit)
        Form.setTabOrder(self.passwordLineEdit, self.loginPushButton)
        Form.setTabOrder(self.loginPushButton, self.changeUserPushButton)
        Form.setTabOrder(self.changeUserPushButton, self.entryLimitSpinBox)
        Form.setTabOrder(self.entryLimitSpinBox, self.reloadTableToolButton)
        Form.setTabOrder(self.reloadTableToolButton, self.projectTableView)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Welcome", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Form", "Show last", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadTableToolButton.setToolTip(QtGui.QApplication.translate("Form", "Reload the table from the database", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadTableToolButton.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.changeUserPushButton.setText(QtGui.QApplication.translate("Form", "Change User...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Leginon DB", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Form", "Project DB", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.loginPushButton.setText(QtGui.QApplication.translate("Form", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.leginonDBNameLineEdit.setText(QtGui.QApplication.translate("Form", "leginondb", None, QtGui.QApplication.UnicodeUTF8))
        self.projectDBNameLineEdit.setText(QtGui.QApplication.translate("Form", "projectdb", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Form", "Host name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Form", "Database Name", None, QtGui.QApplication.UnicodeUTF8))

from ..icons import icons_rc;icons_rc;
