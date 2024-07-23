from datetime import datetime

import gdrive
import settings
import utility as util


def delete_all_files_but_latest_daily(from_year: int = None, from_month: int = None, from_day: int = None, to_year: int = None, to_month: int = None, to_day: int = None, delete_tourney_data: bool = False):
    gdrive.init()
    utc_now = util.get_utc_now()
    if not from_year and not from_month and not from_day:
        from_timestamp = datetime(2019, 10, 9, tzinfo=settings.DEFAULT_TIMEZONE)
    else:
        from_year = from_year or 2019
        from_month = from_month or (10 if from_year == 2019 else 1)
        from_day = from_day or (9 if from_year == 2019 and from_month == 10 else 1)
        from_timestamp = datetime(from_year, from_month, from_day, tzinfo=settings.DEFAULT_TIMEZONE)

    to_year = to_year or utc_now.year
    to_month = to_month or utc_now.month
    to_day = to_day or utc_now.day
    to_timestamp = datetime(to_year, to_month, to_day, tzinfo=settings.DEFAULT_TIMEZONE) + util.ONE_DAY

    while from_timestamp < to_timestamp:
        file_name_prefix = f'{settings.FILE_NAME_COLLECT_PREFIX}{from_timestamp.year:02d}{from_timestamp.month:02d}{from_timestamp.day:02d}'
        util.prnt(f'Checking files for deletion with prefix: {file_name_prefix}')
        if delete_tourney_data or not util.is_tourney_running(utc_now=from_timestamp):
            file_list = gdrive.get_files_in_folder(settings.GDRIVE_FOLDER_ID, file_name_prefix)
            if file_list:
                file_count = len(file_list)
                if file_count > 1:
                    util.prnt(f'Found {len(file_list)} files.')
                else:
                    util.prnt(f'Already clean.')
                file_list = sorted(file_list, key=lambda f: f['title'])
                file_list.pop()
            else:
                util.prnt(f'No such files found.')
            for file in file_list:
                skip = None
                while not skip:
                    tries = 0
                    while tries <= 2:
                        util.prnt(f'Permanently deleting file: {file["title"]}')
                        if gdrive.try_delete_file(file):
                            skip = True
                            break
                        tries += 1 # Attempt to delete 3 times
                    if tries == 3:
                        if skip is None: # If deletion fails 3 times, attempt to re-initialize the gdrive client
                            gdrive.init(force=True)
                            skip = False
                        else:
                            skip = True # If re-initializing the gdrive client doesn't help, skip the file


        from_timestamp += util.ONE_DAY


def clear_trash_bin():
    gdrive.init()
    files = gdrive.get_trashed_files()
    for file in files:
        file.Delete()


def get_about():
    gdrive.init()
    about = gdrive.get_about()
    util.print_dict(about)


def print_quota():
    gdrive.init()
    about = gdrive.get_about()
    name = about.get('name', '-')
    max_quota = int(about.get('quotaBytesTotal', -1))
    used_quota = int(about.get('quotaBytesUsed', -1))
    trash_quota = int(about.get('quotaBytesUsedInTrash', -1))
    combined_quota = used_quota + trash_quota
    combined_quota = combined_quota if combined_quota > -2 else -1
    available_quota = max_quota - combined_quota
    available_quota_percentage = (1 - (combined_quota / max_quota))
    util.prnt(f'Quotas for account: {name}')
    util.prnt(f'Max Quota: {max_quota} bytes ({util.convert_to_bytes_count(max_quota)})')
    util.prnt(f'Used Quota: {used_quota} bytes ({util.convert_to_bytes_count(used_quota)})')
    util.prnt(f'Trashed Quota: {trash_quota} bytes ({util.convert_to_bytes_count(trash_quota)})')
    util.prnt(f'Available Quota: {available_quota} bytes ({util.convert_to_bytes_count(available_quota)}, {available_quota_percentage * 100:.2f} %)')


if __name__ == '__main__':
    # from_year=2021
    # from_month=2
    # from_day=1
    # to_year=2021
    # to_month=6
    # to_day=30
    # delete_all_files_but_latest_daily(from_year=from_year, from_month=from_month, from_day=from_day, to_year=to_year, to_month=to_month, to_day=to_day)

    print_quota()
