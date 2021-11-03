import tempfile

import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, QElapsedTimer

from . import ui_methods

V2_QUERY_SIZE_LIMIT = 10000
V2_API_CHUNK_SIZE = 100


def import_dataset_list(domain_url, apikey, include_non_geo_dataset, text_search_param):
    params = {'limit': V2_API_CHUNK_SIZE, 'order_by': 'dataset_id'}
    if apikey:
        params['apikey'] = apikey
    if text_search_param:
        params['where'] = ['"{}"'.format(text_search_param)]
        params.pop('order_by')
    if not include_non_geo_dataset:
        if 'where' in params:
            params['where'].append("features='geo'")
        else:
            params['where'] = "features='geo'"

    try:
        first_query = requests.get("https://{}/api/v2/catalog/query".format(domain_url), params)
        if first_query.status_code == 500:
            raise InternalError
        if first_query.status_code == 404:
            raise DomainError
        if first_query.status_code == 401:
            raise AccessError
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        raise DomainError
    json_dataset = first_query.json()
    total_count = json_dataset['total_count']
    params['offset'] = V2_API_CHUNK_SIZE
    query_size_limit = 30000 if domain_url == 'data.opendatasoft.com' else V2_QUERY_SIZE_LIMIT - V2_API_CHUNK_SIZE
    while params['offset'] <= total_count and params['offset'] < query_size_limit:
        query = requests.get("https://{}/api/v2/catalog/query".format(domain_url), params)
        if query.status_code == 500:
            raise InternalError
        json_dataset['results'] += query.json()['results']
        params['offset'] += V2_API_CHUNK_SIZE
    return json_dataset


def datasets_to_dataset_id_list(json_dataset):
    dataset_id_list = [dataset['dataset_id'] for dataset in json_dataset['results']]
    return dataset_id_list


def import_dataset_metadata(domain_url, dataset_id, apikey):
    params = {'where': 'datasetid:"{}"'.format(dataset_id)}
    if apikey:
        params['apikey'] = apikey
    try:
        query = requests.get("https://{}/api/v2/catalog/query".format(domain_url), params)
    except requests.exceptions.ConnectionError:
        raise DomainError
    if query.status_code == 404 or query.json()['total_count'] == 0:
        raise DatasetError
    return query.json()


def import_first_record(domain_url, dataset_id, apikey):
    params = {'limit': 1}
    if apikey:
        params['apikey'] = apikey
    try:
        query = requests.get("https://{}/api/v2/catalog/datasets/{}/query".format(domain_url, dataset_id), params)
    except requests.exceptions.ConnectionError:
        raise DomainError
    if query.status_code == 404 or query.json()['total_count'] == 0:
        raise DatasetError
    return query.json()


def get_geom_column(metadata):
    for field in metadata['results'][0]['fields']:
        if field['type'] == 'geo_shape':
            return field['name']
    for field in metadata['results'][0]['fields']:
        if field['type'] == 'geo_point_2d':
            return field['name']
    return None


def create_new_ods_auth_config(apikey):
    from qgis.core import QgsApplication, QgsAuthMethodConfig

    auth_manager = QgsApplication.authManager()
    config = QgsAuthMethodConfig()
    config.setName("ods-cache")
    config.setMethod("EsriToken")
    config.setConfig("token", apikey)
    auth_manager.storeAuthenticationConfig(config)


def remove_ods_auth_config():
    from qgis.core import QgsApplication, QgsAuthMethodConfig

    auth_manager = QgsApplication.authManager()
    config_dict = auth_manager.availableAuthMethodConfigs()
    for authConfig in config_dict.keys():
        if config_dict[authConfig].name() == 'ods-cache':
            auth_manager.removeAuthenticationConfig(authConfig)
            break


def get_apikey_from_cache():
    from qgis.core import QgsApplication, QgsAuthMethodConfig

    auth_manager = QgsApplication.authManager()
    config_dict = auth_manager.availableAuthMethodConfigs()
    apikey = None
    for config in config_dict.values():
        if config.name() == 'ods-cache':
            aux_config = QgsAuthMethodConfig()
            auth_manager.loadAuthenticationConfig(config.id(), aux_config, True)
            apikey = aux_config.configMap()['token']
    return apikey


def import_dataset_to_qgis(domain, dataset_id, params):
    try:
        params_no_limit = dict(params)
        if 'limit' in params_no_limit.keys():
            params_no_limit.pop('limit')
        test_query = requests.get("https://{}/api/v2/catalog/datasets/{}/query".format(domain, dataset_id),
                                  params_no_limit)

    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        raise DomainError
    if test_query.status_code == 404:
        raise DatasetError
    if test_query.status_code == 400:
        QtWidgets.QMessageBox.information(None, "ERROR:", test_query.json()['message'])
        raise OdsqlError
    if test_query.status_code == 401:
        raise AccessError

    if 'limit' in params:
        try:
            limit = int(params['limit'])
        except ValueError:
            raise NumberOfLinesError
        if limit < -1:
            raise NumberOfLinesError

    imported_dataset = requests.get("https://{}/api/v2/catalog/datasets/{}/exports/geojson".format(domain, dataset_id),
                                    params, stream=True)
    return imported_dataset


def load_dataset_to_qgis(path, dataset_id, imported_dataset):
    from qgis.core import QgsProject, QgsVectorLayer

    cancelImportDialog = ui_methods.CancelImportDialog()
    try:
        file_path = path
        if file_path == "":
            file = tempfile.NamedTemporaryFile(suffix='.geojson')
            file.close()
            file_path = file.name
        downloaded = 0
        timer = QElapsedTimer()
        timer.start()
        with open(file_path, 'wb') as f:
            for chunk in imported_dataset.iter_content(chunk_size=1024 * 64):
                f.write(chunk)
                downloaded += len(chunk)
                QCoreApplication.processEvents()
                cancelImportDialog.chunkLabel.setText(
                    'Downloaded: {}MB\nSpeed: {:.2f}kB/s'.format(
                        downloaded // 1024 // 1024,
                        (downloaded / 1024) / (timer.elapsed() / 1000)))
                if cancelImportDialog.isCanceled:
                    return

    except FileNotFoundError:
        raise FileNotFoundError
    except PermissionError:
        raise PermissionError

    vector_layer = QgsVectorLayer(file_path, dataset_id, "ogr")
    QgsProject.instance().addMapLayer(vector_layer)


class DomainError(Exception):
    pass


class OdsqlError(Exception):
    pass


class NumberOfLinesError(Exception):
    pass


class DatasetError(Exception):
    pass


class AccessError(Exception):
    pass


class InternalError(Exception):
    pass
