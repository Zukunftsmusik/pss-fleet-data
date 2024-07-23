import json
import logging
import os
import time
import urllib.request
import xml.etree.ElementTree
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

import gdrive
import settings


# ---------- Constants ----------

__BYTE_COUNT: List[str] = ["B", "KiB", "MiB", "GiB", "TiB"]

ONE_DAY: timedelta = timedelta(days=1)
ONE_HOUR: timedelta = timedelta(hours=1)


# ---------- Classes ----------


class AccessTokenExpiredError(Exception):
    pass


# ---------- CLI output ----------


def dbg(msg: str) -> None:
    logging.debug(msg)


def err(msg: str, exc: Exception = None) -> None:
    if exc is None:
        msg = f"ERROR  {msg}"
    else:
        msg = f"ERROR  {msg}\n{exc}"
    logging.error(msg)


def post_wait_message(sleep_for_seconds: float, timestamp: Tuple[int, int, int]) -> None:
    minutes, seconds = divmod(sleep_for_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    microseconds = int((seconds - int(seconds)) * 1000000)
    seconds = int(seconds)
    minutes = int(minutes)
    hours = int(hours)
    if hours > 0:
        duration = f"{hours}:{minutes:02d}:{seconds:02d}.{microseconds:06d} hours"
    elif minutes > 0:
        duration = f"{minutes}:{seconds:02d}.{microseconds:06d} minutes"
    elif seconds > 0:
        duration = f"{seconds}.{microseconds:06d} seconds"
    elif microseconds > 0:
        duration = f"{microseconds} microseconds"
    else:
        return
    prnt(f"Waiting for {duration} until {timestamp[0]:02d}:{timestamp[1]:02d}:{timestamp[2]:02d} UTC.")


def print_dict(dct: dict, level: int = 0) -> None:
    for key, value in dct.items():
        indention = "  " * level
        if isinstance(value, dict):
            print(f"{indention}{key}: {{")
            print_dict(value, level + 1)
            print(f"{indention}}}")
        elif isinstance(value, list):
            print(f"{indention}{key}: [")
            print_list(value, level + 1)
            print(f"{indention}]")
        else:
            print(f"{indention}{key}: {value},")


def print_list(lst: list, level: int = 0) -> None:
    for value in lst:
        indention = "  " * level
        if isinstance(value, dict):
            print_dict(value, level + 1)
        elif isinstance(value, list):
            print(f"{indention}[")
            print_list(value, level + 1)
            print(f"{indention}]")
        else:
            print(f"{indention}{value},")


def prnt(msg: str) -> None:
    logging.info(msg)


def vrbs(msg: str) -> None:
    if settings.SETTINGS["print_verbose"]:
        logging.info(msg)


# ---------- Datetime and time ----------


def calculate_sleep_for_seconds(utc_now: datetime, obtain_at_timestamp: tuple) -> float:
    hour, minute, second = obtain_at_timestamp
    utc_target = datetime(
        year=utc_now.year,
        month=utc_now.month,
        day=utc_now.day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=utc_now.microsecond,
        tzinfo=settings.DEFAULT_TIMEZONE,
    )
    timespan = utc_target - utc_now
    if timespan.days < 0:
        timespan += settings.TIMEDELTA_ONE_DAY
    return timespan.seconds


def convert_file_timestamp_to_output(timestamp: str) -> str:
    dt = parse_file_timestamp(timestamp)
    result = dt.strftime(settings.TIMESTAMP_FORMAT_OUTPUT)
    return result


def convert_to_bytes_count(bytes: int) -> str:
    exponent = 0
    while bytes > 1024.0:
        bytes /= 1024
        exponent += 1
    if exponent:
        result = f"{bytes:.2f} {__BYTE_COUNT[exponent]}"
    else:
        result = f"{bytes:d} {__BYTE_COUNT[exponent]}"
    return result


def pss_timestamp_to_ordinal(timestamp: str) -> int:
    dt = parse_pss_timestamp(timestamp)
    if dt < settings.PSS_START_DATE:
        return 0
    else:
        result = dt - settings.PSS_START_DATE
        return int(result.total_seconds())


def extract_timestamp_from_file_name(file_name: str, prefix: str = None, suffix: str = None) -> str:
    if not prefix:
        prefix = settings.DEFAULT_DATA_FILE_PREFIX
    if not suffix:
        suffix = settings.DEFAULT_DATA_FILE_SUFFIX

    if prefix and file_name.startswith(prefix):
        prefix_len = len(prefix)
        file_name = file_name[prefix_len:]
    if suffix and file_name.endswith(suffix):
        file_name_without_suffix_len = len(file_name) - len(suffix)
        file_name = file_name[:file_name_without_suffix_len]

    return file_name


def format_file_timestamp(timestamp: datetime) -> str:
    result = timestamp.strftime(settings.TIMESTAMP_FORMAT_SOURCE_FILE_NAME)
    return result


def format_output_timestamp(timestamp: datetime) -> str:
    result = timestamp.strftime(settings.TIMESTAMP_FORMAT_OUTPUT)
    return result


def format_pss_timestamp(timestamp: datetime) -> str:
    result = timestamp.strftime(settings.TIMESTAMP_FORMAT_PSS)
    return result


def get_first_of_next_month(utc_now: datetime = None) -> datetime:
    if utc_now is None:
        utc_now = get_utc_now()
    year = utc_now.year
    month = utc_now.month + 1
    if month == 13:
        year += 1
        month = 1
    result = datetime(year, month, 1, 0, 0, 0, 0, timezone.utc)
    return result


def get_utc_now() -> datetime:
    result = datetime.now(settings.DEFAULT_TIMEZONE)
    return result


def parse_file_timestamp(timestamp: str) -> datetime:
    result = datetime.strptime(timestamp, settings.TIMESTAMP_FORMAT_SOURCE_FILE_NAME)
    return result


def parse_output_timestamp(timestamp: str) -> datetime:
    result = datetime.strptime(timestamp, settings.TIMESTAMP_FORMAT_OUTPUT)
    return result


def parse_pss_timestamp(timestamp: str) -> datetime:
    result = datetime.strptime(timestamp, settings.TIMESTAMP_FORMAT_PSS)
    return result


# ---------- Data Retrieval ----------


def get_production_server(latest_settings: dict = None) -> str:
    if settings.PRODUCTION_SERVER:
        return f"https://{settings.PRODUCTION_SERVER}/"

    latest_settings = latest_settings or get_latest_settings()
    production_server = latest_settings.get("ProductionServer") or settings.API_BASE_URL
    return f"https://{production_server}/"


def get_data_from_url(url: str) -> str:
    data = urllib.request.urlopen(url).read()
    return data.decode("utf-8")


def get_data_from_path(path: str, api_server: str = None) -> str:
    if not api_server:
        api_server = get_production_server()
    if path:
        path = path.strip("/")
    url = f"{api_server}{path}"
    return get_data_from_url(url)


def get_dict2_from_path(path: str, key_name: str, api_server: str) -> Dict[str, dict]:
    raw_data = get_data_from_path(path, api_server)
    result = xmltree_to_dict2(raw_data, key_name)
    return result


def get_dict3_from_path(path: str, key_name: str, api_server: str) -> Dict[str, dict]:
    raw_data = get_data_from_path(path, api_server)
    result = xmltree_to_dict3(raw_data, key_name)
    return result


def get_elapsed_seconds(start: datetime, end: datetime = None) -> float:
    if end is None:
        end = get_utc_now()
    duration: timedelta = end - start
    result = float(duration.seconds) + float(duration.microseconds) / 1000000
    return result


def get_latest_settings() -> dict:
    url = f"{settings.API_BASE_URL}{settings.SETTINGS_BASE_PATH}"
    data = get_data_from_url(url)
    d = xmltree_to_dict2(data, "SettingId")
    for latest_settings in d.values():
        if "ProductionServer" in latest_settings:
            return latest_settings
    return {}


def xmltree_to_dict2(raw_text: str, key_name: str) -> Dict[str, dict]:
    if "Access token expired." in raw_text:
        raise AccessTokenExpiredError()
    root = xml.etree.ElementTree.fromstring(raw_text)
    d = {}
    for c in root:
        for cc in c:
            if key_name in cc.attrib:
                d[cc.attrib[key_name]] = cc.attrib
    return d


def xmltree_to_dict3(raw_text: str, key_name: str) -> Dict[str, dict]:
    if "Access token expired." in raw_text:
        raise AccessTokenExpiredError()
    root = xml.etree.ElementTree.fromstring(raw_text)
    d = {}
    for c in root:
        for cc in c:
            for ccc in cc:
                if key_name in ccc.attrib:
                    d[ccc.attrib[key_name]] = ccc.attrib
    return d


# ---------- Storage ----------


def save_to_filesystem(content: str, file_name: str, folder_path: str) -> None:
    file_path = os.path.join(folder_path, file_name)
    try:
        with open(file_path, "w+") as write_file:
            write_file.write(content)
    except Exception as error:
        err(f"Could not create, open or write the file at: {file_path}", error)


def save_to_gdrive(content: str, file_name: str) -> None:
    gdrive.init(force=True)
    try:
        gdrive.upload_file(file_name, content)
    except Exception as error:
        err("Could not upload the file to google drive", error)
    else:
        prnt(f"Successfully uploaded {file_name} to google drive.")


def dump_data(data: object, file_name: str, folder_path: str) -> None:
    file_path = os.path.join(folder_path, file_name)
    try:
        vrbs(f"Start dumping data to file: {file_path}")
        with open(file_path, "w+") as write_file:
            json.dump(data, write_file)
        vrbs(f"Dumped data to file: {file_path}")
    except Exception as error:
        err(f"Could not create, open or write the file at: {file_path}", error)


def update_data(data: object, file_name: str, folder_path: str) -> None:
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r") as read_file:
                data_old = json.load(read_file)
        except Exception as error:
            err(f"Could not read old data from file at: {file_path}", error)
        else:
            data.extend(data_old)
            data = remove_duplicates(data)
    dump_data(data, file_name, folder_path)


# ---------- Tournament ----------


def get_current_tourney_start(utc_now: datetime = None) -> datetime:
    if utc_now is None:
        utc_now = get_utc_now()
    first_of_next_month = get_first_of_next_month(utc_now=utc_now)
    result = first_of_next_month - settings.TIMEDELTA_ONE_WEEK
    return result


def is_tourney_running(start_date: datetime = None, utc_now: datetime = None) -> bool:
    utc_now = utc_now or get_utc_now()
    start_date = start_date or get_current_tourney_start(utc_now)

    return start_date <= utc_now


# ---------- Uncategorized ----------


def get_collect_file_name(utc_now: datetime) -> str:
    result = f"{settings.FILE_NAME_COLLECT_PREFIX}{format_file_timestamp(utc_now)}{settings.FILE_NAME_COLLECT_SUFFIX}"
    return result


def get_next_matching_timestamp(utc_now: datetime, obtain_at_timestamps: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
    obtain_at_timestamps = list(obtain_at_timestamps)
    max_hour = max([t[0] for t in obtain_at_timestamps])
    if utc_now.hour > max_hour:
        return obtain_at_timestamps[0]
    for i, t in enumerate(obtain_at_timestamps):
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
                    return obtain_at_timestamps[(i + 1) % len(obtain_at_timestamps)]


def get_rank_number(rank: str) -> int:
    result = settings.RANKS_LOOKUP[rank]
    return result


def init_logging(debug: bool = None):
    logging_level = logging.INFO

    if debug:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format="%(asctime)s  %(levelname)-8.8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logging.Formatter.converter = time.gmtime


def remove_duplicates(_from: List[Any]) -> List[Any]:
    if not _from:
        return _from

    result = []
    for item in _from:
        if item not in result:
            result.append(item)

    return result


def should_obtain_data(utc_now: datetime, obtain_at_timestamps: list) -> bool:
    result = (utc_now.hour, utc_now.minute, utc_now.second) in obtain_at_timestamps
    return result
