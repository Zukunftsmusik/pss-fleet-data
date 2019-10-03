

from datetime import timedelta, timezone
import openpyxl
import os

IS_DEBUG = True


# ---------- Defaults ----------

directory = f'{os.getcwd()}/'

OBTAIN_AT_HOURS = []
OBTAIN_AT_MINUTES = []
OBTAIN_AT_SECOND = 00

store_at_filesystem = True
store_at_gdrive = False


# ---------- From env vars ----------

GDRIVE_FOLDER_ID = str(os.environ.get('GDRIVE_FOLDER_ID'))
GPAT = str(os.environ.get('GPAT')) # General Purpose Access Token


# ---------- Constants ----------

ALLIANCE_ID_KEY_NAME = 'AllianceId'
ALLIANCE_INFO_PATH = 'AllianceService/ListAlliancesByRanking?skip=0&take=100'
ALLIANCE_TOURNEY_INFO_PATH = 'AllianceService/ListAlliancesWithDivision'
ALLIANCE_USERS_BASE_PATH = f'AllianceService/ListUsers?skip=0&take=100&accessToken={GPAT}&allianceId='

API_BASE_URL = 'https://api2.pixelstarships.com/'

CLI_FALSE_VALUES = ['n', 'no', '0', 'f', 'false']
CLI_TRUE_VALUES = ['y', 'yes', '1', 't', 'true']

COLUMN_FORMAT_DATETIME = 'YYYY-MM-DD hh:MM:ss'
COLUMN_FORMAT_NUMBER = '0'

COLUMN_NAME_FLEET_ID = 'Fleet Id'
COLUMN_NAME_FLEET_NAME = 'Fleet Name'
COLUMN_NAME_STARS = 'Stars'
COLUMN_NAME_TIMESTAMP = 'Timestamp'
COLUMN_NAME_TROPHIES = 'Trophies'
COLUMN_NAME_USER_ID = 'User Id'
COLUMN_NAME_USER_NAME = 'User Name'

CREATE_FOLDERS_ON_COLLECT = ['./tourney-data']

DEFAULT_COLLECT_FOLDER = './tourney-data'

DEFAULT_DATA_FILE_PREFIX = 'tourney-data_'
DEFAULT_DATA_FILE_SUFFIX = '.json'

DEFAULT_TABLE_STYLE = openpyxl.worksheet.table.TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)

DEFAULT_TIMEZONE = timezone.utc

FILE_NAME_COLLECT_PREFIX = 'pss-top-100_'
FILE_NAME_COLLECT_SUFFIX = '.json'
FILE_NAME_FLEET_NAMES = 'fleet-names.json'
FILE_NAME_PROCESS_PREFIX = 'pss-fleet-data_'
FILE_NAME_PROCESS_SUFFIX = '.xlsx'
FILE_NAME_USER_NAMES = 'user-names.json'

OBTAIN_USERS_THREAD_COUNT = 10

OUTPUT_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

SHORT_USER_INFO_FIELDS = [
    'Id',
    'AllianceId',
    'Trophy',
    'AllianceScore',
    'AllianceMembership',
    'AllianceJoinDate',
    'LastLoginDate'
]

SOURCE_FILE_NAME_DATETIME_FORMAT = '%Y%m%d-%H%M%S'

TIMEDELTA_ONE_DAY = timedelta(days=1)
TIMEDELTA_ONE_WEEK = timedelta(days=7)


# ---------- Variables without defaults ----------

files_to_process = []

process_output_file_name = ''
print_verbose = False

obtain_at_timestamps = []



if OBTAIN_AT_HOURS:
    for hour in OBTAIN_AT_HOURS:
        for minute in OBTAIN_AT_MINUTES:
            obtain_at_timestamps.append((hour, minute, OBTAIN_AT_SECOND))
elif OBTAIN_AT_MINUTES:
    for hour in range(24):
        for minute in OBTAIN_AT_MINUTES:
            obtain_at_timestamps.append((hour, minute, OBTAIN_AT_SECOND))
else:
    for hour in range(24):
        for minute in range(60):
            obtain_at_timestamps.append((hour, minute, OBTAIN_AT_SECOND))
