import json
import os
import pydrive.auth
import pydrive.drive
import pydrive.files
import urllib.parse
import yaml

import settings
import utility as util


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'client_secrets.json'
SETTINGS_FILE = 'settings.yaml'

__drive = None
__initialized = False



def __assert_initialized():
    if __drive is None:
        raise Exception('The __drive object has not been initialized, yet!')


def create_service_account_credential_json():
    project_id = str(os.environ.get('GDRIVE_SERVICE_PROJECT_ID'))
    private_key_id = str(os.environ.get('GDRIVE_SERVICE_PRIVATE_KEY_ID'))
    private_key = str(os.environ.get('GDRIVE_SERVICE_PRIVATE_KEY'))
    client_email = str(os.environ.get('GDRIVE_SERVICE_CLIENT_EMAIL'))
    client_id = str(os.environ.get('GDRIVE_SERVICE_CLIENT_ID'))

    contents = {}
    contents['type'] = 'service_account'
    contents['project_id'] = project_id
    contents['private_key_id'] = private_key_id
    contents['private_key'] = private_key
    contents['client_email'] = client_email
    contents['client_id'] = client_id
    contents['auth_uri'] = 'https://accounts.google.com/o/oauth2/auth'
    contents['token_uri'] = 'https://oauth2.googleapis.com/token'
    contents['auth_provider_x509_cert_url'] = 'https://www.googleapis.com/oauth2/v1/certs'
    contents['client_x509_cert_url'] = f'https://www.googleapis.com/robot/v1/metadata/x509/{urllib.parse.quote(client_email)}'
    with open(SERVICE_ACCOUNT_FILE, 'w+') as service_file:
        json.dump(contents, service_file, indent=2)
    util.vrbs(f'Created service account connection file at: {SERVICE_ACCOUNT_FILE}')


def create_service_account_settings_yaml():
    contents = {}
    contents['client_config_backend'] = 'file'
    contents['client_config_file'] = SERVICE_ACCOUNT_FILE
    contents['save_credentials'] = True
    contents['save_credentials_backend'] = 'file'
    contents['save_credentials_file'] = 'credentials.json'
    contents['oauth_scope'] = list(SCOPES)

    with open(SETTINGS_FILE, 'w+') as settings_file:
        yaml.dump(contents, settings_file)
    util.vrbs(f'Created settings yaml file at: {SETTINGS_FILE}')


def get_first_file(folder_id: str, file_name: str) -> pydrive.files.GoogleDriveFile:
    # {'q': "'folder_id' in parents and trashed=false and name='file_name'"}
    __assert_initialized()
    file_list = __drive.ListFile({'q': f"'{folder_id}' in parents and title = '{file_name}'"}).GetList()
    for file_def in file_list:
        return file_def
    return None


def list_files_in_root():
    __assert_initialized()
    file_list = __drive.ListFile({'q': "'root' in parents"}).GetList()
    for file_def in file_list:
        print(f'title: {file_def["title"]}, id: {file_def["id"]}')


def update_file(data_new: list, file_name: str) -> None:
    existing_file = get_first_file(settings.GDRIVE_FOLDER_ID, file_name)
    if existing_file:
        content_old = existing_file.GetContentString()
        data_old = json.loads(content_old)
        data_new.extend(data_old)
        data_new = util.remove_duplicates(data_new)
        content_new = json.dumps(data_new)
        existing_file.SetContentString(content_new)
    else:
        upload_file(data_new, file_name)


def upload_file(data: list, file_name: str) -> None:
    __assert_initialized()
    content = json.dumps(data)
    file_info = {
        'title': file_name,
        'parents': [{
            'kind': 'drive#fileLink',
            'id': settings.GDRIVE_FOLDER_ID
        }]
    }
    util.vrbs(f'Creating file on gdrive: {file_name}')
    drive_file = __drive.CreateFile(file_info)
    drive_file.SetContentString(content)
    drive_file.Upload()
    util.vrbs(f'Uploaded file to gdrive: {file_name}')





def init(force: bool = False):
    global __drive, __initialized
    if (force or not __initialized) and settings.SETTINGS['store_at_gdrive']:
        create_service_account_credential_json()
        create_service_account_settings_yaml()
        gauth = pydrive.auth.GoogleAuth()
        credentials = pydrive.auth.ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
        gauth.credentials = credentials
        __drive = pydrive.drive.GoogleDrive(gauth)
        __initialized = True
