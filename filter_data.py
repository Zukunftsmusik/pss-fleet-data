

import settings


def by_fleet_names(alliance_names: list, data: list) -> dict:
    return _by_field(settings.COLUMN_NAME_FLEET_NAME, alliance_names, data)


def by_fleet_ids(alliance_ids: list, data: list) -> list:
    return _by_field(settings.COLUMN_NAME_FLEET_ID, alliance_ids, data)


def by_user_names(user_names: list, data: list) -> list:
    return _by_field(settings.COLUMN_NAME_USER_NAME, user_names, data)


def by_user_ids(user_ids: list, data: list) -> list:
    return _by_field(settings.COLUMN_NAME_USER_ID, user_ids, data)


def _by_field(field_name: str, field_values: list, data: list) -> list:
    result = []
    headers = data[0]
    header_found = False
    for i, header_name in enumerate(headers):
        if field_name == header_name:
            header_found = True
            break
    if header_found:
        result = [headers]
        result.extend([item for item in data if item[i] in field_values])
    return result