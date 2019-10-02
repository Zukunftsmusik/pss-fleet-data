from datetime import datetime
import json
from multiprocessing.dummy import Pool as ThreadPool
import sys

import gdrive
import settings
import utility as util


__runs = 0


def collect_data(start_timestamp: datetime) -> (list, list, list):
    """
    Collects data and converts it.

    Returns 3 lists:
     - fleet names: (fleet_id, fleet_name)
     - user_names: (user_id, user_name)
     - data: (user_id, fleet_id, trophies, stars, rank, join_date, login_date)
    """
    is_tourney_running = util.is_tourney_running(utc_now=start_timestamp)
    try:
        fleet_infos = get_fleet_infos(is_tourney_running)
    except Exception as error:
        util.err(f'Could not retrieve fleet infos', error)
        sys.exit()
    else:
        util.dbg(f'Retrieved {len(fleet_infos)} fleet infos after {util.get_elapsed_seconds(start_timestamp)} seconds.')

    try:
        user_infos_raw = get_fleets_user_infos_raw(fleet_infos)
    except Exception as error:
        util.err(f'Could not retrieve user infos. Exiting.', error)
        sys.exit()
    else:
        util.dbg(f'Retrieved {len(user_infos_raw)} user infos after {util.get_elapsed_seconds(start_timestamp)} seconds.')
    util.dbg(f'Processing raw data...')

    user_infos = [util.xmltree_to_dict3(user_info_raw, 'Id') for user_info_raw in user_infos_raw]
    fleet_names = [(fleet_info['AllianceId'], fleet_info['AllianceName']) for fleet_info in fleet_infos]
    user_names = [(user_info['Id'], user_info['Name']) for user_info in user_infos]
    output_timestamp = util.format_output_timestamp(start_timestamp)
    data = [get_short_user_info(output_timestamp, user_info) for user_info in user_infos]

    return (fleet_names, user_names, data)


def get_fleet_infos(is_tourney_running: bool) -> dict:
    if is_tourney_running:
        result = get_tournament_fleets()
    else:
        result = get_fleets()
    return result


def get_fleets() -> dict:
    return util.get_dict3_from_path(settings.ALLIANCE_INFO_PATH, settings.ALLIANCE_ID_KEY_NAME)


def get_fleet_users_path(alliance_id: str) -> str:
    result = f'{settings.ALLIANCE_USERS_BASE_PATH}{alliance_id}'
    return result


def get_fleet_users_raw(alliance_id: str) -> str:
    path = get_fleet_users_path(alliance_id)
    return util.get_data_from_path(path)


def get_short_user_info(timestamp: str, user_info: dict) -> dict:
    result = []
    for source_prop in settings.SHORT_USER_INFO_FIELDS:
        result.append(user_info[source_prop])
    return result


def get_tournament_fleets() -> dict:
    return util.get_dict3_from_path(settings.ALLIANCE_TOURNEY_INFO_PATH, settings.ALLIANCE_ID_KEY_NAME)


def get_fleets_user_infos_raw(fleet_infos: dict) -> list:
    pool = ThreadPool(settings.OBTAIN_THREAD_COUNT)
    result = pool.map(get_fleet_users_raw, fleet_infos.keys())
    pool.close()
    pool.join()
    result = list(result)
    return result


def retrieve_and_store_user_infos() -> None:
    global __runs
    __runs += 1
    util.dbg(f'Starting data collection run {__runs}')
    utc_now = util.get_utc_now()
    fleet_names, user_names, data = collect_data(utc_now)

    # TODO: output stuff


def store_fleet_names(data: list, store_at_filesystem: bool, store_at_gdrive: bool) -> None:

    pass


def store_user_infos(data: list, store_at_filesystem: bool, store_at_gdrive: bool) -> None:
    pass


def store_user_names(data: list, store_at_filesystem: bool, store_at_gdrive: bool) -> None:
    pass
