from PyQt5 import QtWidgets
from qgis.PyQt.QtCore import QVariant

V2_QUERY_SIZE_LIMIT = 10000
V2_API_CHUNK_SIZE = 100
JSON_TO_QGIS_TYPES = {"text": QVariant.String, "double": QVariant.Double, "int": QVariant.Int,
                      "boolean": QVariant.Bool, "date": QVariant.String, "datetime": QVariant.DateTime}
# Utiliser date format pour les dates ? Que si on reste sur l'apiv2 et pas sur les exports...
ACCEPTED_GEOMETRY = {"MultiPoint", "MultiLineString", "MultiPolygon", "Point", "LineString", "Polygon"}
ACCEPTED_TYPE = {"geo_point_2d", "geo_shape"}


# TODO : select il faut boucler sur metadata pour créer un dict (name type)
#  et créer les attributs à partir de ligne 1 du dataset


def import_dataset(iface, domain_url, dataset_id, params, number_of_lines):
    import requests
    number_of_lines_left = number_of_lines
    params['limit'] = min(V2_API_CHUNK_SIZE, number_of_lines_left)
    first_query = requests.get(
        "https://{}/api/v2/catalog/datasets/{}/query".format(domain_url, dataset_id), params)
    if first_query.status_code == 404:
        QtWidgets.QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
        return
    elif first_query.status_code == 400:
        QtWidgets.QMessageBox.information(None, "ERROR:", "One of your odsql statement is malformed.")
        return
    number_of_lines_left -= V2_API_CHUNK_SIZE

    params['limit'] = min(V2_API_CHUNK_SIZE, number_of_lines_left)
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    params['offset'] = V2_API_CHUNK_SIZE
    while params['offset'] <= total_count and params['offset'] < V2_QUERY_SIZE_LIMIT - V2_API_CHUNK_SIZE \
            and number_of_lines_left >= 0:
        query = requests.get(
            "https://{}/api/v2/catalog/datasets/{}/query".format(domain_url, dataset_id), params)
        json_dataset['results'] += query.json()['results']
        params['offset'] += V2_API_CHUNK_SIZE
        number_of_lines_left -= V2_API_CHUNK_SIZE
        params['limit'] = min(V2_API_CHUNK_SIZE, number_of_lines_left)

        percent = int(params['offset'] / number_of_lines * 100)
        iface.mainWindow().statusBar().showMessage("Importing dataset {} %".format(percent))
        QtWidgets.QApplication.processEvents()
    return json_dataset


def import_dataset_list(domain_url):
    params = {'limit': V2_API_CHUNK_SIZE}
    import requests
    try:
        first_query = requests.get(
            "https://{}/api/v2/catalog/query".format(domain_url))
    except requests.exceptions.ConnectionError:
        QtWidgets.QMessageBox.information(None, "ERROR:", "This domain does not exist.")
        return
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    params['offset'] = V2_API_CHUNK_SIZE
    while params['offset'] <= total_count and params['offset'] < V2_QUERY_SIZE_LIMIT - V2_API_CHUNK_SIZE:
        query = requests.get(
            "https://{}/api/v2/catalog/query".format(domain_url))
        json_dataset['results'] += query.json()['results']
        params['offset'] += V2_API_CHUNK_SIZE
    return json_dataset


def datasets_to_dataset_id_list(json_dataset):
    dataset_id_list = [dataset['dataset_id'] for dataset in json_dataset['results']]
    return dataset_id_list


def import_dataset_metadata(domain_url, dataset_id):
    import requests
    query = requests.get(
        "https://{}/api/v2/catalog/query?where=datasetid:'{}'".format(domain_url, dataset_id))
    if query.status_code == 404:
        QtWidgets.QMessageBox.information(None, "ERROR:", "The dataset you want does not exist on this domain.")
        return
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


def create_layer(json_geometry, dataset_id, attribute_list):
    from qgis.core import QgsVectorLayer
    layer = QgsVectorLayer(json_geometry, dataset_id + "_" + json_geometry, "memory")
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


def import_to_qgis(iface, domain, dataset_id, geom_data_name, params, number_of_lines=V2_QUERY_SIZE_LIMIT):
    metadata = import_dataset_metadata(domain, dataset_id)
    if number_of_lines <= 0:
        QtWidgets.QMessageBox.information(None, "ERROR:", "Number of lines has to be a strictly positive int.")
        return
    dataset = import_dataset(iface, domain, dataset_id, params, number_of_lines)

    geom_data_type = ""
    for column in metadata["results"][0]["fields"]:
        if column["name"] == geom_data_name:
            geom_data_type = column["type"]

    attribute_list = create_attributes(metadata)
    layer_dict = {}

    if geom_data_type == "geo_point_2d":
        layer = create_layer("Point", dataset_id, attribute_list)
        layer_dict["Point"] = layer
        layer_dict["Point"].startEditing()
        feature_list = []
        for line in range(len(dataset['results'])):
            if dataset["results"][line][geom_data_name] is not None:
                feature = create_feature(metadata, dataset, geom_data_type, geom_data_name, line)
                feature_list.append(feature)

                percent = int(line / float(len(dataset['results'])-1) * 100)
                iface.statusBarIface().showMessage("Filling table {} %".format(percent))
                QtWidgets.QApplication.processEvents()
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
                        layer = create_layer(json_geometry, dataset_id, attribute_list)
                        layer_dict[json_geometry] = layer
                    layer_dict[json_geometry].startEditing()
                    feature = create_feature(metadata, dataset, geom_data_type, geom_data_name, line)
                    layer_dict[json_geometry].addFeatures([feature])
                    layer_dict[json_geometry].commitChanges()

                    percent = int(line / float(len(dataset['results']) - 1) * 100)
                    iface.mainWindow().statusBar().showMessage("Filling table {} %".format(percent))
                    QtWidgets.QApplication.processEvents()
                else:
                    QtWidgets.QMessageBox.information(None, "ERROR:",
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
