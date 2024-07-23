from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import manage_drive as manage
import settings


def clean_up_gdrive(utc_now: datetime, remove_from: datetime = None, delete_tourney_data: bool = False) -> None:
    remove_to: datetime = utc_now - relativedelta(months=settings.DELETE_FULL_DATA_AFTER_MONTHS)
    remove_from = remove_from or remove_to - relativedelta(months=1) + timedelta(days=1)

    manage.delete_all_files_but_latest_daily(
        to_year=remove_to.year,
        to_month=remove_to.month,
        to_day=remove_to.day,
        delete_tourney_data=delete_tourney_data
    )

    manage.print_quota()


if __name__ == '__main__':
    clean_up_gdrive(
        datetime(2021, 10, 31, tzinfo=settings.DEFAULT_TIMEZONE),
        datetime(2019, 10, 9, tzinfo=settings.DEFAULT_TIMEZONE),
        delete_tourney_data=True
    )
