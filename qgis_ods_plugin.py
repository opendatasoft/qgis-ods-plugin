import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import *

from . import helper_functions, ui_methods


class QgisOdsPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QtWidgets.QAction(QIcon(os.path.join(os.path.dirname(__file__), "icon.png")), "ODS plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        dialog = ui_methods.InputDialog(self.iface)
        settings = QSettings()
        if 'ods_cache' in settings.allKeys():
            dialog.push_ods_cache(settings.value('ods_cache'))
        if dialog.exec():
            pass

            # TODO : deal with conversion from type to qgsField : do default string and if date works, date ?
            #  but how ? Hoooooooooooow ?

