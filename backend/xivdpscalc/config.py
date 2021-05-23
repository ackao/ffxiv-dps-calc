import json
from google.cloud import secretmanager

_project_id = '547306328282'
_version = 1

secret_manager_client = secretmanager.SecretManagerServiceClient()

_secret_path = secret_manager_client.secret_version_path(_project_id, 'db_info', _version)
_response = secret_manager_client.access_secret_version(_secret_path)
_db_info = json.dumps(_response.payload.data.decode('UTF-8'))

SQLALCHEMY_DATABASE_URI = f"postgresql://{_db_info['db_user']}:{_db_info['db_password']}@/{_db_info['db_name']}?unix_sock={_db_info['db_socket_dir']}/{_db_info['cloud_sql_connection_name']}"
