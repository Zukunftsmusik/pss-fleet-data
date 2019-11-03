#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import getopt
import json
import os
import pandas
import sys

import excel
import settings
import utility as util


def main():
    raw_data = {}
    for file_name in settings.files_to_process:
        file_path = os.path.join(settings.directory, file_name)
        timestamp = util.extract_timestamp_from_file_name(file_name)
        content = None
        with open(file_path, 'r') as data_file:
            try:
                content = json.load(data_file)
            except:
                continue
            else:
                if content and isinstance(content, (list, tuple)):
                    raw_data[timestamp] = content[0]
    data = create_ordered_data(raw_data)

    if data:
        excel.create_xl_from_data(data, settings.process_output_file_name)
    else:
        util.prnt(f'No data match found')


def init(verbose: bool = None, no_time: bool = None):
    working_directory = f'{os.getcwd()}/'
    sys.path.insert(0, working_directory)

    if verbose is not None:
        settings.print_verbose = verbose

    if no_time is None:
        util.vrbs(f'Print timestamps: {settings.print_timestamps}')
    else:
        print_timestamps = not no_time
        settings.print_timestamps = print_timestamps
        util.vrbs(f'Print timestamps: {print_timestamps}')

    if settings.directory:
        if not settings.files_to_process:
            files = []
            for _, _, files in os.walk(settings.directory):
                break
            settings.files_to_process = files
    else:
        util.err(f'The directory has not been set.')

    if not settings.files_to_process:
        util.prnt(f'No files to be processed have been found. Exiting...')
        sys.exit()

    settings.process_output_file_name = f'{settings.FILE_NAME_PROCESS_PREFIX}{util.format_file_timestamp(util.get_utc_now())}{settings.FILE_NAME_PROCESS_SUFFIX}'


def check_files_arg(file_names: list) -> None:
    if settings.directory:
        if file_names:
            invalid_files = []
            files = []
            for file_name in file_names:
                file_path = os.path.join(settings.directory, file_name)
                if os.path.isfile(file_path):
                    files.append(file_name)
                else:
                    invalid_files.append(file_name)
            if invalid_files:
                util.err(f'These file names are not valid: {", ".join(invalid_files)}')
            elif files:
                settings.files_to_process = files
    else:
        util.err(f'The directory has not been set.')
        print_help()


def check_dir_arg(dir_path: str) -> None:
    if os.path.isdir(dir_path):
        dir_path = dir_path.rstrip('/')
        settings.directory = f'{dir_path}/'
    else:
        util.err(f'The directory specified does not exist: {dir_path}')


def create_ordered_data(raw_data: dict) -> dict:
    """ This function will output 1 list:
         - Fleet data, with the following column format:
           - timestamp
           - fleet name
           - fleet trophy score
           - fleet star score """
    result = {}
    result[settings.DATA_TYPE_FLEETS] = get_ordered_details(raw_data, settings.DATA_TYPE_FLEETS)
    result[settings.DATA_TYPE_USERS] = get_ordered_details(raw_data, settings.DATA_TYPE_USERS)
    return result


def __get_schema_version(raw_data: dict) -> str:
    result = None
    if 'meta' in raw_data.keys():
        result = '2' # First schema version to contain meta data
        if 'version' in raw_data['meta'].keys():
            result = raw_data['meta']['version']
    return result


def get_fleets_data_v2(raw_data: dict) -> dict:
    meta_data = raw_data['meta']
    fleets_data = raw_data['fleets']
    data = raw_data['data']
    result = []
    for fleet_info in fleets_data:
        fleet_id = fleet_info[0]
        fleet_name = fleet_info[1]
        fleet_trophies = sum([data_point[2] for data_point in data if data_point[1] == fleet_id])
        fleet_stars = fleet_info[2]
        result.append((meta_data['timestamp'], fleet_name, fleet_trophies, fleet_stars))
    return result


def get_ordered_details(raw_data: dict, data_type: str) -> list:
    result = []
    if data_type in settings.DATA_OUTPUT_SCHEMA.keys() and data_type in FUNCTION_MAPPING.keys():
        result = list(settings.DATA_OUTPUT_SCHEMA[data_type].keys())

        for raw_data_session in raw_data.values():
            schema_version = __get_schema_version(raw_data_session)
            if schema_version in FUNCTION_MAPPING[data_type].keys():
                transform_function = FUNCTION_MAPPING[data_type][schema_version]
                result.extend(transform_function(raw_data_session))

    return result


def get_users_data_v2(raw_data: dict) -> dict:
    meta_data = raw_data['meta']
    fleets_data = raw_data['fleets']
    users_data = raw_data['users']
    data = raw_data['data']
    result = []
    for data_point in data:
        user_id = data_point[0]
        user_info = [users_data_point for users_data_point in users_data if users_data_point[0] == user_id][0]
        fleet_id = data_point[1]
        fleet_info = [fleets_data_point for fleets_data_point in fleets_data if fleets_data_point[0] == fleet_id][0]
        fleet_name = fleet_info[1]
        user_name = user_info[1]
        rank = user_info[4]
        last_login = user_info[6]
        trophies = user_info[2]
        stars = user_info[3]
        join_date = user_info[5]
        result.append((meta_data['timestamp'], fleet_name, user_name, rank, last_login, trophies, stars, join_date))
    return result


def print_help():
    print(f'Usage: main.py [-d <directory>] [-f <file>[<file 2> ... <file n>]]\n')
    print(f'       -d:  Path to source directory containing the specified files. Default is current directory.')
    print(f'    --dir:  see option \'d\'')
    print(f'       -f:  List of file names to process. Default is all files in specified directory. MUST BE THE LAST ARGUMENT!')
    print(f'  --files:  see option \'f\'')
    print('')
    sys.exit()


FUNCTION_MAPPING = {
    settings.DATA_TYPE_FLEETS: {
        "2": get_fleets_data_v2
    },
    settings.DATA_TYPE_USERS: {
        "2": get_users_data_v2
    }
}










if __name__ == '__main__':
    cli_args = sys.argv[1:]
    no_time = None
    verbose = None

    try:
        opts, args = getopt.getopt(cli_args, 'hf:d:g', ['notime'])
    except getopt.GetoptError:
        print_help()
    else:
        i = 0
        while i < len(cli_args):
            opt = cli_args[i]
            if opt == '-h':
                print_help()
            if opt == '-f':
                i += 1
                check_files_arg(cli_args[i:])
                break
            elif opt == '-d':
                i += 1
                check_dir_arg(cli_args[i])
            elif opt == '--notime':
                no_time = True
            elif opt == '-v':
                verbose = True
            i += 1

    init(verbose=verbose, no_time=no_time)
    main()