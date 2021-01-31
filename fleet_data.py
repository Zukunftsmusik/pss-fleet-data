from datetime import datetime
from itertools import repeat
from multiprocessing.dummy import Pool as ThreadPool
from typing import Dict, List, Union

import gdrive
import pss_login as login
import settings
import utility as util


__runs: int = 0
__login_data: Dict[str, Union[dict, str]] = None


def refresh_access_token(api_server: str) -> None:
    global __login_data
    login_data = login.login(api_server=api_server, login_data=__login_data)
    __login_data = dict(login_data)
    util.dbg(f'Created access token for device: {login_data["deviceKey"]}')
    util.dbg(f'Current access token: {login_data["accessToken"]}')


def collect_data(start_timestamp: datetime) -> dict:
    """
    Collects data and converts it.

    Returns 3 lists:
     - fleet names: (fleet_id, fleet_name)
     - user_names: (user_id, user_name)
     - data: (user_id, fleet_id, trophies, stars, rank, join_date, login_date)
    """
    api_server = util.get_api_server()
    refresh_access_token(api_server)

    is_tourney_running = util.is_tourney_running(utc_now=start_timestamp)
    try:
        fleet_infos = get_fleet_infos(is_tourney_running, api_server)
    except Exception as error:
        util.err(f'Could not retrieve fleet infos', error)
        return None
    else:
        retrieved_fleet_infos_after = util.get_elapsed_seconds(start_timestamp)
        util.vrbs(f'Retrieved {len(fleet_infos)} fleet infos after {retrieved_fleet_infos_after:0.2f} seconds.')

    while True:
        try:
            top_100_users_infos_raw = get_top_100_users_infos_raw(api_server)
        except Exception as error:
            util.err(f'Could not retrieve user infos. Exiting.', error)
            return None
        if 'Access token expired.' in top_100_users_infos_raw:
            refresh_access_token(api_server)
        else:
            break

    retrieved_top_100_user_infos_raw_after = util.get_elapsed_seconds(start_timestamp)

    while True:
        try:
            user_infos_raw = get_fleets_user_infos_raw(fleet_infos, api_server)
            break
        except util.AccessTokenExpiredError:
            refresh_access_token(api_server)
        except Exception as error:
            util.err(f'Could not retrieve user infos. Exiting.', error)
            return None

    top_100_infos = convert_user_data_raw([top_100_users_infos_raw])
    fleets_users_infos = convert_user_data_raw(user_infos_raw)
    util.vrbs(f'Retrieved {len(top_100_infos)} top 100 user infos after {retrieved_top_100_user_infos_raw_after:0.2f} seconds.')
    retrieved_user_infos_raw_after = util.get_elapsed_seconds(start_timestamp)
    util.vrbs(f'Retrieved {len(fleets_users_infos)} fleets user infos after {retrieved_user_infos_raw_after:0.2f} seconds.')

    util.prnt(f'Processing raw data...')
    user_infos = fleets_users_infos
    for user_id, user_info in top_100_infos.items():
        if user_id not in user_infos:
            user_info = get_user_info_from_id(user_id, api_server)
            user_infos[user_id] = user_info[user_id]

    fleets = [get_short_fleet_info(fleet_info) for fleet_info in fleet_infos.values()]
    users = [get_short_user_info(user_info) for user_info in user_infos.values()]
    duration = util.get_elapsed_seconds(start_timestamp)

    meta_data = {
        'timestamp': util.format_output_timestamp(start_timestamp),
        'duration': duration,
        'fleet_count': len(fleets),
        'user_count': len(users),
        'tourney_running': is_tourney_running,
        'schema_version': 6
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


def get_fleet_users_path(alliance_id: str) -> str:
    result = f'AllianceService/ListUsers?skip=0&take=100&accessToken={__login_data["accessToken"]}&allianceId={alliance_id}'
    return result


def get_fleet_users_raw(alliance_id: str, api_server: str) -> str:
    path = get_fleet_users_path(alliance_id)
    return util.get_data_from_path(path, api_server)


def get_short_fleet_info(fleet_info: dict) -> List[Union[int, str]]:
    result = [transform_function(fleet_info[source_prop]) for source_prop, transform_function in settings.SHORT_ALLIANCE_INFO_FIELDS.items()]
    return result


def get_short_user_info(user_info: dict) -> List[Union[int, str]]:
    result = [transform_function(user_info[source_prop]) for source_prop, transform_function in settings.SHORT_USER_INFO_FIELDS.items()]
    return result


def get_tournament_fleets(api_server: str) -> Dict[str, dict]:
    return util.get_dict3_from_path(settings.ALLIANCE_TOURNEY_INFO_PATH, settings.ALLIANCE_ID_KEY_NAME, api_server)


def get_fleets_user_infos_raw(fleet_infos: dict, api_server: str) -> List[str]:
    args = zip(list(fleet_infos.keys()), repeat(api_server))
    pool = ThreadPool(settings.OBTAIN_USERS_THREAD_COUNT)
    result = pool.starmap(get_fleet_users_raw, args)
    pool.close()
    pool.join()
    result = list(result)
    return result


def get_top_100_users_infos_raw(api_server: str) -> str:
    path = f'LadderService/ListUsersByRanking?from=0&to=100&accessToken={__login_data["accessToken"]}'
    return util.get_data_from_path(path, api_server)


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


def get_user_info_from_id(user_id: str, api_server: str) -> dict:
    path = f'ShipService/InspectShip2?accessToken={__login_data["accessToken"]}&userId={user_id}'
    result = util.get_dict2_from_path(path, settings.USER_ID_KEY_NAME, api_server)
    return result