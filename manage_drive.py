from datetime import datetime, timedelta

import gdrive
import settings
import utility as utils


ONE_DAY = timedelta(days=1)


def delete_all_files_but_latest_daily(from_year: int = None, from_month: int = None, from_day: int = None, to_year: int = None, to_month: int = None, to_day: int = None):
    gdrive.init()
    utc_now = utils.get_utc_now()
    if not from_year and not from_month and not from_day:
        from_timestamp = datetime(2019, 10, 9, tzinfo=settings.DEFAULT_TIMEZONE)
    else:
        from_year = from_year or 2019
        from_month = from_month or 10 if from_year == 2019 else 1
        from_day = from_day or 9 if from_year == 2019 and from_month == 10 else 1
        from_timestamp = datetime(from_year, from_month, from_day, tzinfo=settings.DEFAULT_TIMEZONE)

    to_year = to_year or utc_now.year
    to_month = to_month or utc_now.month
    to_day = to_day or utc_now.day
    to_timestamp = datetime(to_year, to_month, to_day, tzinfo=settings.DEFAULT_TIMEZONE) + ONE_DAY

    while from_timestamp < to_timestamp:
        if not utils.is_tourney_running(utc_now=from_timestamp):
            file_name_prefix = f'{settings.FILE_NAME_COLLECT_PREFIX}{from_timestamp.year:02d}{from_timestamp.month:02d}{from_timestamp.day:02d}'
            file_list = gdrive.get_files_in_folder(settings.GDRIVE_FOLDER_ID, file_name_prefix)
            if file_list:
                file_list = sorted(file_list, key=lambda f: f['title'])
                file_list.pop()
            for file in file_list:
                utils.prnt(f'Permanently deleting file: {file["title"]}')
                gdrive.delete_file(file)

        from_timestamp += ONE_DAY


def clear_trash_bin():
    gdrive.init()
    files = gdrive.get_trashed_files()
    for file in files:
        file.Delete()


def get_about():
    gdrive.init()
    about = gdrive.get_about()
    utils.print_dict(about)


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
    utils.prnt(f'Quotas for account: {name}')
    utils.prnt(f'Max Quota: {max_quota} bytes ({utils.convert_to_bytes_count(max_quota)})')
    utils.prnt(f'Used Quota: {used_quota} bytes ({utils.convert_to_bytes_count(used_quota)})')
    utils.prnt(f'Trashed Quota: {trash_quota} bytes ({utils.convert_to_bytes_count(trash_quota)})')
    utils.prnt(f'Available Quota: {available_quota} bytes ({utils.convert_to_bytes_count(available_quota)}, {available_quota_percentage * 100:.2f} %)')


if __name__ == '__main__':
    from_year=2019
    from_month=11
    from_day=1
    to_year=2019
    to_month=12
    to_day=31
    #delete_all_files_but_latest_daily(from_year=from_year, from_month=from_month, from_day=from_day, to_year=to_year, to_month=to_month, to_day=to_day)

    print_quota()
