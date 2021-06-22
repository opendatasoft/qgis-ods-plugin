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
        self.queryButton.toggled.connect(self.endpoint)
        self.exportsButton.toggled.connect(self.endpoint)
        self.updateListButton.clicked.connect(self.updateListButtonPressed)
        self.datasetListComboBox.setEditable(True)
        self.datasetListComboBox.currentIndexChanged.connect(self.updateGeomColumnListComboBox)
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

    def updateGeomColumnListComboBox(self):
        if self.datasetListComboBox.currentText():
            self.geomColumnListComboBox.clear()
            if self.queryButton.isChecked():
                try:
                    geom_column_list = helper_functions.possible_geom_columns_from_metadata(helper_functions.
                        import_dataset_metadata(
                        remove_http(self.domainInput.text()), self.datasetListComboBox.currentText()))
                    self.geomColumnListComboBox.addItems(geom_column_list)
                except helper_functions.DatasetError:
                    QtWidgets.QMessageBox.information(None, "ERROR:",
                                                      "The dataset you want does not exist on this domain.")
            elif self.exportsButton.isChecked():
                try:
                    geom_column_list = helper_functions.geojson_geom_column(
                        helper_functions.import_dataset_metadata(remove_http(self.domainInput.text()),
                                                                 self.datasetListComboBox.currentText()))
                    self.geomColumnListComboBox.addItems(geom_column_list)
                except helper_functions.DatasetError:
                    QtWidgets.QMessageBox.information(None, "ERROR:",
                                                      "The dataset you want does not exist on this domain.")

    def endpoint(self):
        endpoint = 'query'
        if self.queryButton.isChecked():
            endpoint = 'query'
            self.ui_to_query()
            self.updateGeomColumnListComboBox()
        elif self.exportsButton.isChecked():
            endpoint = 'exports'
            self.ui_to_exports()
            self.updateGeomColumnListComboBox()
        return endpoint

    def ui_to_query(self):
        self.geometryLabel.setText("Column containing the geometry :")
        self.numberOfLinesLabel.setText("Number of lines you want (default all lines,\nor 10000 if dataset is bigger "
                                        "than that) :")
        self.geomColumnListComboBox.setEnabled(True)

    def ui_to_exports(self):
        self.geometryLabel.setText("Geojson determines geometry by itself")
        self.numberOfLinesLabel.setText("Number of lines you want :")
        self.geomColumnListComboBox.setDisabled(True)

    def domain(self):
        url = self.domainInput.text()
        return remove_http(url)

    def dataset_id(self):
        return self.datasetListComboBox.currentText()

    def geom_data_name(self):
        return self.geomColumnListComboBox.currentText()

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
            if self.geomColumnListComboBox.currentText() not in select_input:
                params['select'] += ", " + self.geomColumnListComboBox.currentText()
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
        return params

    def push_ods_cache(self, ods_cache):
        if ods_cache['endpoint'] == 'query':
            self.queryButton.setChecked(True)
        elif ods_cache['endpoint'] == 'exports':
            self.exportsButton.setChecked(True)
        self.domainInput.setText(ods_cache['domain'])
        self.datasetListComboBox.addItems(ods_cache['dataset_id']['items'])
        self.datasetListComboBox.setCurrentIndex(ods_cache['dataset_id']['index'])
        self.geomColumnListComboBox.setCurrentIndex(ods_cache['geom_column_index'])
        if 'select' in ods_cache['params'].keys():
            self.selectInput.setText(ods_cache['params']['select'])
        if 'where' in ods_cache['params'].keys():
            self.whereInput.setText(ods_cache['params']['where'])
        if 'order_by' in ods_cache['params'].keys():
            self.orderByInput.setText(ods_cache['params']['order_by'])
        self.numberOfLinesInput.setText(str(ods_cache['number_of_lines']))

    def importDataset(self):
        settings = QSettings()
        if self.domain() == "" or self.dataset_id() == "" or self.geom_data_name() == "":
            QtWidgets.QMessageBox.information(None, "ERROR:", "All fields must be filled to import a dataset.")
            return
        if self.endpoint() == 'query':
            if self.number_of_lines() == "":
                number_of_lines = helper_functions.V2_QUERY_SIZE_LIMIT
            else:
                try:
                    number_of_lines = int(self.number_of_lines())
                except ValueError:
                    QtWidgets.QMessageBox.information(None, "ERROR:", "Number of lines has to be an int.")
                    return
            try:
                helper_functions.import_to_qgis(self.iface, self.domain(), self.dataset_id(),
                                                self.geom_data_name(),
                                                self.params(), number_of_lines)
                all_datasets = [self.datasetListComboBox.itemText(i) for i in range(self.datasetListComboBox.count())]
                dataset_index = self.datasetListComboBox.currentIndex()
                geom_column_index = self.geomColumnListComboBox.currentIndex()
                ods_cache = {'domain': self.domain(), 'dataset_id': {'items': all_datasets, 'index': dataset_index},
                             'geom_column_index': geom_column_index, 'params': self.params(),
                             'number_of_lines': number_of_lines, 'endpoint': 'query'}
                settings.setValue('ods_cache', ods_cache)
                self.close()
            except helper_functions.OdsqlError:
                pass
            except helper_functions.DomainError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
            except helper_functions.DatasetError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
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
        else:
            params = self.params()
            if self.number_of_lines():
                params['limit'] = self.number_of_lines()
            try:
                helper_functions.import_to_qgis_geojson(self.domain(), self.dataset_id(), params)
                all_datasets = [self.datasetListComboBox.itemText(i) for i in range(self.datasetListComboBox.count())]
                dataset_index = self.datasetListComboBox.currentIndex()
                geom_column_index = self.geomColumnListComboBox.currentIndex()
                ods_cache = {'domain': self.domain(), 'dataset_id': {'items': all_datasets, 'index': dataset_index},
                             'geom_column_index': geom_column_index, 'params': self.params(),
                             'number_of_lines': self.number_of_lines(), 'endpoint': 'exports'}
                settings.setValue('ods_cache', ods_cache)
                self.close()
            except helper_functions.OdsqlError:
                pass
            except helper_functions.DomainError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
            except helper_functions.DatasetError:
                QtWidgets.QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")


def remove_http(url):
    if url.startswith("https://"):
        return url[len("https://"):]
    elif url.startswith("http://"):
        return url[len("http://"):]
    return url
