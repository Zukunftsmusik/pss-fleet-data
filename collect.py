import getopt
import os
import sys
import time

import clean
import fleet_data
import gdrive
import settings
import utility as util


def main(run_once: bool = None):
    latest_timestamp = None
    run_once = run_once or settings.RUN_ONCE

    if run_once:
        fleet_data.retrieve_and_store_user_infos()
    else:
        while True:
            utc_now = util.get_utc_now()
            next_timestamp = util.get_next_matching_timestamp(utc_now, settings.obtain_at_timestamps)
            obtain_data = util.should_obtain_data(utc_now, settings.obtain_at_timestamps) and latest_timestamp != next_timestamp
            if obtain_data:
                latest_timestamp = next_timestamp
                fleet_data.retrieve_and_store_user_infos()
                if utc_now.month != (utc_now + util.ONE_HOUR).month:
                    clean.clean_up_gdrive(utc_now)
            else:
                utc_now = util.get_utc_now()
                next_timestamp = util.get_next_matching_timestamp(utc_now, settings.obtain_at_timestamps)
                sleep_for_seconds = util.calculate_sleep_for_seconds(utc_now, next_timestamp)
                sleep_for_seconds -= utc_now.microsecond / 1000000
                if sleep_for_seconds < 0:
                    sleep_for_seconds = 0
                util.post_wait_message(sleep_for_seconds, next_timestamp)
                time.sleep(sleep_for_seconds)





def init(store_at_filesystem: bool = None, store_at_gdrive: bool = None, verbose: bool = None, no_time: bool = None) -> dict:
    PWD = os.getcwd()
    sys.path.insert(0, f'{PWD}/')


    if verbose is not None:
        settings.SETTINGS['print_verbose'] = verbose

    if no_time is None:
        util.vrbs(f'Print timestamps: {settings.SETTINGS["print_timestamps"]}')
    else:
        print_timestamps = not no_time
        settings.SETTINGS['print_timestamps'] = print_timestamps
        util.vrbs(f'Print timestamps: {print_timestamps}')

    if store_at_filesystem is None:
        util.vrbs(f'Store at filesystem: {settings.SETTINGS["store_at_fileystem"]}')
    else:
        settings.SETTINGS['store_at_filesystem'] = store_at_filesystem
        util.vrbs(f'Store at filesystem: {store_at_filesystem}')

    if store_at_gdrive is None:
        util.vrbs(f'Store at google drive: {settings.SETTINGS["store_at_gdrive"]}')
    else:
        settings.SETTINGS['store_at_gdrive'] = store_at_gdrive
        util.vrbs(f'Store at google drive: {store_at_gdrive}')
        if store_at_gdrive:
            gdrive.init()

    for folder_name in settings.CREATE_FOLDERS_ON_COLLECT:
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)


def print_help():
    bool_values = list(settings.CLI_FALSE_VALUES)
    bool_values.extend(settings.CLI_TRUE_VALUES)
    print(f'Usage: collect.py [-fghv] [--once] [--notime]\n')
    print(f'-f:       Store at file system')
    print(f'-g:       Store at google drive')
    print(f'-h:       Print this help')
    print(f'--notime: Suppress timestamps on cli output')
    print(f'--once:   Run only once')
    print(f'-v:       Verbose mode')
    print(f'\n')
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
    cli_args = sys.argv[1:]
    no_time = False
    run_once = False
    store_at_filesystem = False
    store_at_gdrive = False
    verbose = False

    try:
        opts, args = getopt.getopt(cli_args, 'hvfg', ['once', 'notime'])
    except getopt.GetoptError:
        print_help()
    else:
        for opt, arg in opts:
            if opt == '-f':
                store_at_filesystem = True
            elif opt == '-g':
                store_at_gdrive = True
            elif opt == '-h':
                print_help()
            elif opt == '--once':
                run_once = True
            elif opt == '--notime':
                no_time = True
            elif opt == '-v':
                verbose = True

    init(store_at_filesystem=store_at_filesystem, store_at_gdrive=store_at_gdrive, verbose=verbose, no_time=no_time)
    main(run_once=run_once)