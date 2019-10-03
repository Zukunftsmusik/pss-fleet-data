#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import getopt
import os
import sys
import time

import fleet_data
import gdrive
import pydrive
import settings
import utility as util



def main():
    latest_timestamp = None

    while True:
        utc_now = util.get_utc_now()
        next_timestamp = util.get_next_matching_timestamp(utc_now, settings.obtain_at_timestamps)
        obtain_data = util.should_obtain_data(utc_now, settings.obtain_at_timestamps) and latest_timestamp != next_timestamp
        if obtain_data:
            latest_timestamp = next_timestamp
            fleet_data.retrieve_and_store_user_infos()
        else:
            utc_now = util.get_utc_now()
            next_timestamp = util.get_next_matching_timestamp(utc_now, settings.obtain_at_timestamps)
            sleep_for_seconds = util.calculate_sleep_for_seconds(utc_now, next_timestamp)
            sleep_for_seconds -= utc_now.microsecond / 1000000
            if sleep_for_seconds < 0:
                sleep_for_seconds = 0
            util.post_wait_message(sleep_for_seconds, next_timestamp)
            time.sleep(sleep_for_seconds)


def init(store_at_filesystem: bool = None, store_at_gdrive: bool = None, verbose: bool = None):
    PWD = os.getcwd()
    sys.path.insert(0, f'{PWD}/')

    if verbose is not None:
        settings.print_verbose = verbose

    if store_at_filesystem is None:
        util.vrbs(f'Store at filesystem: {settings.store_at_fileystem}')
    else:
        util.vrbs(f'Store at filesystem: {store_at_filesystem}')
        settings.store_at_fileystem = store_at_filesystem

    if store_at_gdrive is None:
        util.vrbs(f'Store at google drive: {settings.store_at_gdrive}')
    else:
        util.vrbs(f'Store at google drive: {store_at_gdrive}')
        settings.store_at_gdrive = store_at_gdrive

    for folder_name in settings.CREATE_FOLDERS_ON_COLLECT:
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)


def print_help():
    bool_values = list(settings.CLI_FALSE_VALUES)
    bool_values.extend(settings.CLI_TRUE_VALUES)
    print(f'Usage: main.py [-h] [-f <bool>] [-g <bool>]\n')
    print(f'       -f:  <bool> store at file system (default is {settings.store_at_filesystem})')
    print(f'     --fs:  see option \'f\'')
    print(f'       -g:  <bool> store at google drive (default is {settings.store_at_gdrive})')
    print(f' --gdrive:  see option \'g\'')
    print(f'\nbool values: {", ".join(bool_values)}\n')
    sys.exit()


def __check_bool_arg(arg: str) -> bool:
    arg = str(arg).lower()
    if arg in settings.CLI_TRUE_VALUES:
        return True
    elif arg in settings.CLI_FALSE_VALUES:
        return False
    else:
        print_help()




if __name__ == '__main__':
    store_at_filesystem = None
    store_at_gdrive = None
    verbose = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hvf:g:', '')
    except getopt.GetoptError:
        print_help()
    else:
        for opt, arg in opts:
            if opt == '-h':
                print_help()
            elif opt == '-v':
                verbose = True
            elif opt == '-f':
                store_at_filesystem = __check_bool_arg(arg)
            elif opt == '-g':
                store_at_gdrive = __check_bool_arg(arg)

    init(store_at_filesystem=store_at_filesystem, store_at_gdrive=store_at_gdrive, verbose=verbose)
    main()