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
        content = None
        with open(file_path, 'r') as data_file:
            try:
                content = json.load(data_file)
            except:
                continue
            else:
                if content and isinstance(content, (list, tuple)):
                    raw_data[timestamp] = content[0]
    data = excel.create_ordered_data(raw_data)

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