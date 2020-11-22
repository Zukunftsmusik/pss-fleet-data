import hashlib
import random
import requests
from xml.etree import ElementTree

import utility as util





def create_device_checksum(device_key: str, device_type: str) -> str:
    result = hashlib.md5((f'{device_key}{device_type}savysoda').encode('utf-8')).hexdigest()
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


def login(device_key: str = None, api_server: str = None, device_type: str = 'DeviceTypeMac') -> dict:
    if not device_key:
        device_key: str = create_device_key()
    if not api_server:
        api_server = util.get_api_server()

    params = {
        'advertisingKey': '""',
        'checksum': create_device_checksum(device_key, device_type),
        'deviceKey': device_key,
        'deviceType': device_type,
        'isJailBroken': 'false',
        'languageKey': 'en'
    }
    url = f'{api_server}/UserService/DeviceLogin8'
    data = requests.post(url, params=params).content.decode('utf-8')

    xml = ElementTree.fromstring(data)

    users = util.xmltree_to_dict2(data, 'Id')
    user_id = xml.find('UserLogin').attrib['UserId']
    access_token = xml.find('UserLogin').attrib['accessToken']
    result = {
        'User': users[user_id],
        'UserId': user_id,
        'accessToken': access_token
    }

    return device_key, result