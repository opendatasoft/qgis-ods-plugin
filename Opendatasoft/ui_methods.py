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
from urllib.parse import urlparse

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QSettings

from . import utils


# noinspection PyPep8Naming
class ODSDialog(QtWidgets.QDialog):
    """
    Main dialog window. Allows the user to:
    - fetch the catalog of datasets for a given Opendatasoft domain
    - select a specific dataset from the catalog
    - add optional SQL-like filters
    - download the dataset locally
    """
    def __init__(self, iface):
        super(ODSDialog, self).__init__()
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_dir, 'plugin_dialog.ui')
        uic.loadUi(ui_path, self)
        self.iface = iface

        for button in self.dialogButtonBox.buttons():
            button.setDefault(False)
            if button.text() == 'OK':
                button.setText('Import dataset')
                button.setEnabled(False)
        self.filePathButton.clicked.connect(self.getFilePath)
        self.datasetLabel.setVisible(False)
        self.datasetListComboBox.setVisible(False)
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
        """
        Fetch datasets list from the remote catalog server.
        """
        self.datasetListComboBox.clear()
        self.datasetListComboBox.addItems(["--Choose a dataset identifier--"])
        try:
            dataset_id_list = utils.datasets_to_dataset_id_list(utils.import_dataset_list(
                self.domain(), self.apikey(), self.nonGeoCheckBox.isChecked(), self.text_search()))
            self.datasetListComboBox.addItems(dataset_id_list)
            self.datasetLabel.setVisible(True)
            self.datasetListComboBox.setVisible(True)
        except utils.DomainError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
        except utils.AccessError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "You need an API key to access this domain or "
                                                              "the apikey to search for datasets is wrong.")
        except utils.InternalError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "InternalError from Opendatasoft while updating dataset list: "
                                                              "contact support@opendatasoft.com for more information.")

    def updateSchemaTable(self):
        """
        Fetch selected dataset metadata and first records in order to fill the schema.
        """
        if self.datasetListComboBox.currentText() and \
                self.datasetListComboBox.currentText() != "--Choose a dataset identifier--":
            self.schemaTableWidget.setColumnCount(0)
            try:
                if self.apikey():
                    metadata = utils.import_dataset_metadata(self.domain(), self.dataset_id(), self.apikey())
                    first_record = utils.import_first_record(self.domain(), self.dataset_id(), self.apikey())
                else:
                    metadata = utils.import_dataset_metadata(self.domain(), self.dataset_id(), None)
                    first_record = utils.import_first_record(self.domain(), self.dataset_id(), None)
                self.datasetNameLabel.setText("Dataset name: {}".format(metadata['results'][0]['metas']['default']['title']))
                self.publisherLabel.setText("Publisher: {}".format(metadata['results'][0]['metas']['default']['publisher']))
                self.recordsNumberLabel.setText("Number of records: {}".format(
                    metadata['results'][0]['metas']['default']['records_count']))
                for field in metadata['results'][0]['fields']:
                    column_position = self.schemaTableWidget.columnCount()
                    self.schemaTableWidget.insertColumn(column_position)
                    self.schemaTableWidget.setItem(0, column_position, QtWidgets.QTableWidgetItem(field['label']))
                    self.schemaTableWidget.setItem(1, column_position, QtWidgets.QTableWidgetItem(field['name']))
                    self.schemaTableWidget.setItem(2, column_position, QtWidgets.QTableWidgetItem(field['type']))
                    first_record_value = first_record['results'][0][field['name']]
                    self.schemaTableWidget.setItem(3, column_position, QtWidgets.QTableWidgetItem(str(first_record_value)))
                    self.schemaTableWidget.resizeColumnsToContents()
                for button in self.dialogButtonBox.buttons():
                    if button.text() == 'Import dataset':
                        button.setEnabled(True)
            except utils.DatasetError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "This dataset is private. "
                                                                  "You need an API key to access it.")
            self.metadataWidget.setVisible(True)
            self.saveWidget.setVisible(True)
            self.clearFilters()
        else:
            if self.datasetListComboBox.currentText() != "--Choose a dataset identifier--":
                self.datasetLabel.setVisible(False)
                self.datasetListComboBox.setVisible(False)

            self.metadataWidget.setVisible(False)
            self.showFilterCheckBox.setChecked(False)
            self.saveWidget.setVisible(False)
            for button in self.dialogButtonBox.buttons():
                if button.text() == 'Import dataset':
                    button.setEnabled(False)
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
        if urlparse(url).scheme:
            # https://data.opendatasoft.com format
            ods_domain_url = urlparse(url).netloc
        else:
            # no scheme, urlparse cannot parse: let's do best effort
            ods_domain_url = url.split('/')[0]
        return ods_domain_url

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
                geom_column_name = utils.get_geom_column(
                    utils.import_dataset_metadata(self.domain(), self.dataset_id(), self.apikey()))
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

        if apikey and ods_cache['store_apikey_in_cache']:
            self.apikeyCacheCheckBox.setChecked(True)
            self.apikeyInput.setText(apikey)
            self.updateListButtonPressed()
            self.datasetListComboBox.setCurrentIndex(ods_cache['dataset_id']['index'])
        else:
            if 'items' in ods_cache['dataset_id']:
                self.datasetLabel.setVisible(True)
                self.datasetListComboBox.setVisible(True)
                self.datasetListComboBox.addItems(ods_cache['dataset_id']['items'])
                self.datasetListComboBox.setCurrentIndex(ods_cache['dataset_id']['index'])
            else:
                self.datasetLabel.setVisible(False)
                self.datasetListComboBox.setVisible(False)
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
        """
        Fetch the selected dataset from remote Opendatasoft catalog
        and add it to the current project as a vector layer.
        """
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
            fetched_dataset = utils.import_dataset_to_qgis(self.domain(), self.dataset_id(), params)
            self.setVisible(False)
            utils.load_dataset_to_qgis(path, self.dataset_id(), fetched_dataset)
            all_datasets = [self.datasetListComboBox.itemText(i) for i in range(self.datasetListComboBox.count())]
            dataset_index = self.datasetListComboBox.currentIndex()

            if self.apikey():
                params.pop('apikey')
                if self.apikey() != utils.get_apikey_from_cache() and self.apikeyCacheCheckBox.isChecked():
                    utils.create_new_ods_auth_config(self.apikey())
            else:
                utils.remove_ods_auth_config()

            ods_cache = {'domain': self.domain(), 'include_non_geo_dataset': self.nonGeoCheckBox.isChecked(),
                         'text_search': self.text_search(),
                         'store_apikey_in_cache': self.apikeyCacheCheckBox.isChecked(),
                         'dataset_id': {'index': dataset_index},
                         'default_geom_column': self.defaultGeomCheckBox.isChecked(),
                         'are_filters_shown': self.showFilterCheckBox.isChecked(),
                         'params': params, 'path': self.path()}

            if not self.apikey():
                ods_cache['dataset_id'] = {'items': all_datasets, 'index': dataset_index}
            settings.setValue('ods_cache', ods_cache)

            self.close()
        except utils.OdsqlError:
            pass
        except utils.DomainError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
        except utils.DatasetError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
        except utils.NumberOfLinesError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "Limit has to be a strictly positive int.")
        except FileNotFoundError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "Specified folder path doesn't exist.")
        except PermissionError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "Permission required to write on this file.")
        except utils.AccessError:
            QtWidgets.QMessageBox.information(None, "ERROR:", "The apikey to access this dataset is wrong.")


# noinspection PyPep8Naming
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
