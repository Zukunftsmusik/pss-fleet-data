from datetime import datetime
from itertools import repeat
import json
from multiprocessing.dummy import Pool as ThreadPool
import sys

import gdrive
import pss_login as login
import settings
import utility as util


__runs = 0
__access_token: str = None


def collect_data(start_timestamp: datetime) -> dict:
    """
    Collects data and converts it.

    Returns 3 lists:
     - fleet names: (fleet_id, fleet_name)
     - user_names: (user_id, user_name)
     - data: (user_id, fleet_id, trophies, stars, rank, join_date, login_date)
    """
    _, login_data = login.login('8a7e7f42ba7d')
    global __access_token
    __access_token = login_data['accessToken']

    is_tourney_running = util.is_tourney_running(utc_now=start_timestamp)
    api_server = util.get_api_server()
    try:
        fleet_infos = get_fleet_infos(is_tourney_running, api_server)
    except Exception as error:
        util.err(f'Could not retrieve fleet infos', error)
        sys.exit()
    else:
        retrieved_fleet_infos_after = util.get_elapsed_seconds(start_timestamp)
        util.vrbs(f'Retrieved {len(fleet_infos)} fleet infos after {retrieved_fleet_infos_after:0.2f} seconds.')

    try:
        user_infos_raw = get_fleets_user_infos_raw(fleet_infos, api_server)
    except Exception as error:
        util.err(f'Could not retrieve user infos. Exiting.', error)
        sys.exit()
    else:
        retrieved_user_data_raw_after = util.get_elapsed_seconds(start_timestamp)
        user_infos = convert_user_data_raw(user_infos_raw)
        util.vrbs(f'Retrieved {len(user_infos)} user infos after {retrieved_user_data_raw_after:0.2f} seconds.')
    util.prnt(f'Processing raw data...')

    fleets = [get_short_fleet_info(fleet_info) for fleet_info in fleet_infos.values()]
    users = [get_short_user_info(user_info) for user_info in user_infos.values()]

    meta_data = {
        'timestamp': util.format_output_timestamp(start_timestamp),
        'duration': retrieved_fleet_infos_after + retrieved_user_data_raw_after,
        'fleet_count': len(fleet_infos),
        'user_count': len(user_infos),
        'tourney_running': is_tourney_running,
        'schema_version': 5
    }

    result = {
        'meta': meta_data,
        'fleets': fleets,
        'users': users
    }

    return result


def convert_user_data_raw(fleets_users_data_raw: list) -> dict:
    result = {}
    for user_data_raw in fleets_users_data_raw:
        user_infos = util.xmltree_to_dict3(user_data_raw, 'Id')
        result.update(user_infos)
    return result


def get_fleet_infos(is_tourney_running: bool, api_server: str) -> dict:
    if is_tourney_running:
        result = get_tournament_fleets(api_server)
    else:
        result = get_fleets(api_server)
    return result


def get_fleets(api_server: str) -> dict:
    return util.get_dict3_from_path(settings.ALLIANCE_INFO_PATH, settings.ALLIANCE_ID_KEY_NAME, api_server)


def get_fleet_users_path(alliance_id: str) -> str:
    result = f'AllianceService/ListUsers?skip=0&take=100&accessToken={__access_token}&allianceId={alliance_id}'
    return result


def get_fleet_users_raw(alliance_id: str, api_server: str) -> str:
    path = get_fleet_users_path(alliance_id)
    return util.get_data_from_path(path, api_server)


def get_short_fleet_info(fleet_info: dict) -> list:
    result = [int(fleet_info['AllianceId']), fleet_info['AllianceName'], int(fleet_info['Score']), int(fleet_info['DivisionDesignId']), int(fleet_info['Trophy'])]
    return result


def get_short_user_info(user_info: dict) -> list:
    result = []
    for source_prop, transform_function in settings.SHORT_USER_INFO_FIELDS.items():
        result.append(transform_function(user_info[source_prop]))
    return result


def get_tournament_fleets(api_server: str) -> dict:
    return util.get_dict3_from_path(settings.ALLIANCE_TOURNEY_INFO_PATH, settings.ALLIANCE_ID_KEY_NAME, api_server)


def get_fleets_user_infos_raw(fleet_infos: dict, api_server: str) -> list:
    args = zip(list(fleet_infos.keys()), repeat(api_server))
    pool = ThreadPool(settings.OBTAIN_USERS_THREAD_COUNT)
    result = pool.starmap(get_fleet_users_raw, args)
    pool.close()
    pool.join()
    result = list(result)
    return result


def retrieve_and_store_user_infos() -> None:
    global __runs
    __runs += 1
    util.prnt(f'Starting data collection run {__runs}')
    utc_now = util.get_utc_now()
    data = collect_data(utc_now)

    data_file_name = util.get_collect_file_name(utc_now)

    if settings.SETTINGS['store_at_filesystem']:
        util.dump_data(data, data_file_name, settings.DEFAULT_COLLECT_FOLDER)

    if settings.SETTINGS['store_at_gdrive']:
        tries_left = 5
        while tries_left > 0:
            tries_left -= 1
            try:
                gdrive.upload_file(data, data_file_name)
                tries_left = 0
            except Exception as error:
                if tries_left > 0:
                    gdrive.init(force=True)
                else:
                    raise error
