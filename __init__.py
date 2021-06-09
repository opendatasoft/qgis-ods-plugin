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

from PyQt5.QtWidgets import QAction, QMessageBox

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
        QMessageBox.information(None, 'ODS plugin',
                                "When you press the button, you'll get a new dataset from scratch.")

        # TODO : add input
        # TODO : deal with conversion from type to qgsField
        plugin_input = {}
        plugin_input["geom_data_name"] = "sens_velo"
        plugin_input["domain"] = "vroullier"
        plugin_input["dataset_id"] = "reseau-des-itineraires-cyclables"

        pyqgis_script.import_to_qgis(plugin_input)