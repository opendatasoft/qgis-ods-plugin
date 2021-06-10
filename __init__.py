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

from PyQt5.QtWidgets import QAction, QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QApplication, QLabel
from . import pyqgis_script


def classFactory(iface):
    return MinimalPlugin(iface)


class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction('ODS', self.iface.mainWindow())
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
        # TODO : add error for : wrong domain, wrong dataset_id
        pyqgis_script.import_to_qgis(plugin_input)


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        label = QLabel("Enter the domain, the dataset id, and the column where the geometry is.", self)
        self.domainInput = QLineEdit(self)
        self.datasetidInput = QLineEdit(self)
        self.columnInput = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)


        layout = QFormLayout(self)
        layout.addWidget(label)
        layout.addRow("Name of your domain :", self.domainInput)
        layout.addRow("Name of your dataset :", self.datasetidInput)
        layout.addRow("Name of the geometry column :", self.columnInput)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return self.domainInput.text(), self.datasetidInput.text(), self.columnInput.text()
