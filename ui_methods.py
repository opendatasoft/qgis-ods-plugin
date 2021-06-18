import os

from PyQt5 import QtWidgets, uic

from . import helper_functions


class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super(InputDialog, self).__init__()
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_dir, 'plugin_dialog.ui')
        uic.loadUi(ui_path, self)

        self.updateListButton.clicked.connect(self.updateListButtonPressed)
        self.datasetListComboBox.currentTextChanged.connect(self.updateGeomColumnListComboBox)

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
            self.geomColumnListComboBox.addItems(
                helper_functions.possible_geom_columns_from_metadata(helper_functions.import_dataset_metadata(
                    remove_http(self.domainInput.text()), self.datasetListComboBox.currentText())))

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

    def push_last_domain(self, domain):
        self.domainInput.setText(domain)


def remove_http(url):
    if url.startswith("https://"):
        return url[len("https://"):]
    elif url.startswith("http://"):
        return url[len("http://"):]
    return url
