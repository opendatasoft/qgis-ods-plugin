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
                number_of_lines = helper_functions.V2_QUERY_SIZE_LIMIT
            else:
                try:
                    number_of_lines = int(dialog.number_of_lines())
                except ValueError:
                    QtWidgets.QMessageBox.information(None, "ERROR:", "Number of lines has to be an int.")
                    return
            try:
                helper_functions.import_to_qgis(self.iface, dialog.domain(), dialog.dataset_id(), dialog.geom_data_name(),
                                                dialog.params(), number_of_lines)
                settings.setValue('domain_name_cache', dialog.domain())
            except helper_functions.OdsqlError:
                pass
            except helper_functions.DatasetError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
            except helper_functions.DomainError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
            except helper_functions.SelectError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "Unauthorized select statement : "
                                                                  "only select field literal is permitted "
                                                                  "or name not in dataset.")
            except helper_functions.NumberOfLinesError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "Number of lines has to be a strictly positive int.")
            except helper_functions.GeometryError:
                QtWidgets.QMessageBox.information(None, "ERROR:",
                                                  "This json geometry isn't valid. Valid geometries are "
                                                  + ", ".join(helper_functions.ACCEPTED_GEOMETRY) + ".")


            # TODO : deal with conversion from type to qgsField : do default string and if date works, date ?
            #  but how ? Hoooooooooooow ?

