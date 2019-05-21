import platform
import os
import logging
import numpy as np

from foqus_lib.framework.graph.graph import *
from foqus_lib.framework.uq.flowsheetToUQModel import *
from foqus_lib.framework.uq.Model import *
from foqus_lib.framework.uq.LocalExecutionModule import *
from foqus_lib.framework.uq.ResponseSurfaces import *
from foqus_lib.framework.uq.Common import Common

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, \
    QAbstractItemView, QDialogButtonBox, QDialog
mypath = os.path.dirname(__file__)
_updateSDOEModelDialogUI, _updateSDOEModelDialog = \
        uic.loadUiType(os.path.join(mypath, "updateSDOEModelDialog_UI.ui"))
        

class updateSDOEModelDialog(_updateSDOEModelDialog, _updateSDOEModelDialogUI):
    def __init__(self, dat, parent=None):
        super(updateSDOEModelDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.dat = dat

        #Init options
        self.historyRadioButton.toggled.connect(self.showHistoryOption)
        self.templateRadioButton.toggled.connect(self.showTemplateOption)

        self.browseHistoryButton.clicked.connect(self.getDataFileName)
        self.browseHistoryButton.setEnabled(False)
        self.browseTemplateButton.clicked.connect(self.getDataFileName)
        self.browseTemplateButton.setEnabled(False)

        self.show()

    class listItem(QListWidgetItem):
        def __init__(self, text, inputIndex):
            super(updateSDOEModelDialog.listItem, self).__init__(text)
            self.inputIndex = inputIndex

        def getInputIndex(self):
            return self.inputIndex

    def showHistoryOption(self):
        if self.historyRadioButton.isChecked():
            self.historyFileLabel.setEnabled(True)
            self.historyFileEdit.setEnabled(True)
            self.browseHistoryButton.setEnabled(True)
            self.templateFileLabel.setEnabled(False)
            self.templateFileEdit.setEnabled(False)
            self.browseTemplateButton.setEnabled(False)

            button = self.buttonBox.button(QDialogButtonBox.Ok)
            button.setEnabled(True)

    def showTemplateOption(self):
        if self.templateRadioButton.isChecked():
            self.historyFileLabel.setEnabled(False)
            self.historyFileEdit.setEnabled(False)
            self.browseHistoryButton.setEnabled(False)
            self.templateFileLabel.setEnabled(True)
            self.templateFileEdit.setEnabled(True)
            self.browseTemplateButton.setEnabled(True)

            button = self.buttonBox.button(QDialogButtonBox.Ok)
            button.setEnabled(True)

    def getDataFileName(self):
        if platform.system() == 'Windows':
            allFiles = '*.*'
        else:
            allFiles = '*'
       # Get file name
        fileName, selectedFilter = QFileDialog.getOpenFileName(self, "Open Ensemble", '' , "CSV (Comma delimited) (*.csv)")
        if len(fileName) == 0:
            return

        if self.historyRadioButton.isChecked():
            self.historyFileEdit.setText(fileName)
        if self.templateRadioButton.isChecked():
            self.templateFileEdit.setText(fileName)

    def accept(self):
        if self.historyRadioButton.isChecked():
            fileName = self.historyFileEdit.text()
            data = LocalExecutionModule.readSampleFromCsvFile(fileName, False)
            mins = np.min(data.getInputData(), 0)
            maxs = np.max(data.getInputData(), 0)
            defaults = []
            for i in range(len(mins)):
                defaults.append((mins[i] + maxs[i]) / 2)

        if self.templateRadioButton.isChecked():
            fileName = self.templateFileEdit.text()
            data = LocalExecutionModule.readSampleFromCsvFile(fileName, False)
            mins = data.getInputData()[0]
            maxs = data.getInputData()[1]
            if len(data.getInputData()) > 2:
                defaults = data.getInputData()[2]
            else:
                defaults = []
                for i in range(len(mins)):
                    defaults.append((mins[i] + maxs[i]) / 2)

        data.model.setInputMins(mins)
        data.model.setInputMaxs(maxs)
        data.model.setInputDefaults(defaults)
        #data.setSession = self.dat
        self.dat.uqModel = data.model
        self.done(QDialog.Accepted)

    def reject(self):
            self.done(QDialog.Rejected)
