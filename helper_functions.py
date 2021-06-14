# -------------------------------------------------------------------------------------------------------------------------------------
# TODO : UPDATE DESCRIPTION
# -------------------------------------------------------------------------------------------------------------------------------------
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QVariant

V2_QUERY_SIZE_LIMIT = 10000
V2_API_CHUNK_SIZE = 100
JSON_TO_QGIS_TYPES = {"text": QVariant.String, "double": QVariant.Double, "int": QVariant.Int,
                      "boolean": QVariant.Bool, "date": QVariant.String, "datetime": QVariant.DateTime}
# Utiliser date format pour les dates ? Que si on reste sur l'apiv2 et pas sur les exports...
ACCEPTED_GEOMETRY = {"MultiPoint", "MultiLineString", "MultiPolygon", "Point", "LineString", "Polygon"}
ACCEPTED_TYPE = {"geo_point_2d", "geo_shape"}


def import_dataset(domain_url, dataset_id):
    import requests
    first_query = requests.get(
        "https://{}/api/v2/catalog/datasets/{}/query?limit=100".format(domain_url, dataset_id,
                                                                       V2_API_CHUNK_SIZE))
    if first_query.status_code == 404:
        QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
        raise ValueError("The dataset you want does not exist on this domain.")
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    offset = V2_API_CHUNK_SIZE
    while offset <= total_count and offset < V2_QUERY_SIZE_LIMIT - V2_API_CHUNK_SIZE:
        query = requests.get(
            "https://{}/api/v2/catalog/datasets/{}/query?limit={}&offset={}".format(domain_url,
                                                                                    dataset_id,
                                                                                    V2_API_CHUNK_SIZE,
                                                                                    offset))
        json_dataset['results'] += query.json()['results']
        offset += V2_API_CHUNK_SIZE
    return json_dataset


def import_dataset_list(domain_url):
    import requests
    try:
        first_query = requests.get(
            "https://{}/api/v2/catalog/query?limit={}".format(domain_url, V2_API_CHUNK_SIZE))
    except requests.exceptions.ConnectionError:
        QMessageBox.information(None, "ERROR:", "This domain does not exist.")
        raise
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    offset = V2_API_CHUNK_SIZE
    while offset <= total_count and offset < V2_QUERY_SIZE_LIMIT - V2_API_CHUNK_SIZE:
        query = requests.get(
            "https://{}/api/v2/catalog/query?limit={}&offset={}".format(domain_url, V2_API_CHUNK_SIZE,
                                                                        offset))
        json_dataset['results'] += query.json()['results']
        offset += V2_API_CHUNK_SIZE
    return json_dataset


def datasets_to_dataset_id_list(json_dataset):
    dataset_id_list = [dataset['dataset_id'] for dataset in json_dataset['results']]
    return dataset_id_list


def import_dataset_metadata(domain_url, dataset_id):
    import requests
    query = requests.get(
        "https://{}/api/v2/catalog/query?where=datasetid:'{}'".format(domain_url, dataset_id))
    if query.status_code == 404:
        QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
        raise ValueError("The dataset you want does not exist on this domain.")
    return query.json()


def possible_geom_columns_from_metadata(metadata):
    geom_column_names = []
    for field in metadata['results'][0]['fields']:
        if field['type'] in ACCEPTED_TYPE:
            geom_column_names.append(field['name'])
    return geom_column_names


def create_attributes(metadata):
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsField

    attribute_list = []
    for field in metadata['results'][0]['fields']:
        if field['type'] not in ACCEPTED_TYPE:
            if "multivalued" in field['annotations']:
                if field['type'] == "text":
                    attribute_list.append(QgsField(field['name'], QVariant.StringList))
                else:
                    attribute_list.append(QgsField(field['name'], QVariant.List))
            else:
                attribute_list.append(QgsField(field['name'], JSON_TO_QGIS_TYPES[field["type"]]))
    return attribute_list


def geom_to_multi_geom(geometry):
    if "Multi" not in geometry:
        geometry = "Multi" + geometry
    return geometry


def create_layer(json_geometry, attribute_list):
    from qgis.core import QgsVectorLayer
    layer = QgsVectorLayer(json_geometry, "temporary_dataset_{}".format(json_geometry), "memory")
    layer.dataProvider().setEncoding("UTF-8")
    provider = layer.dataProvider()
    provider.addAttributes(attribute_list)
    layer.updateFields()
    return layer


def create_feature(metadata, dataset, geom_data_type, geom_data_name, line):
    from qgis.core import (QgsFeature, QgsGeometry, QgsPointXY)
    from osgeo import ogr
    import json

    feature = QgsFeature()

    if geom_data_type == "geo_point_2d":
        geometry = dataset['results'][line][geom_data_name]
        feature.setGeometry(
            QgsGeometry.fromPointXY(QgsPointXY(geometry['lon'], geometry['lat'])))
    else:
        geometry = dataset['results'][line][geom_data_name]["geometry"]
        geometry_string = json.dumps(geometry)
        geom = ogr.CreateGeometryFromJson(geometry_string)
        feature.setGeometry(QgsGeometry.fromWkt(geom.ExportToWkt()))

    feature_values = []
    for field in metadata["results"][0]["fields"]:
        if field["type"] not in ACCEPTED_TYPE:
            feature_values.append(dataset['results'][line][field['name']])
    feature.setAttributes(feature_values)
    return feature


def import_to_qgis(domain, dataset_id, geom_data_name):
    metadata = import_dataset_metadata(domain, dataset_id)
    dataset = import_dataset(domain, dataset_id)

    geom_data_type = ""
    for column in metadata["results"][0]["fields"]:
        if column["name"] == geom_data_name:
            geom_data_type = column["type"]

    attribute_list = create_attributes(metadata)
    layer_dict = {}

    if geom_data_type == "geo_point_2d":
        layer = create_layer("Point", attribute_list)
        layer_dict["Point"] = layer
        layer_dict["Point"].startEditing()
        feature_list = []
        for line in range(dataset["total_count"]):
            feature = create_feature(metadata, dataset, geom_data_type, geom_data_name, line)
            feature_list.append(feature)
        layer_dict["Point"].addFeatures(feature_list)
        layer_dict["Point"].commitChanges()
    elif geom_data_type == "geo_shape":
        geometry_set = set()
        for line in range(len(dataset["results"])):
            if dataset["results"][line][geom_data_name] is not None:
                json_geometry = dataset["results"][line][geom_data_name]["geometry"]["type"]
                json_geometry = geom_to_multi_geom(json_geometry)
                if json_geometry in ACCEPTED_GEOMETRY:
                    if json_geometry not in geometry_set:
                        geometry_set.add(json_geometry)
                        layer = create_layer(json_geometry, attribute_list)
                        layer_dict[json_geometry] = layer
                    layer_dict[json_geometry].startEditing()
                    feature = create_feature(metadata, dataset, geom_data_type, geom_data_name, line)
                    layer_dict[json_geometry].addFeatures([feature])
                    layer_dict[json_geometry].commitChanges()
                else:
                    QMessageBox.information(None, "ERROR:",
                                            "This json geometry isn't valid. Valid geometries are "
                                            + ", ".join(ACCEPTED_GEOMETRY) + ".")

    for layer in layer_dict.values():
        layer.updateExtents()

    from qgis.core import QgsProject
    from qgis.gui import QgsMapCanvas
    for layer in layer_dict.values():
        QgsProject.instance().addMapLayer(layer)
    canvas = QgsMapCanvas()
    for layer in layer_dict.values():
        canvas.setExtent(layer.extent())
        canvas.setLayers([layer])
