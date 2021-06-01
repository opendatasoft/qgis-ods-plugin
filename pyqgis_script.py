def create_layer_from_dataset():
    path_to_festivals = "/Users/venceslas/Documents/pyqgis_plugin/festivals-du-finistere.geojson"

    festival_vlayer = QgsVectorLayer(path_to_festivals, "Festivals du Finistère", "ogr")
    #Regarder provider "memory" (crée une couche vide, etc)

    if not festival_vlayer.isValid():
        print("Layer failed to load!")
    else:
        QgsProject.instance().addMapLayer(festival_vlayer)

    feat = QgsFeature(festival_vlayer.fields())
    feat.setAttributes(["29", "2020-05-27", "CE197", "www.brestivaldelachaussette.com", "Annuelle", "PLOUZANE", "Finist\u00e8re", 29.0,  "BRESTIVAL DE LA CHAUSSETTE", (48.4, -4.6), "2020-05-25", 0.0, 20.0, 21.0, "29280", 5.0, "C'est LE festival de la chaussette : amoureux des pieds bien traités, amis du tricot ou encore givrés du panard, vous y trouverez les dernières nouveautés en matière de chaussette bretonne...", "Chaussettes, what else ?", "29280", "Bretagne","Transdisciplinaire", "1998-01-01", "05 (mai)", "PLOUZANE"])
    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-4.6, 48.4)))
    (res, outFeats) = festival_vlayer.dataProvider().addFeatures([feat])
    if iface.mapCanvas().isCachingEnabled():
        festival_vlayer.triggerRepaint()
    else:
        iface.mapCanvas().refresh()

def create_layer_with_memory_provider():
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