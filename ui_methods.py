import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings

from . import helper_functions


class InputDialog(QtWidgets.QDialog):
    def __init__(self, iface):
        super(InputDialog, self).__init__()
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_dir, 'plugin_dialog.ui')
        uic.loadUi(ui_path, self)
        self.iface = iface

        for button in self.dialogButtonBox.buttons():
            button.setDefault(False)
        self.filePathButton.clicked.connect(self.getFilePath)
        self.updateListButton.clicked.connect(self.updateListButtonPressed)
        self.datasetListComboBox.setEditable(True)
        self.datasetListComboBox.currentIndexChanged.connect(self.updateSchemaTable)
        self.dialogButtonBox.accepted.connect(self.importDataset)
        self.show()

    def updateListButtonPressed(self):
        self.datasetListComboBox.clear()
        try:
            dataset_id_list = helper_functions.datasets_to_dataset_id_list(helper_functions.import_dataset_list(
                remove_http(self.domainInput.text())))
            self.datasetListComboBox.addItems(dataset_id_list)
        except helper_functions.DomainError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")

    def updateSchemaTable(self):
        if self.datasetListComboBox.currentText():
            self.schemaTableWidget.setColumnCount(0)
            metadata = helper_functions.import_dataset_metadata(remove_http(self.domainInput.text()),
                                                                self.datasetListComboBox.currentText())
            for field in metadata['results'][0]['fields']:
                column_position = self.schemaTableWidget.columnCount()
                self.schemaTableWidget.insertColumn(column_position)
                self.schemaTableWidget.setItem(0, column_position, QtWidgets.QTableWidgetItem(field['name']))
                self.schemaTableWidget.setItem(1, column_position, QtWidgets.QTableWidgetItem(field['type']))

    def getFilePath(self):
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        fileName = fileDialog.getSaveFileName(self, "Choose save location", "/Users",
                                              "Geojson Files (*.geojson)")
        self.pathInput.setText(fileName[0])

    def path(self):
        return self.pathInput.text()

    def domain(self):
        url = self.domainInput.text()
        return remove_http(url)

    def dataset_id(self):
        return self.datasetListComboBox.currentText()

    def number_of_lines(self):
        return self.numberOfLinesInput.text()

    def params(self):
        params = {}
        if self.selectInput.text():
            select_input = self.selectInput.text()
            if select_input.startswith("select="):
                params['select'] = select_input[len("select="):]
            else:
                params['select'] = select_input
            if '*' in select_input:
                params.pop('select', None)

        if self.whereInput.text():
            where_input = self.whereInput.text()
            if where_input.startswith("where="):
                params['where'] = where_input[len("where="):]
            else:
                params['where'] = where_input

        if self.orderByInput.text():
            order_by_input = self.orderByInput.text()
            if order_by_input.startswith("order_by="):
                params['order_by'] = order_by_input[len("order_by="):]
            else:
                params['order_by'] = order_by_input

        if self.limitInput.text():
            limit_input = self.limitInput.text()
            if limit_input.startswith("limit="):
                params['limit'] = limit_input[len("limit="):]
            else:
                params['limit'] = limit_input
        return params

    def push_ods_cache(self, ods_cache):
        self.domainInput.setText(ods_cache['domain'])
        self.datasetListComboBox.addItems(ods_cache['dataset_id']['items'])
        self.datasetListComboBox.setCurrentIndex(ods_cache['dataset_id']['index'])
        if 'select' in ods_cache['params']:
            self.selectInput.setText(ods_cache['params']['select'])
        if 'where' in ods_cache['params']:
            self.whereInput.setText(ods_cache['params']['where'])
        if 'order_by' in ods_cache['params']:
            self.orderByInput.setText(ods_cache['params']['order_by'])
        if 'limit' in ods_cache['params']:
            self.limitInput.setText(ods_cache['params']['limit'])
        if 'path' in ods_cache:
            self.pathInput.setText(ods_cache['path'])

    def importDataset(self):
        settings = QSettings()
        if self.domain() == "" or self.dataset_id() == "":
            QtWidgets.QMessageBox.information(None, "ERROR:", "Domain and dataset fields must be filled to import a "
                                                              "dataset.")
            return
        path = self.path()
        try:
            helper_functions.import_to_qgis_geojson(self.domain(), self.dataset_id(), self.params(), path)
            all_datasets = [self.datasetListComboBox.itemText(i) for i in range(self.datasetListComboBox.count())]
            dataset_index = self.datasetListComboBox.currentIndex()
            ods_cache = {'domain': self.domain(), 'dataset_id': {'items': all_datasets, 'index': dataset_index},
                         'params': self.params(), 'path': self.path()}
            settings.setValue('ods_cache', ods_cache)
            self.close()
        except helper_functions.OdsqlError:
            pass
        except helper_functions.DomainError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
        except helper_functions.DatasetError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
        except helper_functions.NumberOfLinesError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "Limit has to be a strictly positive int.")
        except FileNotFoundError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "Specified folder path doesn't exist.")
        except PermissionError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "Permission required to write on this file.")


def remove_http(url):
    if url.startswith("https://"):
        return url[len("https://"):]
    elif url.startswith("http://"):
        return url[len("http://"):]
    return url
