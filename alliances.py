

import json
from multiprocessing.dummy import Pool as ThreadPool
import pydrive

import gdrive
import settings
import utility as util


__runs = 0




def get_tournament_alliances() -> dict:
    path = f'AllianceService/ListAlliancesWithDivision'
    return util.get_dict3_from_path(path, 'AllianceId')


def get_alliance_users_path(alliance_id: str) -> str:
    return f'{settings.ALLIANCE_USERS_BASE_PATH}{alliance_id}'


def get_alliance_users_raw(alliance_id: str) -> str:
    path = get_alliance_users_path(alliance_id)
    return (alliance_id, util.get_data_from_path(path))


def get_short_user_info(user_info: dict) -> dict:
    result = {}
    for source, target in settings.SHORT_USER_INFO_FIELDS.items():
        result[target] = user_info[source]
    return result


def get_user_infos() -> dict:
    start = util.get_time()
    alliance_infos = get_tournament_alliances()

    pool = ThreadPool(settings.THREAD_COUNT)
    alliance_user_infos_raw = pool.map(get_alliance_users_raw, alliance_infos.keys())
    pool.close()
    pool.join()

    for alliance_id, user_infos_raw in alliance_user_infos_raw:
        user_infos = util.xmltree_to_dict3(user_infos_raw, 'Id')
        alliance_infos[alliance_id]['Users'] = user_infos

    user_infos_count = sum([len(alliance_info['Users']) for alliance_info in alliance_infos.values()])
    util.dbg(f'Retrieved {user_infos_count} user info entries in {util.get_elapsed_seconds(start):0.2f} seconds.')

    result = {}
    for alliance_info in alliance_infos.values():
        for user_id, user_info in alliance_info['Users'].items():
            suffix = 1
            new_key = user_id
            while new_key in result.keys():
                suffix += 1
                new_key = f'{user_id}_{suffix}'
            result[new_key] = get_short_user_info(user_info)

    return result


def retrieve_and_store_user_infos(upload_to_gdrive: bool = False) -> None:
    global __runs
    __runs += 1
    util.dbg(f'Starting data collection run {__runs}')
    user_infos = []
    utc_now = util.get_utc_now()
    try:
        user_infos = get_user_infos()
    except Exception as error:
        util.err(f'Could not retrieve user infos', error)
    if user_infos:
        file_content = json.dumps(user_infos)
        file_name = f'tourney-data_{util.format_datetime(utc_now)}.json'
        if settings.STORE_AT_FILESYSTEM:
            util.save_to_filesystem(file_content, file_name)
        if settings.STORE_AT_GDRIVE:
            util.save_to_gdrive(file_content, file_name)
