import json
from metabase_api import Metabase_API
from supporting_functions import *


# Access secrets file and setup connection
def get_metabase_connection(secrets_path):
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


# Archive previously copied dashboard, charts, and collection containing copied charts if they exist
def archive_dashboard(metabase_connection, copy_collection_id):
    print('Checking for dashboard/collection to archive')
    try:
        # Find ids of dashboard and folder inside copy collection
        previous_copy_collection_get = metabase_connection.get(f'/api/collection/{copy_collection_id}/items')['data']
        previous_copy_dashboard_id = \
            previous_copy_collection_get[find(previous_copy_collection_get, 'model', 'dashboard')]['id']
        previous_copy_chart_folder_id = \
            previous_copy_collection_get[find(previous_copy_collection_get, 'model', 'collection')]['id']
        # Archive ids
        metabase_connection.move_to_archive('dashboard', item_id=previous_copy_dashboard_id)
        metabase_connection.move_to_archive('collection',
                                            item_id=previous_copy_chart_folder_id)  # Will also archive all charts inside
        print('Archive process successful')
    except:
        print('No dashboard/collection found to be archived')


# Update database and field filters for each chart
def repoint_copied_charts(mb, copy_dashboard_name, copy_database_id):
    print('Repointing dashboard charts to new database')

    # Create list of chart ids from the copied dashboard
    copy_card_ids = dashboard_card_ids(mb, copy_dashboard_name)

    for card_id in copy_card_ids:
        print(f'Updating chart {copy_card_ids.index(card_id) + 1} of {len(copy_card_ids)}')

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
            copy_field_filter_id = \
                copy_db_fields[
                    find3(copy_db_fields, 'table_name', field_table, 'schema', field_scheme, 'name', field_column)][
                    'id']

        # Modify chart json with new database and update field filter ids
        chart_json['database_id'] = copy_database_id
        chart_json['dataset_query']['database'] = copy_database_id
        if field_filter_present:
            chart_json['dataset_query']['native']['template-tags']['Date']['dimension'][1] = copy_field_filter_id

        # Update chart in Metabase
        mb.put(f'/api/card/{card_id}', json=chart_json)

    print('Done')


# Check if chart uses a field filter
def check_field_filter_present(chart_json):
    try:
        x = chart_json['dataset_query']['native']['template-tags']['Date']['dimension']
        return True
    except KeyError:
        return False


# Find dashboard id from dashboard name
def find_dashboard_id(mb, dashboard_name):
    # mb.search performs a fuzzy search and returns a list of all matches, after we select the exact dashboard
    fuzzy_dashboard_search = mb.search(q=dashboard_name, item_type='dashboard')
    dashboard_details = fuzzy_dashboard_search[find(fuzzy_dashboard_search, 'name', dashboard_name)]
    dashboard_id = dashboard_details['id']

    return dashboard_id


# Returns list of cards in dashboard
def dashboard_card_ids(mb, dashboard_name):
    dashboard_id = find_dashboard_id(mb, dashboard_name)
    dashboard_get = mb.get(f'/api/dashboard/{dashboard_id}')
    card_ids = [i['card_id'] for i in dashboard_get['ordered_cards'] if i['card_id'] is not None]

    return card_ids
