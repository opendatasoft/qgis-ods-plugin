# -------------------------------------------------------------------------------------------------------------------------------------
# This file has two functions, each for creating and modifying a layer using the python console of QGIS.
# Each time, you just have to copy the code under the definition, and voilà.
# The first function is a way to create a layer using an existing dataset. The current example uses the Festivals du Finistère dataset.
# The second function is a way to create a layer from scratch, using the memory provider. The current example creates Futurama data.
# -------------------------------------------------------------------------------------------------------------------------------------
from qgis.PyQt.QtCore import QVariant

V2_API_CHUNK_SIZE = 100
JSON_TO_QGIS_TYPES = {"text": QVariant.String, "double": QVariant.Double, "int": QVariant.Int,
                      "boolean": QVariant.Bool, "date": QVariant.Date, "datetime": QVariant.DateTime,
                      "geo_point_2d": QVariant.String}


def create_layer_from_dataset():
    """This script modifies the dataset it uses."""

    # Don't forget to adapt the path to your computer for now
    path_to_festivals = "/Users/venceslas/qgis-ods-plugin/festivals-du-finistere.geojson"

    festival_vlayer = QgsVectorLayer(path_to_festivals, "Festivals du Finistère", "ogr")

    if not festival_vlayer.isValid():
        print("Layer failed to load!")
    else:
        QgsProject.instance().addMapLayer(festival_vlayer)

    feat = QgsFeature(festival_vlayer.fields())
    feat.setAttributes(
        ["29", "2020-05-27", "CE197", "www.brestivaldelachaussette.com", "Annuelle", "PLOUZANE", "Finist\u00e8re", 29.0,
         "BRESTIVAL DE LA CHAUSSETTE", (48.4, -4.6), "2020-05-25", 0.0, 20.0, 21.0, "29280", 5.0,
         "C'est LE festival de la chaussette : amoureux des pieds bien traités, amis du tricot ou encore givrés du "
         "panard, vous y trouverez les dernières nouveautés en matière de chaussette bretonne...",
         "Chaussettes, what else ?", "29280", "Bretagne", "Transdisciplinaire", "1998-01-01", "05 (mai)", "PLOUZANE"])
    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-4.6, 48.4)))
    (res, outFeats) = festival_vlayer.dataProvider().addFeatures([feat])
    if iface.mapCanvas().isCachingEnabled():
        festival_vlayer.triggerRepaint()
    else:
        iface.mapCanvas().refresh()


def create_layer_with_memory_provider():
    """The script dataset is temporary, and will be deleted when you quit QGIS."""

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


def import_dataset(domain_url, dataset_id):
    import requests
    first_query = requests.get(
        "https://{}.opendatasoft.com/api/v2/catalog/datasets/{}/query?limit=100".format(domain_url, dataset_id,
                                                                                        V2_API_CHUNK_SIZE))
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    offset = V2_API_CHUNK_SIZE
    while offset <= total_count:
        query = requests.get(
            "https://{}.opendatasoft.com/api/v2/catalog/datasets/{}/query?limit={}&offset={}".format(domain_url,
                                                                                                     dataset_id,
                                                                                                     V2_API_CHUNK_SIZE,
                                                                                                     offset))
        json_dataset['results'] += query.json()['results']
        offset += 100
    return json_dataset


def import_dataset_list(domain_url):
    import requests
    first_query = requests.get(
        "https://{}.opendatasoft.com/api/v2/catalog/query?limit={}".format(domain_url, V2_API_CHUNK_SIZE))
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    offset = V2_API_CHUNK_SIZE
    while offset <= total_count:
        query = requests.get(
            "https://{}.opendatasoft.com/api/v2/catalog/query?limit={}&offset={}".format(domain_url, V2_API_CHUNK_SIZE,
                                                                                         offset))
        json_dataset['results'] += query.json()['results']
        offset += V2_API_CHUNK_SIZE
    return json_dataset


def import_dataset_metadata(domain_url, dataset_id):
    import requests
    query = requests.get(
        "https://{}.opendatasoft.com/api/v2/catalog/query?where=datasetid:'{}'".format(domain_url, dataset_id))
    return query.json()


def create_layer_old(json_geometry, metadata, geom_data_type, dataset, geom_data_name, attribute_list):
    from qgis.core import (QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsProject)
    from qgis.gui import QgsMapCanvas

    vlayer = QgsVectorLayer(json_geometry, "temporary_dataset_points", "memory")
    vlayer.dataProvider().setEncoding("UTF-8")
    provider = vlayer.dataProvider()
    provider.addAttributes(attribute_list)
    vlayer.updateFields()

    magic_length = len(dataset['results'])
    for i in range(magic_length):
        feature = QgsFeature()
        coordinates = dataset['results'][i][geom_data_name]
        # if geometry is Point, else adapt with right geometry e.g. QgsMultiPolygonXY
        if geom_data_type == "geo_point_2d":
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coordinates['lon'], coordinates['lat'])))
        else:
            print("no geom for you")
        feature_values = []
        for field in metadata["results"][0]["fields"]:
            if field["type"] != geom_data_type:  # if geom attribute is geo_point_2d, else adapt with geo_shape
                feature_values.append(dataset['results'][i][field['name']])

        feature.setAttributes(feature_values)
        provider.addFeatures([feature])

    vlayer.updateExtents()
    QgsProject.instance().addMapLayer(vlayer)
    canvas = QgsMapCanvas()
    canvas.setExtent(vlayer.extent())
    canvas.setLayers([vlayer])


def create_layer(json_geometry, attribute_list):
    from qgis.core import QgsVectorLayer
    layer = QgsVectorLayer(json_geometry, "temporary_dataset_{}".format(json_geometry), "memory")
    layer.dataProvider().setEncoding("UTF-8")
    provider = layer.dataProvider()
    provider.addAttributes(attribute_list)
    layer.updateFields()
    return layer


def fill_layer(layer, metadata, dataset, geom_data_type, geom_data_name, line):
    from qgis.core import (QgsFeature, QgsGeometry, QgsPointXY, QgsMultiPolygon, QgsMultiLineString,
                           QgsMultiPoint, QgsPoint)
    from osgeo import ogr
    import json

    provider = layer.dataProvider()
    feature = QgsFeature()
    geometry = dataset['results'][line][geom_data_name]["geometry"]

    if geom_data_type == "geo_point_2d":
        feature.setGeometry(
            QgsGeometry.fromPointXY(QgsPointXY(geometry["coordinates"]['lon'], geometry["coordinates"]['lat'])))
    else:
        geometry_string = json.dumps(geometry)
        geom = ogr.CreateGeometryFromJson(geometry_string)
        feature.setGeometry(QgsGeometry.fromWkt(geom.ExportToWkt()))
    feature_values = []
    for field in metadata["results"][0]["fields"]:
        if field["type"] != geom_data_type and field["type"] != "geo_point_2d":
            feature_values.append(dataset['results'][line][field['name']])

    feature.setAttributes(feature_values)
    print(feature.attributes(), feature.geometry())
    provider.addFeatures([feature])


def create_attributes(metadata, geom_data_type):
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsField

    attribute_list = []
    for field in metadata["results"][0]["fields"]:
        if field["type"] != geom_data_type and field["type"] != "geo_point_2d":
            if "multivalued" in field["annotations"]:
                if field["type"] == "text":
                    attribute_list.append(QgsField(field["name"], QVariant.StringList))
                else:
                    attribute_list.append(QgsField(field["name"], QVariant.List))
            else:
                attribute_list.append(QgsField(field["name"], JSON_TO_QGIS_TYPES[field["type"]]))
    return attribute_list


def geom_to_multi_geom(geometry):
    if "Multi" not in geometry:
        geometry = "Multi" + geometry
    return geometry
