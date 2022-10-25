# Metabase Dashboard Copy Tool
**You are required to be on VPN for this script to execute successfully.**

This script leverages the Metabase API in order to produce a copy of a dashboard, as well as copying each chart within the dashboard store in a sub-collection. Then each chart and it's field filter (limited by a single field filter called 'Date' currently) is pointed to a specified database. Allowing for easy management of multi-environment dashboards for Metabase. 

If there is already a dashboard/charts in the copy destination collection, this will automatically be archived if made previously by this tool.

## Useful Documention
[Metabase API tutorial](https://www.metabase.com/learn/administration/metabase-api) - Quick walkthrough on API use

[Metabase API documentation](https://www.metabase.com/docs/latest/api-documentation) - API docs

[Python Metabase API Wrapper](https://github.com/vvaezian/metabase_api_python) - Wrapper used for 'deep' copying dashboards. Also has other useful functions and good starting place for finding the most helpful endpoints.

## Setup

Modify the 5 input variables found in the config.json:
```json
{
  "original_dashboard_id": 27,
  "copy_collection_id": 70,
  "copy_dashboard_name": "Prod - Decision Engine Performance",
  "copy_database_id": 7,
  "secrets_path": "../../secrets/Config.json"
}
```
- `original_dashboard_id` the id of the dashboard that you wish to be copied
- `copy_collection_id` the id of the collection where you wish for the copy to stored
- `copy_dashboard_name` the name for the copied dashboard
- `copy_database_id` the id of the database for the copied charts to be pointed to
- `secrets_path` the location of your secrets file, expected structure found below

You can find the ids for the dashboards/collections from their URL when viewing in Metabase.

### Secrets

Your secrets files should look like this:

```json
{
  "Metabase": {
    "url": "https://prod-metabase.koodoo.io",
    "username": "your-username",
    "password": "your-password"
  }
}
```