import requests
from PyQt5 import QtWidgets

V2_QUERY_SIZE_LIMIT = 10000
V2_API_CHUNK_SIZE = 100


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


def import_to_qgis_geojson(domain, dataset_id, params, path):
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
        if limit < -1:
            raise NumberOfLinesError

    exports = requests.get("https://{}/api/v2/catalog/datasets/{}/exports/geojson".format(domain, dataset_id), params,
                           stream=True)
    # TODO : add exception when can't write on file PermissionError
    try:
        with open(path, 'wb') as f:
            for chunk in exports.iter_content(chunk_size=None):
                f.write(chunk)
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


class DatasetError(Exception):
    pass
