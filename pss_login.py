import hashlib
import random
import requests
from xml.etree import ElementTree

import settings
import utility as util





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

def create_device_checksum(device_key: str) -> str:
    result = hashlib.md5((f'{device_key}DeviceTypeMacsavysoda').encode('utf-8')).hexdigest()
    return result

def login(device_key: str = None, api_server: str = None) -> dict:
    if not device_key:
        device_key: str = create_device_key()
    if not api_server:
        api_server = util.get_api_server()

    checksum = create_device_checksum(device_key)

    path = f'UserService/DeviceLogin8?deviceKey={device_key}&isJailBroken=false&checksum={checksum}&deviceType=DeviceTypeMac&languageKey=en&advertisingkey=%22%22'

    url = f'{api_server}/{path}'
    data = requests.post(url).content.decode('utf-8')

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