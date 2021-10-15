from datetime import datetime
from itertools import repeat
from multiprocessing.dummy import Pool as ThreadPool
from os import access
from urllib.error import HTTPError
from typing import Dict, List, Union
from xml.etree.ElementTree import ParseError as XmlParseError

import gdrive
import settings
import utility as util


__runs: int = 0


def collect_data(start_timestamp: datetime) -> dict:
    api_server = util.get_production_server()
    access_token = settings.ACCESS_TOKEN

    is_tourney_running = util.is_tourney_running(utc_now=start_timestamp)
    try:
        fleet_infos = get_fleet_infos(is_tourney_running, api_server)
    except Exception as error:
        util.err(f'Could not retrieve fleet infos', error)
        return None
    else:
        retrieved_fleet_infos_after = util.get_elapsed_seconds(start_timestamp)
        util.vrbs(f'Retrieved {len(fleet_infos)} fleet infos after {retrieved_fleet_infos_after:0.2f} seconds.')

    fleets_users_count = sum(int(fleet_info.get('NumberOfMembers', 0)) for fleet_info in fleet_infos.values())

    if settings.RETRIEVE_TOP_USERS:
        try:
            top_100_users_infos_raw = get_top_100_users_infos_raw(api_server, access_token)
        except Exception as error:
            util.err(f'Could not retrieve user infos. Exiting.', error)
            return None

        retrieved_top_100_user_infos_raw_after = util.get_elapsed_seconds(start_timestamp)

    if settings.RETRIEVE_FLEET_USERS:
        try:
            user_infos_raw = get_fleets_user_infos_raw(fleet_infos, api_server, access_token)
            retrieved_user_infos_raw_after = util.get_elapsed_seconds(start_timestamp)
        except Exception as error:
            util.err(f'Could not retrieve user infos.', error)

    if settings.RETRIEVE_TOP_USERS:
        top_100_users_infos = convert_user_data_raw([top_100_users_infos_raw])
        util.vrbs(f'Retrieved {len(top_100_users_infos)} top 100 user infos after {retrieved_top_100_user_infos_raw_after:0.2f} seconds.')
    else:
        top_100_users_infos = {}

    if settings.RETRIEVE_FLEET_USERS:
        fleets_users_infos = convert_user_data_raw(user_infos_raw)
        util.vrbs(f'Retrieved {len(fleets_users_infos)} of {fleets_users_count} fleets user infos after {retrieved_user_infos_raw_after:0.2f} seconds.')
    else:
        fleets_users_infos = {}

    util.prnt(f'Processing raw data...')
    user_infos = fleets_users_infos

    if settings.RETRIEVE_TOP_USERS:
        if settings.RETRIEVE_TOP_USERS_DETAILS:
            for user_id in top_100_users_infos.keys():
                if user_id not in user_infos.keys():
                    user_info = get_user_info_from_id(user_id, api_server, access_token)
                    user_infos[user_id] = user_info
        else:
            for user_id, top_100_user_info in top_100_users_infos.items():
                if user_id not in user_infos:
                    user_infos[user_id] = top_100_user_info

    fleets = [get_short_fleet_info(fleet_info) for fleet_info in fleet_infos.values()]
    users = [get_short_user_info(user_info) for user_info in user_infos.values()]
    duration = util.get_elapsed_seconds(start_timestamp)

    meta_data = {
        'timestamp': util.format_output_timestamp(start_timestamp),
        'duration': duration,
        'fleet_count': len(fleets),
        'user_count': len(users),
        'tourney_running': is_tourney_running,
        'schema_version': 7
    }

    result = {
        'meta': meta_data,
        'fleets': fleets,
        'users': users
    }

    return result


def convert_user_data_raw(fleets_users_data_raw: list) -> Dict[str, dict]:
    result = {}
    for user_data_raw in fleets_users_data_raw:
        user_infos = util.xmltree_to_dict3(user_data_raw, 'Id')
        result.update(user_infos)
    return result


def get_fleet_infos(is_tourney_running: bool, api_server: str) -> Dict[str, dict]:
    if is_tourney_running:
        result = get_tournament_fleets(api_server)
    else:
        result = get_fleets(api_server)
    return result


def get_fleets(api_server: str) -> Dict[str, dict]:
    return util.get_dict3_from_path(settings.ALLIANCE_INFO_PATH, settings.ALLIANCE_ID_KEY_NAME, api_server)


def get_fleet_users_path(alliance_id: str, access_token: str) -> str:
    result = f'AllianceService/ListUsers2?skip=0&take=100&accessToken={access_token}&allianceId={alliance_id}'
    return result


def get_fleet_users_raw(alliance_id: str, api_server: str, access_token: str) -> str:
    path = get_fleet_users_path(alliance_id, access_token)
    try:
        result = util.get_data_from_path(path, api_server)
    except HTTPError:
        result = ''
    return result


def get_short_fleet_info(fleet_info: dict) -> List[Union[int, str]]:
    result = [transform_function(fleet_info[source_prop]) for source_prop, transform_function in settings.SHORT_ALLIANCE_INFO_FIELDS.items()]
    return result


def get_short_user_info(user_info: dict) -> List[Union[int, str]]:
    result = [transform_function(user_info[source_prop]) for source_prop, transform_function in settings.SHORT_USER_INFO_FIELDS.items()]
    return result


def get_tournament_fleets(api_server: str) -> Dict[str, dict]:
    return util.get_dict3_from_path(settings.ALLIANCE_TOURNEY_INFO_PATH, settings.ALLIANCE_ID_KEY_NAME, api_server)


def get_fleets_user_infos_raw(fleet_infos: dict, api_server: str, access_token: str) -> List[str]:
    args = zip(list(fleet_infos.keys()), repeat(api_server), repeat(access_token))
    pool = ThreadPool(settings.OBTAIN_USERS_THREAD_COUNT)
    result = pool.starmap(get_fleet_users_raw, args)
    pool.close()
    pool.join()
    result = list(result)
    return result


def get_top_100_users_infos_raw(api_server: str, access_token: str) -> str:
    path = f'LadderService/ListUsersByRanking?from=0&to=100&accessToken={access_token}'
    try:
        result = util.get_data_from_path(path, api_server)
    except HTTPError:
        result = ''
    return result


def retrieve_and_store_user_infos() -> None:
    global __runs
    __runs += 1
    util.prnt(f'----------')
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


def get_user_info_from_id(user_id: str, api_server: str, access_token: str) -> dict:
    path = f'ShipService/InspectShip2?accessToken={access_token}&userId={user_id}'
    try:
        result = util.get_dict2_from_path(path, settings.USER_ID_KEY_NAME, api_server)
    except (HTTPError, XmlParseError) as err:
        result = {}
    return result