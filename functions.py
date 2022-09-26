import json
from metabase_api import Metabase_API


# Access secrets file and setup connection
def metabase_connection(secrets_path):
    # Load secrets
    with open(secrets_path, 'r') as f:
        config = json.load(f)
    url = config['Metabase']['url']
    user = config['Metabase']['username']
    password = config['Metabase']['password']

    # Setup connection
    mb = Metabase_API(url, user, password)
    # Add context type to header, required for put requests
    mb.header.update({'content-type': 'application/json'})

    return mb


# Finds the index of a list of dictionary, based on a value in the dictionaries
def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


# TODO have one find functions, that can handle 1 or more keys value pairs
def find3(lst, key1, value1, key2, value2, key3, value3):
    for i, dic in enumerate(lst):
        if (dic[key1] == value1) & (dic[key2] == value2) & (dic[key3] == value3):
            return i
    return -1


# Check if chart uses a field filter
def check_field_filter_present(chart_json):
    try:
        x = chart_json['dataset_query']['native']['template-tags']['Date']['dimension']
        return True
    except KeyError:
        return False
