import hashlib
import random
from typing import Dict, Union
import requests
from xml.etree import ElementTree

import utility as util





def create_device_checksum(device_key: str, device_type: str, client_datetime: str) -> str:
    checksum_key = '5343'
    result = hashlib.md5((f'{device_key}{client_datetime}{device_type}{checksum_key}savysoda').encode('utf-8')).hexdigest()
    return result


def create_device_key() -> str:
    h = '0123456789abcdef'
    result = ''.join(
        random.choice(h)
        + random.choice('26ae')
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
        + random.choice(h)
    )
    return result


def login(device_key: str = None, api_server: str = None, device_type: str = None, login_data: Dict[str, Union[dict, str]] = None) -> Dict[str, Union[dict, str]]:
    if not device_key:
        if login_data:
            device_key = login_data['deviceKey']
        else:
            device_key: str = create_device_key()
    if not device_type:
        if login_data:
            device_type = login_data['deviceType']
        else:
            device_type = 'DeviceTypeMac'
    if not api_server:
        api_server = util.get_api_server()
    utc_now = util.get_utc_now()
    client_datetime = util.format_pss_timestamp(utc_now)

    params = {
        'advertisingKey': '""',
        'checksum': create_device_checksum(device_key, device_type, client_datetime),
        'clientDateTime': client_datetime,
        'deviceKey': device_key,
        'deviceType': device_type,
        'isJailBroken': 'false',
        'languageKey': 'en'
    }
    url = f'{api_server}/UserService/DeviceLogin11'
    data = requests.post(url, params=params).content.decode('utf-8')

    xml = ElementTree.fromstring(data)

    users = util.xmltree_to_dict2(data, 'Id')
    user_id = xml.find('UserLogin').attrib['UserId']
    access_token = xml.find('UserLogin').attrib['accessToken']
    result = {
        'User': users[user_id],
        'UserId': user_id,
        'accessToken': access_token,
        'deviceKey': device_key,
        'deviceType': device_type,
    }

    return result