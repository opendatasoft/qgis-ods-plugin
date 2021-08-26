import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QCoreApplication

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
        self.metadataWidget.setVisible(False)
        self.filterGroupBox.setVisible(False)
        self.saveWidget.setVisible(False)
        self.showFilterCheckBox.stateChanged.connect(self.showFilterUI)
        self.resize(self.width(), 0)
        self.updateListButton.clicked.connect(self.updateListButtonPressed)
        self.datasetListComboBox.setEditable(True)
        self.datasetListComboBox.currentIndexChanged.connect(self.updateSchemaTable)
        self.schemaTableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.clearFiltersButton.clicked.connect(self.clearFilters)
        self.dialogButtonBox.accepted.connect(self.importDataset)

        self.show()

    def updateListButtonPressed(self):
        self.datasetListComboBox.clear()
        try:
            dataset_id_list = helper_functions.datasets_to_dataset_id_list(helper_functions.import_dataset_list(
                remove_http(self.domain()), self.apikey(), self.nonGeoCheckBox.isChecked(), self.text_search()))
            self.datasetListComboBox.addItems(dataset_id_list)
        except helper_functions.DomainError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
        except helper_functions.AccessError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "This apikey to search for datasets is wrong.")

    def updateSchemaTable(self):
        if self.datasetListComboBox.currentText():
            self.schemaTableWidget.setColumnCount(0)
            try:
                if self.apikey():
                    metadata = helper_functions.import_dataset_metadata(remove_http(self.domain()), self.dataset_id(),
                                                                        self.apikey())
                else:
                    metadata = helper_functions.import_dataset_metadata(remove_http(self.domain()), self.dataset_id(),
                                                                        None)
                for field in metadata['results'][0]['fields']:
                    column_position = self.schemaTableWidget.columnCount()
                    self.schemaTableWidget.insertColumn(column_position)
                    self.schemaTableWidget.setItem(0, column_position, QtWidgets.QTableWidgetItem(field['label']))
                    self.schemaTableWidget.setItem(1, column_position, QtWidgets.QTableWidgetItem(field['name']))
                    self.schemaTableWidget.setItem(2, column_position, QtWidgets.QTableWidgetItem(field['type']))
            except helper_functions.DatasetError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "This dataset is private. "
                                                                  "You need an API key to access it.")
            self.metadataWidget.setVisible(True)
            self.saveWidget.setVisible(True)
        else:
            self.metadataWidget.setVisible(False)
            self.showFilterCheckBox.setChecked(False)
            self.saveWidget.setVisible(False)
            QCoreApplication.processEvents()
            self.resize(self.width(), 0)

    def showFilterUI(self):
        self.filterGroupBox.setVisible(self.showFilterCheckBox.isChecked())
        if not self.showFilterCheckBox.isChecked():
            QCoreApplication.processEvents()
            self.resize(self.width(), 0)

    def clearFilters(self):
        self.selectInput.setText('')
        self.whereInput.setText('')
        self.orderByInput.setText('')
        self.limitInput.setText('')

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

    def apikey(self):
        if self.apikeyInput.text():
            return self.apikeyInput.text()
        return None

    def text_search(self):
        if self.textSearchInput.text():
            return self.textSearchInput.text()
        return None

    def dataset_id(self):
        return self.datasetListComboBox.currentText()

    def params(self):
        params = {}
        if self.selectInput.text():
            select_input = self.selectInput.text()
            if select_input.startswith("select="):
                params['select'] = select_input[len("select="):]
            else:
                params['select'] = select_input
            if self.defaultGeomCheckBox.isChecked():
                geom_column_name = helper_functions.get_geom_column(
                    helper_functions.import_dataset_metadata(self.domain(), self.dataset_id(), self.apikey()))
                if geom_column_name:
                    if geom_column_name not in params['select']:
                        params['select'] += ',' + geom_column_name
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

    def push_ods_cache(self, ods_cache, apikey):
        self.domainInput.setText(ods_cache['domain'])
        if ods_cache['text_search']:
            self.textSearchInput.setText(ods_cache['text_search'])
        self.nonGeoCheckBox.setChecked(ods_cache['include_non_geo_dataset'])
        self.showFilterCheckBox.setChecked(ods_cache['are_filters_shown'])
        self.defaultGeomCheckBox.setChecked(ods_cache['default_geom_column'])
        if apikey:
            if ods_cache['store_apikey_in_cache']:
                self.apikeyCacheCheckBox.setChecked(True)
                self.apikeyInput.setText(apikey)
                self.updateListButtonPressed()
                self.datasetListComboBox.setCurrentIndex(ods_cache['dataset_id']['index'])
        else:
            if 'dataset_id' in ods_cache:
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
        if self.showFilterCheckBox.isChecked():
            params = self.params()
        else:
            params = {}
        if self.apikey():
            params['apikey'] = self.apikey()
        try:
            imported_dataset = helper_functions.import_dataset_to_qgis(self.domain(), self.dataset_id(), params)
            self.setVisible(False)
            helper_functions.load_dataset_to_qgis(path, self.dataset_id(), imported_dataset)
            all_datasets = [self.datasetListComboBox.itemText(i) for i in range(self.datasetListComboBox.count())]
            dataset_index = self.datasetListComboBox.currentIndex()

            if self.apikey():
                params.pop('apikey')
                if self.apikey() != helper_functions.get_apikey_from_cache() and self.apikeyCacheCheckBox.isChecked():
                    helper_functions.create_new_ods_auth_config(self.apikey())
            else:
                helper_functions.remove_ods_auth_config()

            ods_cache = {'domain': self.domain(), 'include_non_geo_dataset': self.nonGeoCheckBox.isChecked(),
                         'text_search': self.text_search(),
                         'store_apikey_in_cache': self.apikeyCacheCheckBox.isChecked(),
                         'dataset_id': {'index': dataset_index},
                         'default_geom_column': self.defaultGeomCheckBox.isChecked(),
                         'are_filters_shown': self.showFilterCheckBox.isChecked(),
                         'params': params, 'path': self.path()}

            if not self.apikey():
                ods_cache['dataset_id']['items'] = all_datasets
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
        except helper_functions.AccessError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "The apikey to access this dataset is wrong.")


class CancelImportDialog(QtWidgets.QDialog):
    def __init__(self):
        super(CancelImportDialog, self).__init__()
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_dir, 'cancel_import.ui')
        uic.loadUi(ui_path, self)

        self.isCanceled = False
        self.cancelButton.clicked.connect(self.cancelImport)

        self.show()

    def cancelImport(self):
        self.isCanceled = True


def remove_http(url):
    if url.startswith("https://"):
        return url[len("https://"):]
    elif url.startswith("http://"):
        return url[len("http://"):]
    return url
