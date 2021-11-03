# -----------------------------------------------------------
# Copyright (C) 2021 Venceslas Roullier/Opendatasoft
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
# ---------------------------------------------------------------------

import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import *

from . import ui_methods, utils


class QgisOdsPlugin:
    def __init__(self, iface):
        self.iface = iface

    # noinspection PyPep8Naming
    def initGui(self):
        self.action = QtWidgets.QAction(
            QIcon(os.path.join(os.path.dirname(__file__), "icon.png")),
            "ODS plugin",
            self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToWebMenu('Opendatasoft', self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        """
        Init the main dialog window and init the ods_cache, used for storing credentials.
        """
        dialog = ui_methods.ODSDialog(self.iface)
        settings = QSettings()
        if 'ods_cache' in settings.allKeys():
            try:
                apikey = utils.get_apikey_from_cache()
                dialog.push_ods_cache(settings.value('ods_cache'), apikey)
            except KeyError:
                pass
        if dialog.exec():
            pass
