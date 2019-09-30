#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import getopt
import os
import sys
import time

import alliances
import gdrive
import pydrive
import settings
import utility as util



def main():
    latest_timestamp = None

    while True:
        utc_now = util.get_utc_now()
        next_timestamp = util.get_next_matching_timestamp(utc_now)
        obtain_data = util.should_obtain_data(utc_now) and latest_timestamp != next_timestamp
        if obtain_data:
            latest_timestamp = next_timestamp
            alliances.retrieve_and_store_user_infos()
        else:
            utc_now = util.get_utc_now()
            next_timestamp = util.get_next_matching_timestamp(utc_now)
            sleep_for_seconds = util.calculate_sleep_for_seconds(utc_now, next_timestamp)
            sleep_for_seconds -= utc_now.microsecond / 1000000
            if sleep_for_seconds < 0:
                sleep_for_seconds = 0
            util.post_wait_message(sleep_for_seconds, next_timestamp)
            time.sleep(sleep_for_seconds)


def init(store_at_filesystem: bool = True, store_at_gdrive: bool = True):
    PWD = os.getcwd()
    sys.path.insert(0, f'{PWD}/')

    if store_at_filesystem is not None:
        util.dbg(f'Store at filesystem: {store_at_filesystem}')
        settings.STORE_AT_FILESYSTEM = store_at_filesystem
    if store_at_gdrive is not None:
        util.dbg(f'Store at google drive: {store_at_gdrive}')
        settings.STORE_AT_GDRIVE = store_at_gdrive

    if settings.FOLDERS_TO_BE_CREATED:
        for folder_name in settings.FOLDERS_TO_BE_CREATED:
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)


def print_help():
    bool_values = list(settings.FALSE_VALUES)
    bool_values.extend(settings.TRUE_VALUES)
    print(f'Usage: main.py [-h] [-f <bool>] [-g <bool>]\n')
    print(f'       -f:  <bool> store at file system (default is {settings.STORE_AT_FILESYSTEM})')
    print(f'     --fs:  see option \'f\'')
    print(f'       -g:  <bool> store at google drive (default is {settings.STORE_AT_GDRIVE})')
    print(f' --gdrive:  see option \'g\'')
    print(f'\nbool values: {", ".join(bool_values)}\n')
    sys.exit()


def __check_bool_arg(arg: str) -> bool:
    arg = str(arg).lower()
    if arg in settings.TRUE_VALUES:
        return True
    elif arg in settings.FALSE_VALUES:
        return False
    else:
        print_help()



if __name__ == '__main__':
    store_at_filesystem = None
    store_at_gdrive = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hf:g:', 'fs=gdrive=')
    except getopt.GetoptError:
        print_help()
    else:
        for opt, arg in opts:
            if opt == '-h':
                print_help()
                break
            elif opt == '-f' or opt == '--fs':
                store_at_filesystem = __check_bool_arg(arg)
            elif opt == '-g' or opt == '--gdrive':
                store_at_gdrive = __check_bool_arg(arg)

    init(store_at_filesystem=store_at_filesystem, store_at_gdrive=store_at_gdrive)
    main()