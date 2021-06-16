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
        dialog = ui_methods.InputDialog()
        settings = QSettings()
        if 'domain_name_cache' in settings.allKeys():
            dialog.push_last_domain(settings.value('domain_name_cache'))
        if dialog.exec():
            if dialog.domain() == "" or dialog.dataset_id() == "" or dialog.geom_data_name() == "":
                QtWidgets.QMessageBox.information(None, "ERROR:", "All fields must be filled to import a dataset.")
                return
            if dialog.number_of_lines() == "":
                helper_functions.import_to_qgis(self.iface, dialog.domain(), dialog.dataset_id(), dialog.geom_data_name(),
                                                dialog.params())
                settings.setValue('domain_name_cache', dialog.domain())
            else:
                try:
                    number_of_lines = int(dialog.number_of_lines())
                except ValueError:
                    QtWidgets.QMessageBox.information(None, "ERROR:", "Number of lines has to be an int.")
                    return
                helper_functions.import_to_qgis(self.iface, dialog.domain(), dialog.dataset_id(), dialog.geom_data_name(),
                                                dialog.params(), number_of_lines)
                settings.setValue('domain_name_cache', dialog.domain())
            # TODO : deal with conversion from type to qgsField : do default string and if date works, date ?
            #  but how ? Hoooooooooooow ?
