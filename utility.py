

from datetime import datetime, timezone
import time
import urllib.request
import xml.etree.ElementTree

import gdrive
import settings


TZ_UTC = timezone.utc



def calculate_sleep_for_seconds(utc_now: datetime, obtain_at_timestamp: tuple, today: bool = True) -> float:
    hour, minute, second = obtain_at_timestamp
    utc_target = datetime(year=utc_now.year, month=utc_now.month, day=utc_now.day, hour=hour, minute=minute, second=second, microsecond=utc_now.microsecond, tzinfo=TZ_UTC)
    timespan = utc_target - utc_now
    if timespan.days < 0:
        timespan += settings.TD_ONE_DAY
    return timespan.seconds


def dbg(msg: str) -> None:
    if settings.IS_DEBUG:
        utc_now = datetime.now(timezone.utc)
        print(f'[{utc_now}] {msg}')


def err(msg: str, error: Exception) -> None:
    utc_now = datetime.now(timezone.utc)
    print(f'[{utc_now}] ERROR  {msg}: {error}')


def get_data_from_url(url: str) -> str:
    data = urllib.request.urlopen(url).read()
    return data.decode('utf-8')


def get_data_from_path(path: str) -> str:
    if path:
        path = path.strip('/')
    url = f'{settings.BASE_URL}{path}'
    return get_data_from_url(url)


def get_dict3_from_path(path: str, key_name: str) -> dict:
    raw_data = get_data_from_path(path)
    result = xmltree_to_dict3(raw_data, key_name)
    return result


def get_elapsed_seconds(start: float) -> float:
    end = time.time()
    result = end - start
    return result


def get_next_matching_timestamp(utc_now: datetime) -> (int, int, int):
    max_hour = max([t[0] for t in settings.OBTAIN_AT_TIMESTAMPS])
    if utc_now.hour > max_hour:
        return settings.OBTAIN_AT_TIMESTAMPS[0]
    for i, t in enumerate(settings.OBTAIN_AT_TIMESTAMPS):
        hour, minute, second = t
        if hour > utc_now.hour:
            return t
        elif hour == utc_now.hour:
            if minute > utc_now.minute:
                return t
            elif minute == utc_now.minute:
                if second >= utc_now.second:
                    return t
                else:
                    return settings.OBTAIN_AT_TIMESTAMPS[(i + 1) % len(settings.OBTAIN_AT_TIMESTAMPS)]


def get_time() -> float:
    return time.time()


def get_utc_now() -> datetime:
    result = datetime.now(TZ_UTC)
    return result


def format_datetime(dt: datetime) -> str:
    return dt.strftime('%Y%m%d-%H%M%S')


def post_wait_message(sleep_for_seconds: float, timestamp: (int, int, int)) -> None:
    minutes, seconds = divmod(sleep_for_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    microseconds = int((seconds - int(seconds)) * 1000000)
    seconds = int(seconds)
    minutes = int(minutes)
    hours = int(hours)
    if hours > 0:
        duration = f'{hours}:{minutes:02d}:{seconds:02d}.{microseconds:06d} hours'
    elif minutes > 0:
        duration = f'{minutes}:{seconds:02d}.{microseconds:06d} minutes'
    elif seconds > 0:
        duration = f'{seconds}.{microseconds:06d} seconds'
    elif microseconds > 0:
        duration = f'{microseconds} microseconds'
    else:
        return
    dbg(f'Waiting for {duration} until {timestamp[0]:02d}:{timestamp[1]:02d}:{timestamp[2]:02d} UTC.')


def save_to_filesystem(content: str, file_name: str) -> None:
    file_name = file_name.strip('/')
    file_name = f'tourney-data/{file_name}'
    try:
        with open(file_name, 'w+') as json_file:
            json_file.write(content)
    except Exception as error:
        err('Could not open or write the file', error)


def save_to_gdrive(content: str, file_name: str) -> None:
    gdrive.init(force=True)
    try:
        gdrive.upload_file(file_name, content)
    except Exception as error:
        err(f'Could not upload the file to google drive', error)
    else:
        dbg(f'Successfully uploaded {file_name} to google drive.')


def should_obtain_data(utc_now: datetime) -> bool:
    result = (utc_now.hour, utc_now.minute, utc_now.second) in settings.OBTAIN_AT_TIMESTAMPS
    return result


def xmltree_to_dict3(raw_text: str, key_name: str) -> dict:
    root = xml.etree.ElementTree.fromstring(raw_text)
    d = {}
    for c in root:
        for cc in c:
            for ccc in cc:
                d[ccc.attrib[key_name]] = ccc.attrib
    return d
