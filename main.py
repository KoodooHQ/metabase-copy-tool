from metabase_api import Metabase_API
import json


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

#
with open('../../secrets/Config.json', 'r') as f:
    config = json.load(f)

url = config['Metabase']['url']
user = config['Metabase']['username']
password = config['Metabase']['password']

# Setup connection
mb = Metabase_API(url, user, password)
# Add context type to header
mb.header.update({'content-type': 'application/json'})

# Input variables
original_dashboard_id = 27
copy_collection_id = 70
copy_dashboard_name = 'Prod - Decision Engine Performance'
copy_database_id = 7

# TODO Archive previous copy dashboard, charts, and collection for copy charts


# Copy original dashboard and charts
print('Starting dashboard copy')
mb.copy_dashboard(source_dashboard_id=original_dashboard_id, destination_collection_id=copy_collection_id,
                  destination_dashboard_name=copy_dashboard_name, deepcopy=True)
print('Finished dashboard copy')

# Find the ID of the dashboard copy we have just made
# mb.search performs a fuzzy search and returns a list of all matches, after we select the exact dashboard
copy_search = mb.search(q=copy_dashboard_name, item_type='dashboard')
copy_dashboard_data = copy_search[find(copy_search, 'name', copy_dashboard_name)]
copy_dashboard_data_id = copy_dashboard_data['id']

# Create list of chart ids in our copied dashboard
copy_dashboard_get = mb.get(f'/api/dashboard/{copy_dashboard_data_id}')
copy_card_ids = [i['card_id'] for i in copy_dashboard_get['ordered_cards'] if i['card_id'] is not None]

# Update database and field filters for each chart
print('Repointing dashboard charts to new database')
for card_id in copy_card_ids:
    print(f'Updating chart {copy_card_ids.index(card_id)+1} of {len(copy_card_ids)}')

    # Get chart json structure
    chart_json = mb.get(f'/api/card/{card_id}')

    # Check if there is a field filter for this chart
    field_filter_present = check_field_filter_present(chart_json)

    if field_filter_present:
        # Find the id of the field filter for the original database
        # TODO make work for more than 1 field filter named 'Date'
        original_field_filter_id = chart_json['dataset_query']['native']['template-tags']['Date']['dimension'][1]

        # Find the table + column name for the filter field in the original database
        original_db = chart_json['database_id']
        original_db_fields = mb.get(f'/api/database/{original_db}/fields')
        original_field_filter = original_db_fields[find(original_db_fields, 'id', original_field_filter_id)]

        field_table = original_field_filter['table_name']
        field_scheme = original_field_filter['schema']
        field_column = original_field_filter['name']

        # Find the id of the field filter in the new database
        copy_db_fields = mb.get(f'/api/database/{copy_database_id}/fields')
        copy_field_filter_id = copy_db_fields[find3(copy_db_fields, 'table_name', field_table, 'schema', field_scheme, 'name', field_column)]['id']

    # Modify chart json with new database and update field filter ids
    chart_json['database_id'] = copy_database_id
    chart_json['dataset_query']['database'] = copy_database_id
    if field_filter_present:
        chart_json['dataset_query']['native']['template-tags']['Date']['dimension'][1] = copy_field_filter_id

    # Update chart in Metabase
    mb.put(f'/api/card/{card_id}', json=chart_json)

print('Done')
