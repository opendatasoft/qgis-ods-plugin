# -----------------------------------------------------------
# Copyright (C) 2021 Venceslas Roullier/Opendatasoft
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

from PyQt5.QtWidgets import QAction, QMessageBox
from . import pyqgis_script


def classFactory(iface):
    return MinimalPlugin(iface)


class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction('ODS', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        QMessageBox.information(None, 'ODS plugin',
                                "When you press the button, you'll get a new dataset from scratch.")

        from qgis.core import (QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsProject)
        from qgis.PyQt.QtCore import QVariant
        from qgis.gui import QgsMapCanvas

        # DISCLAIMER : only works with Point for now
        vlayer = QgsVectorLayer("Point", "temporary_dataset_points", "memory")
        vlayer.dataProvider().setEncoding("UTF-8")
        provider = vlayer.dataProvider()

        json_to_qgis_types = {"text": QVariant.String, "double": QVariant.Double, "int": QVariant.Int,
                              "boolean": QVariant.Bool, "date": QVariant.Date, "datetime": QVariant.DateTime,
                              "geo_point_2d": QVariant.String}
        attribute_list = []

        metadata = pyqgis_script.import_dataset_metadata("vroullier", "festivals-du-finistere")

        for field in metadata["results"][0]["fields"]:
            if field["type"] != "geo_point_2d":
                if "multivalued" in field["annotations"]:
                    # Only handles list of string
                    attribute_list.append(QgsField(field["name"], QVariant.StringList))
                else:
                    attribute_list.append(QgsField(field["name"], json_to_qgis_types[field["type"]]))
            else:
                point_attribute = field["name"]
        provider.addAttributes(attribute_list)
        vlayer.updateFields()

        json_dataset = pyqgis_script.import_dataset("vroullier","festivals-du-finistere")
        feat = QgsFeature()
        for i in range(json_dataset['total_count']):
            coordinates = json_dataset['results'][i][point_attribute]
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coordinates['lon'], coordinates['lat'])))
            feature_values = []
            for field in metadata["results"][0]["fields"]:
                if field["type"] != "geo_point_2d":
                    feature_values.append(json_dataset['results'][i][field['name']])

            feat.setAttributes(feature_values)
            provider.addFeatures([feat])

        vlayer.updateExtents()

        features = vlayer.getFeatures()
        for fet in features:
            print("F:", fet.id(), fet.attributes(), fet.geometry().asPoint())

        QgsProject.instance().addMapLayer(vlayer)
        canvas = QgsMapCanvas()
        canvas.setExtent(vlayer.extent())
        canvas.setLayers([vlayer])
