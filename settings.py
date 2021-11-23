from datetime import datetime, timedelta, timezone
import os

import utility as util

IS_DEBUG = True


# ---------- Settings dict ----------

SETTINGS = {
    'print_timestamps': False,
    'store_at_filesystem': False,
    'store_at_gdrive': False,
    'print_verbose': False
}


# ---------- Defaults ----------

directory = f'{os.getcwd()}/'

OBTAIN_AT_HOURS = [3, 7, 11, 15, 19, 23]
OBTAIN_AT_MINUTES = [59]
OBTAIN_AT_SECOND = 00

store_at_filesystem = False
store_at_gdrive = False


# ---------- From env vars ----------

ACCESS_TOKEN: str = os.environ.get('PSS_ACCESS_TOKEN')

GDRIVE_FOLDER_ID = '10wOZgAQk_0St2Y_jC3UW497LVpBNxWmP'


# ---------- Constants ----------

ALLIANCE_ID_KEY_NAME = 'AllianceId'
ALLIANCE_INFO_PATH = 'AllianceService/ListAlliancesByRanking?skip=0&take=100'
ALLIANCE_TOURNEY_INFO_PATH = 'AllianceService/ListAlliancesWithDivision'

API_BASE_URL = 'https://api.pixelstarships.com/'


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


DATA_MAPPING_FLEETS = 'fleets'
DATA_MAPPING_USERS = 'users'

DEFAULT_COLLECT_FOLDER = './tourney-data'

DEFAULT_DATA_FILE_PREFIX = 'tourney-data_'
DEFAULT_DATA_FILE_SUFFIX = '.json'

DEFAULT_TIMEZONE = timezone.utc


FILE_NAME_COLLECT_PREFIX = 'pss-top-100_'
FILE_NAME_COLLECT_SUFFIX = '.json'


OBTAIN_USERS_THREAD_COUNT = 10


PRODUCTION_SERVER: str = os.environ.get('PSS_PRODUCTION_SERVER')
PSS_START_DATE = datetime(year=2016, month=1, day=6)


RANKS_LOOKUP = {
    'None': -1,
    'FleetAdmiral': 0,
    'ViceAdmiral': 1,
    'Commander': 2,
    'Major': 3,
    'Lieutenant': 4,
    'Ensign': 5,
    'Candidate': 6
}
RETRIEVE_FLEET_USERS: bool = bool(int(os.environ.get('RETRIEVE_FLEET_USERS', 1)))
RETRIEVE_TOP_USERS: bool = bool(int(os.environ.get('RETRIEVE_TOP_USERS', 0)))
RETRIEVE_TOP_USERS_DETAILS: bool = bool(int(os.environ.get('RETRIEVE_TOP_USERS_DETAILS', 0)))


SETTINGS_BASE_PATH = 'SettingService/GetLatestVersion3?deviceType=DeviceTypeAndroid&languageKey='
SHORT_ALLIANCE_INFO_FIELDS = {
    'AllianceId': int,
    'AllianceName': str,
    'Score': int,
    'DivisionDesignId': int,
    'Trophy': int,
    'ChampionshipScore': int,
    'NumberOfMembers': int,
    'NumberOfApprovedMembers': int,
}
SHORT_USER_INFO_FIELDS = {
    'Id': int,
    'Name': str,
    'AllianceId': int,
    'Trophy': int,
    'AllianceScore': int,
    'AllianceMembership': util.get_rank_number,
    'AllianceJoinDate': util.pss_timestamp_to_ordinal,
    'LastLoginDate': util.pss_timestamp_to_ordinal,
    'LastHeartBeatDate': util.pss_timestamp_to_ordinal,
    'CrewDonated': int,
    'CrewReceived': int,
	'PVPAttackWins': int,
	'PVPAttackLosses': int,
	'PVPAttackDraws': int,
	'PVPDefenceWins': int,
	'PVPDefenceLosses': int,
	'PVPDefenceDraws': int,
    'ChampionshipScore': int,
}


TIMEDELTA_ONE_DAY = timedelta(days=1)
TIMEDELTA_ONE_WEEK = timedelta(days=7)

TIMESTAMP_FORMAT_OUTPUT = '%Y-%m-%d %H:%M:%S'
TIMESTAMP_FORMAT_PSS = '%Y-%m-%dT%H:%M:%S'
TIMESTAMP_FORMAT_SOURCE_FILE_NAME = '%Y%m%d-%H%M%S'


USER_ID_KEY_NAME = 'Id'


# ---------- Late binding constants ----------

# schema dict:
# <data_type> : {
#     <column_name>: (<excel cell format>, <custom transformation function>)
#   }
DATA_OUTPUT_SCHEMA = {
    DATA_MAPPING_FLEETS: {
        'Timestamp': (COLUMN_FORMAT_DATETIME, None),
        'Fleet name': (None, None),
        'Trophies': (COLUMN_FORMAT_NUMBER, None),
        'Stars': (COLUMN_FORMAT_NUMBER, None)
    },
    DATA_MAPPING_USERS: {
        'Timestamp': (COLUMN_FORMAT_DATETIME, None),
        'Fleet name': (None, None),
        'Player name': (None, None),
        'Rank': (None, None),
        'Last login': (COLUMN_FORMAT_DATETIME, None),
        'Trophies': (COLUMN_FORMAT_NUMBER, None),
        'Stars': (COLUMN_FORMAT_NUMBER, None),
        'Join date': (COLUMN_FORMAT_DATETIME, None)
    }
}


# ---------- Variables without defaults ----------

files_to_process = []

process_output_file_name = ''
print_timestamps = True
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
