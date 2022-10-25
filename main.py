from metabase_functions import *

# Load variables from config
with open('config.json', 'r') as f:
    config = json.load(f)
original_dashboard_id = config['original_dashboard_id']
copy_collection_id = config['copy_collection_id']
copy_dashboard_name = config['copy_dashboard_name']
copy_database_id = config['copy_database_id']
secrets_path = config['secrets_path']

# Establish connection to Metabase
metabase_connection = get_metabase_connection(secrets_path)

# Archive previously copied dashboard, charts, and collection containing copied charts if they exist
archive_dashboard(metabase_connection, copy_collection_id)

# Copy original dashboard and charts
print('Starting dashboard copy')
metabase_connection.copy_dashboard(source_dashboard_id=original_dashboard_id,
                                   destination_collection_id=copy_collection_id,
                                   destination_dashboard_name=copy_dashboard_name, deepcopy=True)
print('Finished dashboard copy')

# Update database and field filters for each of the copied charts
repoint_copied_charts(metabase_connection, copy_dashboard_name, copy_database_id)
