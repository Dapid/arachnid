# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/robertlanglois/workspace/arachnida/src/arachnid/core/gui/dialogs/pyui/ProjectWizard.ui'
#
# Created: Mon Jan 14 16:52:46 2013
#      by: PyQt4 UI code generator 4.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ProjectWizard(object):
    def setupUi(self, ProjectWizard):
        ProjectWizard.setObjectName(_fromUtf8("ProjectWizard"))
        ProjectWizard.resize(691, 412)
        ProjectWizard.setWizardStyle(QtGui.QWizard.MacStyle)
        ProjectWizard.setOptions(QtGui.QWizard.NoCancelButton|QtGui.QWizard.NoDefaultButton)
        self.wizardPage1 = QtGui.QWizardPage()
        self.wizardPage1.setObjectName(_fromUtf8("wizardPage1"))
        ProjectWizard.addPage(self.wizardPage1)
        self.wizardPage = QtGui.QWizardPage()
        self.wizardPage.setObjectName(_fromUtf8("wizardPage"))
        self.verticalLayout = QtGui.QVBoxLayout(self.wizardPage)
        self.verticalLayout.setMargin(2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(self.wizardPage)
        self.widget.setMinimumSize(QtCore.QSize(200, 200))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(6)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.micrographFileLineEdit = QtGui.QLineEdit(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.micrographFileLineEdit.sizePolicy().hasHeightForWidth())
        self.micrographFileLineEdit.setSizePolicy(sizePolicy)
        self.micrographFileLineEdit.setObjectName(_fromUtf8("micrographFileLineEdit"))
        self.gridLayout.addWidget(self.micrographFileLineEdit, 0, 0, 1, 1)
        self.micrographFilePushButton = QtGui.QPushButton(self.widget)
        self.micrographFilePushButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/mini/mini/folder.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.micrographFilePushButton.setIcon(icon)
        self.micrographFilePushButton.setFlat(True)
        self.micrographFilePushButton.setObjectName(_fromUtf8("micrographFilePushButton"))
        self.gridLayout.addWidget(self.micrographFilePushButton, 0, 1, 1, 1)
        self.invertCheckBox = QtGui.QCheckBox(self.widget)
        self.invertCheckBox.setChecked(True)
        self.invertCheckBox.setObjectName(_fromUtf8("invertCheckBox"))
        self.gridLayout.addWidget(self.invertCheckBox, 1, 1, 1, 1)
        self.widget_2 = QtGui.QWidget(self.widget)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget_2)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_2 = QtGui.QLabel(self.widget_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.micrographCountLabel = QtGui.QLabel(self.widget_2)
        self.micrographCountLabel.setObjectName(_fromUtf8("micrographCountLabel"))
        self.gridLayout_2.addWidget(self.micrographCountLabel, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.widget_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.widget_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 2, 0, 1, 1)
        self.micrographWidthLabel = QtGui.QLabel(self.widget_2)
        self.micrographWidthLabel.setObjectName(_fromUtf8("micrographWidthLabel"))
        self.gridLayout_2.addWidget(self.micrographWidthLabel, 1, 1, 1, 1)
        self.micrographHeightLabel = QtGui.QLabel(self.widget_2)
        self.micrographHeightLabel.setObjectName(_fromUtf8("micrographHeightLabel"))
        self.gridLayout_2.addWidget(self.micrographHeightLabel, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.widget_2, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.widget)
        self.scrollArea = QtGui.QScrollArea(self.wizardPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 467, 94))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.micrographDisplayLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.micrographDisplayLabel.setText(_fromUtf8(""))
        self.micrographDisplayLabel.setObjectName(_fromUtf8("micrographDisplayLabel"))
        self.verticalLayout_2.addWidget(self.micrographDisplayLabel)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        ProjectWizard.addPage(self.wizardPage)
        self.wizardPage_2 = QtGui.QWizardPage()
        self.wizardPage_2.setObjectName(_fromUtf8("wizardPage_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.wizardPage_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.widget_3 = QtGui.QWidget(self.wizardPage_2)
        self.widget_3.setMinimumSize(QtCore.QSize(200, 200))
        self.widget_3.setObjectName(_fromUtf8("widget_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.widget_3)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.referenceLineEdit = QtGui.QLineEdit(self.widget_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.referenceLineEdit.sizePolicy().hasHeightForWidth())
        self.referenceLineEdit.setSizePolicy(sizePolicy)
        self.referenceLineEdit.setObjectName(_fromUtf8("referenceLineEdit"))
        self.gridLayout_3.addWidget(self.referenceLineEdit, 0, 0, 1, 1)
        self.referenceFilePushButton = QtGui.QPushButton(self.widget_3)
        self.referenceFilePushButton.setText(_fromUtf8(""))
        self.referenceFilePushButton.setIcon(icon)
        self.referenceFilePushButton.setFlat(True)
        self.referenceFilePushButton.setObjectName(_fromUtf8("referenceFilePushButton"))
        self.gridLayout_3.addWidget(self.referenceFilePushButton, 0, 1, 1, 1)
        self.widget_4 = QtGui.QWidget(self.widget_3)
        self.widget_4.setObjectName(_fromUtf8("widget_4"))
        self.gridLayout_4 = QtGui.QGridLayout(self.widget_4)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_12 = QtGui.QLabel(self.widget_4)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_4.addWidget(self.label_12, 0, 0, 1, 1)
        self.referenceDepthLabel = QtGui.QLabel(self.widget_4)
        self.referenceDepthLabel.setObjectName(_fromUtf8("referenceDepthLabel"))
        self.gridLayout_4.addWidget(self.referenceDepthLabel, 0, 1, 1, 1)
        self.label_14 = QtGui.QLabel(self.widget_4)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_4.addWidget(self.label_14, 1, 0, 1, 1)
        self.label_15 = QtGui.QLabel(self.widget_4)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_4.addWidget(self.label_15, 2, 0, 1, 1)
        self.referenceWidthLabel = QtGui.QLabel(self.widget_4)
        self.referenceWidthLabel.setObjectName(_fromUtf8("referenceWidthLabel"))
        self.gridLayout_4.addWidget(self.referenceWidthLabel, 1, 1, 1, 1)
        self.referenceHeightLabel = QtGui.QLabel(self.widget_4)
        self.referenceHeightLabel.setObjectName(_fromUtf8("referenceHeightLabel"))
        self.gridLayout_4.addWidget(self.referenceHeightLabel, 2, 1, 1, 1)
        self.label_18 = QtGui.QLabel(self.widget_4)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.gridLayout_4.addWidget(self.label_18, 3, 0, 1, 1)
        self.referencePixelSizeDoubleSpinBox = QtGui.QDoubleSpinBox(self.widget_4)
        self.referencePixelSizeDoubleSpinBox.setDecimals(3)
        self.referencePixelSizeDoubleSpinBox.setObjectName(_fromUtf8("referencePixelSizeDoubleSpinBox"))
        self.gridLayout_4.addWidget(self.referencePixelSizeDoubleSpinBox, 3, 1, 1, 1)
        self.gridLayout_3.addWidget(self.widget_4, 1, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.widget_3)
        ProjectWizard.addPage(self.wizardPage_2)
        self.wizardPage_3 = QtGui.QWizardPage()
        self.wizardPage_3.setObjectName(_fromUtf8("wizardPage_3"))
        self.formLayout = QtGui.QFormLayout(self.wizardPage_3)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_8 = QtGui.QLabel(self.wizardPage_3)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_8)
        self.pixelSizeDoubleSpinBox = QtGui.QDoubleSpinBox(self.wizardPage_3)
        self.pixelSizeDoubleSpinBox.setObjectName(_fromUtf8("pixelSizeDoubleSpinBox"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.pixelSizeDoubleSpinBox)
        self.label_9 = QtGui.QLabel(self.wizardPage_3)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_9)
        self.particleSizeDoubleSpinBox = QtGui.QDoubleSpinBox(self.wizardPage_3)
        self.particleSizeDoubleSpinBox.setMaximum(5000.0)
        self.particleSizeDoubleSpinBox.setObjectName(_fromUtf8("particleSizeDoubleSpinBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.particleSizeDoubleSpinBox)
        self.label_10 = QtGui.QLabel(self.wizardPage_3)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_10)
        self.voltageDoubleSpinBox = QtGui.QDoubleSpinBox(self.wizardPage_3)
        self.voltageDoubleSpinBox.setMaximum(5000.0)
        self.voltageDoubleSpinBox.setObjectName(_fromUtf8("voltageDoubleSpinBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.voltageDoubleSpinBox)
        self.label_11 = QtGui.QLabel(self.wizardPage_3)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_11)
        self.csDoubleSpinBox = QtGui.QDoubleSpinBox(self.wizardPage_3)
        self.csDoubleSpinBox.setObjectName(_fromUtf8("csDoubleSpinBox"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.csDoubleSpinBox)
        ProjectWizard.addPage(self.wizardPage_3)
        self.wizardPage_4 = QtGui.QWizardPage()
        self.wizardPage_4.setObjectName(_fromUtf8("wizardPage_4"))
        self.formLayout_2 = QtGui.QFormLayout(self.wizardPage_4)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_19 = QtGui.QLabel(self.wizardPage_4)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_19)
        self.workerCountSpinBox = QtGui.QSpinBox(self.wizardPage_4)
        self.workerCountSpinBox.setMaximum(10000)
        self.workerCountSpinBox.setProperty(_fromUtf8("value"), 1)
        self.workerCountSpinBox.setObjectName(_fromUtf8("workerCountSpinBox"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.workerCountSpinBox)
        self.label_20 = QtGui.QLabel(self.wizardPage_4)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_20)
        self.threadCountSpinBox = QtGui.QSpinBox(self.wizardPage_4)
        self.threadCountSpinBox.setMaximum(10000)
        self.threadCountSpinBox.setProperty(_fromUtf8("value"), 1)
        self.threadCountSpinBox.setObjectName(_fromUtf8("threadCountSpinBox"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.threadCountSpinBox)
        self.label_21 = QtGui.QLabel(self.wizardPage_4)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_21)
        self.windowSizeSpinBox = QtGui.QSpinBox(self.wizardPage_4)
        self.windowSizeSpinBox.setMaximum(5000)
        self.windowSizeSpinBox.setObjectName(_fromUtf8("windowSizeSpinBox"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.windowSizeSpinBox)
        self.label_22 = QtGui.QLabel(self.wizardPage_4)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_22)
        self.extensionLineEdit = QtGui.QLineEdit(self.wizardPage_4)
        self.extensionLineEdit.setMaxLength(3)
        self.extensionLineEdit.setObjectName(_fromUtf8("extensionLineEdit"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.extensionLineEdit)
        ProjectWizard.addPage(self.wizardPage_4)
        self.wizardPage2 = QtGui.QWizardPage()
        self.wizardPage2.setSubTitle(_fromUtf8(""))
        self.wizardPage2.setObjectName(_fromUtf8("wizardPage2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.wizardPage2)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.settingsTabWidget = QtGui.QTabWidget(self.wizardPage2)
        self.settingsTabWidget.setObjectName(_fromUtf8("settingsTabWidget"))
        self.verticalLayout_4.addWidget(self.settingsTabWidget)
        ProjectWizard.addPage(self.wizardPage2)
        self.wizardPage_5 = QtGui.QWizardPage()
        self.wizardPage_5.setObjectName(_fromUtf8("wizardPage_5"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.wizardPage_5)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.widget_5 = QtGui.QWidget(self.wizardPage_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy)
        self.widget_5.setObjectName(_fromUtf8("widget_5"))
        self.gridLayout_5 = QtGui.QGridLayout(self.widget_5)
        self.gridLayout_5.setContentsMargins(-1, 6, -1, 6)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.jobProgressBar = QtGui.QProgressBar(self.widget_5)
        self.jobProgressBar.setProperty(_fromUtf8("value"), 0)
        self.jobProgressBar.setObjectName(_fromUtf8("jobProgressBar"))
        self.gridLayout_5.addWidget(self.jobProgressBar, 0, 0, 1, 1)
        self.verticalLayout_5.addWidget(self.widget_5)
        self.widget_7 = QtGui.QWidget(self.wizardPage_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.widget_7.sizePolicy().hasHeightForWidth())
        self.widget_7.setSizePolicy(sizePolicy)
        self.widget_7.setObjectName(_fromUtf8("widget_7"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_7)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.jobListView = QtGui.QListView(self.widget_7)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.jobListView.sizePolicy().hasHeightForWidth())
        self.jobListView.setSizePolicy(sizePolicy)
        self.jobListView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.jobListView.setProperty(_fromUtf8("showDropIndicator"), False)
        self.jobListView.setObjectName(_fromUtf8("jobListView"))
        self.horizontalLayout_2.addWidget(self.jobListView)
        self.logTextEdit = QtGui.QPlainTextEdit(self.widget_7)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logTextEdit.sizePolicy().hasHeightForWidth())
        self.logTextEdit.setSizePolicy(sizePolicy)
        self.logTextEdit.setUndoRedoEnabled(False)
        self.logTextEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.logTextEdit.setReadOnly(True)
        self.logTextEdit.setObjectName(_fromUtf8("logTextEdit"))
        self.horizontalLayout_2.addWidget(self.logTextEdit)
        self.verticalLayout_5.addWidget(self.widget_7)
        self.widget_6 = QtGui.QWidget(self.wizardPage_5)
        self.widget_6.setObjectName(_fromUtf8("widget_6"))
        self.formLayout_3 = QtGui.QFormLayout(self.widget_6)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout_3.setMargin(0)
        self.formLayout_3.setMargin(0)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.runJobButton = QtGui.QPushButton(self.widget_6)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/mini/mini/arrow_refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/mini/mini/cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/mini/mini/cancel.png")), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        self.runJobButton.setIcon(icon1)
        self.runJobButton.setCheckable(True)
        self.runJobButton.setObjectName(_fromUtf8("runJobButton"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.runJobButton)
        self.verticalLayout_5.addWidget(self.widget_6)
        ProjectWizard.addPage(self.wizardPage_5)

        self.retranslateUi(ProjectWizard)
        self.settingsTabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(ProjectWizard)

    def retranslateUi(self, ProjectWizard):
        ProjectWizard.setWindowTitle(QtGui.QApplication.translate("ProjectWizard", "Wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage1.setTitle(QtGui.QApplication.translate("ProjectWizard", "Welcome to Arachnid", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage1.setSubTitle(QtGui.QApplication.translate("ProjectWizard", "This wizard will take you through the steps required to generate and run an arachnid project.", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage.setTitle(QtGui.QApplication.translate("ProjectWizard", "Select Micrographs", None, QtGui.QApplication.UnicodeUTF8))
        self.invertCheckBox.setToolTip(QtGui.QApplication.translate("ProjectWizard", "Do the micrographs require contrast inversion", None, QtGui.QApplication.UnicodeUTF8))
        self.invertCheckBox.setText(QtGui.QApplication.translate("ProjectWizard", "Invert Contrast", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ProjectWizard", "Number of Micrographs", None, QtGui.QApplication.UnicodeUTF8))
        self.micrographCountLabel.setText(QtGui.QApplication.translate("ProjectWizard", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ProjectWizard", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ProjectWizard", "Height", None, QtGui.QApplication.UnicodeUTF8))
        self.micrographWidthLabel.setText(QtGui.QApplication.translate("ProjectWizard", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.micrographHeightLabel.setText(QtGui.QApplication.translate("ProjectWizard", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage_2.setTitle(QtGui.QApplication.translate("ProjectWizard", "Select Reference", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("ProjectWizard", "Depth", None, QtGui.QApplication.UnicodeUTF8))
        self.referenceDepthLabel.setText(QtGui.QApplication.translate("ProjectWizard", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("ProjectWizard", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("ProjectWizard", "Height", None, QtGui.QApplication.UnicodeUTF8))
        self.referenceWidthLabel.setText(QtGui.QApplication.translate("ProjectWizard", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.referenceHeightLabel.setText(QtGui.QApplication.translate("ProjectWizard", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_18.setText(QtGui.QApplication.translate("ProjectWizard", "Reference Pixel Size", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage_3.setTitle(QtGui.QApplication.translate("ProjectWizard", "Set Microscope Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("ProjectWizard", "Pixel Size (1/A)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("ProjectWizard", "Particle Size (A)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("ProjectWizard", "Voltage (kV)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("ProjectWizard", "CS (mm)", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage_4.setTitle(QtGui.QApplication.translate("ProjectWizard", "Advanced Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setText(QtGui.QApplication.translate("ProjectWizard", "Process Count", None, QtGui.QApplication.UnicodeUTF8))
        self.label_20.setText(QtGui.QApplication.translate("ProjectWizard", "Thread Count", None, QtGui.QApplication.UnicodeUTF8))
        self.label_21.setText(QtGui.QApplication.translate("ProjectWizard", "Window Size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_22.setText(QtGui.QApplication.translate("ProjectWizard", "SPIDER Extension", None, QtGui.QApplication.UnicodeUTF8))
        self.extensionLineEdit.setInputMask(QtGui.QApplication.translate("ProjectWizard", "ANN; ", None, QtGui.QApplication.UnicodeUTF8))
        self.extensionLineEdit.setText(QtGui.QApplication.translate("ProjectWizard", "dat", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage2.setTitle(QtGui.QApplication.translate("ProjectWizard", "Fine Tune Options", None, QtGui.QApplication.UnicodeUTF8))
        self.runJobButton.setText(QtGui.QApplication.translate("ProjectWizard", "Run", None, QtGui.QApplication.UnicodeUTF8))

from arachnid.core.gui.icons import icons_rc
icons_rc;
