#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

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
        QMessageBox.information(None, 'Minimal plugin', "When you press the button, you'll get a new Futurama dataset from scratch.")

        import os
        from qgis.core import (QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY)

        vlayer = QgsVectorLayer("Point", "temporary_futurama_points", "memory")
        provider = vlayer.dataProvider()
        provider.addAttributes([QgsField("name", QVariant.String),
                                QgsField("age", QVariant.Int),
                                QgsField("size", QVariant.Double),
                                QgsField("is_human", QVariant.Bool),
                                QgsField("date_of_birth", QVariant.Date)])

        vlayer.updateFields()

        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 10)))
        feat.setAttributes(["Fry", 30, 1.8, True, "1975-01-21"])
        provider.addFeatures([feat])
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-10, 10)))
        feat.setAttributes(["Farnsworth", 200, 1.2, True, "1990-05-29"])
        provider.addFeatures([feat])
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, -10)))
        feat.setAttributes(["Zoidberg", 50, 1.6, False])
        provider.addFeatures([feat])
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-10, -10)))
        feat.setAttributes(["Bender", 20, 1.8, False, "2100-05-05"])
        provider.addFeatures([feat])

        vlayer.updateExtents()
