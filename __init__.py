# -----------------------------------------------------------
# Copyright (C) 2021 Venceslas Roullier/Opendatasoft
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------
import os

from PyQt5 import QtWidgets, uic
import sys

from . import pyqgis_script


def classFactory(iface):
    return MinimalPlugin(iface)


class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QtWidgets.QAction('ODS', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        dialog = InputDialog()
        plugin_input = {}
        if dialog.exec():
            plugin_input["domain"], plugin_input["dataset_id"], plugin_input["geom_data_name"] = dialog.getInputs()
        # TODO : deal with conversion from type to qgsField UPDATE : /export will deal with that
        # TODO : add error for : wrong domain
            pyqgis_script.import_to_qgis(plugin_input)


class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super(InputDialog, self).__init__()
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_dir, 'plugin_dialog.ui')
        uic.loadUi(ui_path, self)

        self.domainInput = self.findChild(QtWidgets.QLineEdit, 'domainInput')
        self.updateListButton = self.findChild(QtWidgets.QPushButton, 'updateListButton')
        self.datasetListComboBox = self.findChild(QtWidgets.QComboBox, 'datasetListComboBox')
        self.geometryInput = self.findChild(QtWidgets.QLineEdit, 'geometryInput')

        self.updateListButton.clicked.connect(self.updateListButtonPressed)

        self.show()

    def updateListButtonPressed(self):
        self.datasetListComboBox.clear()
        self.datasetListComboBox.addItems(
            pyqgis_script.datasets_to_dataset_id_list(pyqgis_script.import_dataset_list(self.domainInput.text())))

    def getInputs(self):
        return self.domainInput.text(), self.datasetListComboBox.currentText(), self.geometryInput.text()
