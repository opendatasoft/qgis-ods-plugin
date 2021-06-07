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

        # REMOVE DEF AFTER IMPORT PROBLEM SOLVED
        # function imports don't seem to work, so we put the definition here for now
        def import_dataset_metadata(domain_url, dataset_id):
            import requests
            query = requests.get(
                "https://{}.opendatasoft.com/api/v2/catalog/query?where=datasetid:'{}'".format(domain_url, dataset_id))
            return query.json()

        metadata = import_dataset_metadata("vroullier", "festivals-du-finistere")

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

        # REMOVE DEF AFTER IMPORT PROBLEM SOLVED
        # function imports don't seem to work, so we put the definition here for now
        def import_dataset(domain_url, dataset_id):
            import requests
            first_query = requests.get(
                "https://{}.opendatasoft.com/api/v2/catalog/datasets/{}/query?limit=100".format(domain_url, dataset_id))
            json_dataset = first_query.json()
            total_count = json_dataset['total_count']
            offset = 100
            while offset <= total_count:
                query = requests.get(
                    "https://{}.opendatasoft.com/api/v2/catalog/datasets/{}/query?limit=100&offset={}".format(
                        domain_url, dataset_id, offset))
                json_dataset['results'] += query.json()['results']
                offset += 100
            return json_dataset

        json_dataset = import_dataset("vroullier","festivals-du-finistere")
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
