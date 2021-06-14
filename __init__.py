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
from PyQt5 import QtWidgets

from ui_methods import InputDialog
from . import helper_functions


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
        if dialog.exec():
            if dialog.domain() == "" or dialog.dataset_id() == "" or dialog.geom_data_name() == "":
                QtWidgets.QMessageBox.information(None, "ERROR:", "All fields must be filled to import a dataset.")
                raise ValueError("One or more fields are empty.")
            # TODO : deal with conversion from type to qgsField UPDATE : /export will deal with that
            # TODO : UPDATE : if we really keep export but we don't really know because heyyyyyy
            helper_functions.import_to_qgis(dialog.domain(), dialog.dataset_id(), dialog.geom_data_name())
