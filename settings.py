

from datetime import timedelta, timezone
import os


GDRIVE_FOLDER_ID = '10wOZgAQk_0St2Y_jC3UW497LVpBNxWmP'
GPAT = str(os.environ.get('GPAT')) # General Purpose Access Token

IS_DEBUG = True
FOLDERS_TO_BE_CREATED = ['./tourney-data']
OBTAIN_AT_HOURS = []
OBTAIN_AT_MINUTES = [39]
OBTAIN_AT_SECOND = 00
OBTAIN_AT_TIMESTAMPS = []
OUTPUT_FILE_NAME_PREFIX = 'pss-top-100_'
OUTPUT_FILE_NAME_SUFFIX = '.json'
STORE_AT_FILESYSTEM = True
STORE_AT_GDRIVE = False
THREAD_COUNT = 10

ALLIANCE_USERS_BASE_PATH = f'AllianceService/ListUsers?skip=0&take=100&accessToken={GPAT}&allianceId='
BASE_URL = 'https://api2.pixelstarships.com/'
SHORT_USER_INFO_FIELDS = {
    'AllianceId': 'AllianceId',
    'Name': 'UserName',
    'AllianceName': 'AllianceName',
    'Trophy': 'Trophies',
    'AllianceScore': 'Stars',
    'AllianceMembership': 'Rank',
    'AllianceJoinDate': 'Joined',
    'LastLoginDate': 'LastLogin'
}
TD_ONE_DAY = timedelta(days=1)
TD_ONE_WEEK = timedelta(days=7)
TZ_UTC = timezone.utc

TRUE_VALUES = ['y', 'yes', '1', 't', 'true']
FALSE_VALUES = ['n', 'no', '0', 'f', 'false']



if OBTAIN_AT_HOURS:
    for hour in OBTAIN_AT_HOURS:
        for minute in OBTAIN_AT_MINUTES:
            OBTAIN_AT_TIMESTAMPS.append((hour, minute, OBTAIN_AT_SECOND))
elif OBTAIN_AT_MINUTES:
    for hour in range(24):
        for minute in OBTAIN_AT_MINUTES:
            OBTAIN_AT_TIMESTAMPS.append((hour, minute, OBTAIN_AT_SECOND))
else:
    for hour in range(24):
        for minute in range(60):
            OBTAIN_AT_TIMESTAMPS.append((hour, minute, OBTAIN_AT_SECOND))