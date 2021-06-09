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

        # Input : name of the column that contains the geometry (either geo_point_2d or geo_shape)
        geom_data_name = "geo_shape"

        metadata = pyqgis_script.import_dataset_metadata("vroullier", "provinces-and-territories-canada")
        dataset = pyqgis_script.import_dataset("vroullier", "provinces-and-territories-canada")

        for column in metadata["results"][0]["fields"]:
            if column["name"] == geom_data_name:
                geom_data_type = column["type"]
            # TODO check if geo_shape or geo_point_2d

        attribute_list = pyqgis_script.create_attributes(metadata, geom_data_type)

        if geom_data_type == "geo_point_2d":
            pyqgis_script.create_layer_old("Point", metadata, geom_data_type, dataset, geom_data_name,
                                           attribute_list)
        elif geom_data_type == "geo_shape":
            geometry_set = set()
            layer_dict = {}
            for line in range(dataset["total_count"]):
                json_geometry = dataset["results"][line][geom_data_name]["geometry"]["type"]
                json_geometry = pyqgis_script.geom_to_multi_geom(json_geometry)
                # TODO : check if json_geometry in accepted geometries, namely MultiPolygon, MultiLineString, MultiPoint
                if json_geometry not in geometry_set:
                    geometry_set.add(json_geometry)
                    layer = pyqgis_script.create_layer(json_geometry, attribute_list)
                    layer_dict[json_geometry] = layer
                    # TODO : else : not an accepted geojson geom, exception
                pyqgis_script.fill_layer(layer_dict[json_geometry], metadata, dataset, geom_data_type, geom_data_name,
                                         line)

            features = layer_dict["MultiPolygon"].getFeatures()
            for feat in features:
                print("F:", feat.id(), feat.attributes(), feat.geometry())

            for layer in layer_dict.values():
                layer.updateExtents()

            features = layer_dict["MultiPolygon"].getFeatures()
            for feat in features:
                print("F:", feat.id(), feat.attributes(), feat.geometry())

            from qgis.core import QgsProject
            from qgis.gui import QgsMapCanvas
            QgsProject.instance().addMapLayer(layer_dict["MultiPolygon"])
            canvas = QgsMapCanvas()
            canvas.setExtent(layer_dict["MultiPolygon"].extent())
            canvas.setLayers([layer_dict["MultiPolygon"]])
