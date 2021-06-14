import os

from PyQt5 import QtWidgets, uic

import helper_functions


class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super(InputDialog, self).__init__()
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_dir, 'plugin_dialog.ui')
        uic.loadUi(ui_path, self)

        self.domainInput = self.findChild(QtWidgets.QLineEdit, 'domainInput')
        self.updateListButton = self.findChild(QtWidgets.QPushButton, 'updateListButton')
        self.datasetListComboBox = self.findChild(QtWidgets.QComboBox, 'datasetListComboBox')
        self.geomColumnListComboBox = self.findChild(QtWidgets.QComboBox, 'geomColumnListComboBox')

        self.updateListButton.clicked.connect(self.updateListButtonPressed)
        self.datasetListComboBox.currentTextChanged.connect(self.updateGeomColumnListComboBox)

        self.show()

    def updateListButtonPressed(self):
        self.datasetListComboBox.clear()
        self.datasetListComboBox.addItems(
            helper_functions.datasets_to_dataset_id_list(helper_functions.import_dataset_list(self.domainInput.text())))

    def updateGeomColumnListComboBox(self):
        self.geomColumnListComboBox.clear()
        self.geomColumnListComboBox.addItems(
            helper_functions.possible_geom_columns_from_metadata(helper_functions.import_dataset_metadata(
                self.domainInput.text(), self.datasetListComboBox.currentText())))

    def domain(self):
        return self.domainInput.text()

    def dataset_id(self):
        return self.datasetListComboBox.currentText()

    def geom_data_name(self):
        return self.geomColumnListComboBox.currentText()
