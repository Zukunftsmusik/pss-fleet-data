#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import getopt
import json
import os
import sys

import excel
import filter_data
import settings
import utility as util




def main():
    raw_data = {}
    for file_name in settings.files_to_process:
        file_path = os.path.join(settings.directory, file_name)
        content = None
        with open(file_path, 'r') as data_file:
            try:
                content = json.load(data_file)
            except:
                continue
            else:
                if content and isinstance(content, dict):
                    timestamp = util.extract_timestamp_from_file_name(file_name)
                    raw_data[timestamp] = content
    data = create_ordered_data(raw_data)
    #data = filter_data.by_user_names(['Namith\u270c\ufe0e', '.Xeon.'], data)
    if data:
        excel.create_xl_from_data(data, settings.process_output_file_name)
    else:
        util.prnt(f'No data match found')


def create_ordered_data(raw_data: dict) -> list:
    """ This function will output 1 dicts:
         - Tournament data, with the following column format:
           - output timestamp
           - user id
           - user name
           - fleet id
           - fleet name
           - trophy count
           - star count"""
    tournament_data = [(
        settings.COLUMN_NAME_TIMESTAMP,
        settings.COLUMN_NAME_USER_ID,
        settings.COLUMN_NAME_USER_NAME,
        settings.COLUMN_NAME_FLEET_ID,
        settings.COLUMN_NAME_FLEET_NAME,
        settings.COLUMN_NAME_TROPHIES,
        settings.COLUMN_NAME_STARS
    )]
    for timestamp, data in raw_data.items():
        for user_id, tourney_data in data.items():
            user_name = tourney_data['UserName']
            fleet_id = tourney_data['AllianceId']
            fleet_name = tourney_data['AllianceName']
            trophies = tourney_data['Trophies']
            stars = tourney_data['Stars']

            tournament_data.append((timestamp, user_id, user_name, fleet_id, fleet_name, trophies, stars))
    return tournament_data


def init():
    working_directory = f'{os.getcwd()}/'
    sys.path.insert(0, working_directory)

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


def print_help():
    print(f'Usage: main.py [-d <directory>] [-f <file>[<file 2> ... <file n>]]\n')
    print(f'       -d:  Path to source directory containing the specified files. Default is current directory.')
    print(f'    --dir:  see option \'d\'')
    print(f'       -f:  List of file names to process. Default is all files in specified directory. MUST BE THE LAST ARGUMENT!')
    print(f'  --files:  see option \'f\'')
    print('')
    sys.exit()


if __name__ == '__main__':
    cli_args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(cli_args, 'hf:d:', 'files=dir=')
    except getopt.GetoptError:
        print_help()
    else:
        i = 0
        while i < len(cli_args):
            opt = cli_args[i]
            if opt == 'h':
                print_help()
            if opt == '-f' or opt == '--files':
                i += 1
                check_files_arg(cli_args[i:])
                break
            elif opt == '-d' or opt == '--dir':
                i += 1
                check_dir_arg(cli_args[i])
            i += 1

    init()
    main()