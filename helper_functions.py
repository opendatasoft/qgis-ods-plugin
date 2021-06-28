import json
import requests

from PyQt5 import QtWidgets
from qgis.PyQt.QtCore import QVariant

V2_QUERY_SIZE_LIMIT = 10000
V2_API_CHUNK_SIZE = 100
JSON_TO_QGIS_TYPES = {"text": QVariant.String, "double": QVariant.Double, "int": QVariant.Int,
                      "boolean": QVariant.Bool, "date": QVariant.String, "datetime": QVariant.DateTime}
# Utiliser date format pour les dates ? Que si on reste sur l'apiv2 et pas sur les exports...
ACCEPTED_GEOMETRY = {"MultiPoint", "MultiLineString", "MultiPolygon", "Point", "LineString", "Polygon"}
ACCEPTED_TYPE = {"geo_point_2d", "geo_shape"}


def create_name_type_dict(dataset_line, metadata):
    name_type_dict = {}
    for name in dataset_line.keys():
        for field in metadata['results'][0]['fields']:
            if name == field['name']:
                name_type_dict[name] = {'json_type': field['type'],
                                        'is_multivalued': "multivalued" in field['annotations']}
    return name_type_dict


def import_dataset(iface, domain_url, dataset_id, params, number_of_lines):
    number_of_lines_left = number_of_lines
    params['limit'] = min(V2_API_CHUNK_SIZE, number_of_lines_left)
    first_query = requests.get(
        "https://{}/api/v2/catalog/datasets/{}/query".format(domain_url, dataset_id), params)
    if first_query.status_code == 404:
        raise DatasetError
    elif first_query.status_code == 400:
        QtWidgets.QMessageBox.information(None, "ERROR:", first_query.json()['message'])
        raise OdsqlError
    number_of_lines_left -= V2_API_CHUNK_SIZE

    params['limit'] = min(V2_API_CHUNK_SIZE, number_of_lines_left)
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    params['offset'] = V2_API_CHUNK_SIZE
    while params['offset'] <= total_count and params['offset'] < V2_QUERY_SIZE_LIMIT - V2_API_CHUNK_SIZE \
            and number_of_lines_left >= 0:
        query = requests.get("https://{}/api/v2/catalog/datasets/{}/query".format(domain_url, dataset_id), params)
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
    try:
        first_query = requests.get("https://{}/api/v2/catalog/query".format(domain_url), params)
        if first_query.status_code == 404:
            raise DomainError
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        raise DomainError
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    params['offset'] = V2_API_CHUNK_SIZE
    query_size_limit = 30000 if domain_url == 'data.opendatasoft.com' else V2_QUERY_SIZE_LIMIT - V2_API_CHUNK_SIZE
    while params['offset'] <= total_count and params['offset'] < query_size_limit:
        query = requests.get("https://{}/api/v2/catalog/query".format(domain_url), params)
        json_dataset['results'] += query.json()['results']
        params['offset'] += V2_API_CHUNK_SIZE
    return json_dataset


def datasets_to_dataset_id_list(json_dataset):
    dataset_id_list = [dataset['dataset_id'] for dataset in json_dataset['results']]
    return dataset_id_list


def import_dataset_metadata(domain_url, dataset_id):
    try:
        query = requests.get("https://{}/api/v2/catalog/query?where=datasetid:'{}'".format(domain_url, dataset_id))
    except requests.exceptions.ConnectionError:
        raise DomainError
    if query.status_code == 404 or query.json()['total_count'] == 0:
        raise DatasetError
    return query.json()


def possible_geom_columns_from_metadata(metadata):
    geom_column_names = []
    for field in metadata['results'][0]['fields']:
        if field['type'] in ACCEPTED_TYPE:
            geom_column_names.append(field['name'])
    return geom_column_names


def create_attributes(name_type_dict):
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsField

    attribute_list = []
    for column_name in name_type_dict.keys():
        if name_type_dict[column_name]['json_type'] not in ACCEPTED_TYPE:
            if name_type_dict[column_name]['is_multivalued']:
                if name_type_dict[column_name]['json_type'] == "text":
                    attribute_list.append(QgsField(column_name, QVariant.StringList))
                else:
                    attribute_list.append(QgsField(column_name, QVariant.List))
            else:
                attribute_list.append(
                    QgsField(column_name, JSON_TO_QGIS_TYPES[name_type_dict[column_name]['json_type']]))
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


def create_feature(name_type_dict, dataset, geom_data_type, geom_data_name, line):
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
    for column_name in name_type_dict.keys():
        if name_type_dict[column_name]['json_type'] not in ACCEPTED_TYPE:
            feature_values.append(dataset['results'][line][column_name])
    feature.setAttributes(feature_values)
    return feature


def import_to_qgis(iface, domain, dataset_id, geom_data_name, params, number_of_lines):
    metadata = import_dataset_metadata(domain, dataset_id)

    # Checks if select is different from select field literal (to remove when types added to dataset)
    name_list = []
    for field in metadata['results'][0]['fields']:
        name_list.append(field['name'])
    if 'select' in params.keys():
        for selected_data in params['select'].replace(", ", ",").split(","):
            if selected_data not in name_list:
                raise SelectError

    if number_of_lines <= 0:
        raise NumberOfLinesError

    dataset = import_dataset(iface, domain, dataset_id, params, number_of_lines)
    name_type_dict = create_name_type_dict(dataset['results'][0], metadata)
    geom_data_type = name_type_dict[geom_data_name]['json_type']

    attribute_list = create_attributes(name_type_dict)
    layer_dict = {}

    if geom_data_type == "geo_point_2d":
        layer = create_layer("Point", dataset_id, attribute_list)
        layer_dict["Point"] = layer
        layer_dict["Point"].startEditing()
        feature_list = []
        for line in range(len(dataset['results'])):
            if dataset["results"][line][geom_data_name] is not None:
                feature = create_feature(name_type_dict, dataset, geom_data_type, geom_data_name, line)
                feature_list.append(feature)

                percent = int(line / float(len(dataset['results']) - 1) * 100)
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
                    feature = create_feature(name_type_dict, dataset, geom_data_type, geom_data_name, line)
                    layer_dict[json_geometry].addFeatures([feature])
                    layer_dict[json_geometry].commitChanges()

                    percent = int(line / float(len(dataset['results']) - 1) * 100)
                    iface.mainWindow().statusBar().showMessage("Filling table {} %".format(percent))
                    QtWidgets.QApplication.processEvents()
                else:
                    raise GeometryError

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


def geojson_geom_column(metadata):
    geom_column_names = []
    for field in metadata['results'][0]['fields']:
        if field['type'] == 'geo_shape':
            geom_column_names.append(field['name'])
    if not geom_column_names:
        for field in metadata['results'][0]['fields']:
            if field['type'] == 'geo_point_2d':
                geom_column_names.append(field['name'])
    if not geom_column_names:
        QtWidgets.QMessageBox.information(None, "ERROR:", "There's no geojson geometry column in this dataset.")
    return geom_column_names


def import_to_qgis_geojson(domain, dataset_id, params, path):
    """progressMessageBar = iface.messageBar().createMessage("HOO HEE HOO HAHA DING DANG WALLA WALLA BING BANG")
    progress = QtWidgets.QProgressBar()
    # progress.setMaximum(10)
    # progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar)"""

    """import qgis.utils
    
    progressMessageBar = qgis.utils.iface.messageBar()
    progressbar = QtWidgets.QProgressBar()
    progressMessageBar.pushWidget(progressbar)
    progressbar.setValue(84)"""
    # TODO ? : https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/communicating.html#showing-progress
    from qgis.core import QgsProject, QgsVectorLayer

    try:
        params_no_limit = dict(params)
        if 'limit' in params_no_limit.keys():
            params_no_limit.pop('limit')
        test_query = requests.get("https://{}/api/v2/catalog/datasets/{}/query".format(domain, dataset_id),
                                  params_no_limit)
        # TODO : tous les 20Mbs, checker cancel, et si cancel, abort (?)
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        raise DomainError
    if test_query.status_code == 404:
        raise DatasetError
    if test_query.status_code == 400:
        QtWidgets.QMessageBox.information(None, "ERROR:", test_query.json()['message'])
        raise OdsqlError

    if 'limit' in params:
        try:
            limit = int(params['limit'])
        except ValueError:
            raise NumberOfLinesError
        if limit < 0:
            raise NumberOfLinesError

    exports = requests.get("https://{}/api/v2/catalog/datasets/{}/exports/geojson".format(domain, dataset_id), params)
    geojson_data = exports.json()
    print(path)
    try:
        with open(path, 'w') as f:
            json.dump(geojson_data, f)
    except FileNotFoundError:
        raise FileNotFoundError
    vector_layer = QgsVectorLayer(path, dataset_id, "ogr")
    QgsProject.instance().addMapLayer(vector_layer)


class DomainError(Exception):
    pass


class OdsqlError(Exception):
    pass


class NumberOfLinesError(Exception):
    pass


class SelectError(Exception):
    pass


class DatasetError(Exception):
    pass


class GeometryError(Exception):
    pass
