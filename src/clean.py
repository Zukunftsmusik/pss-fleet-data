from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

import manage_drive as manage
import settings
import utility as util


def clean_up_gdrive(utc_now: datetime, remove_from: datetime = None, delete_tourney_data: bool = False) -> None:
    remove_to: datetime = utc_now - relativedelta(months=settings.DELETE_FULL_DATA_AFTER_MONTHS)
    remove_from = remove_from or remove_to - relativedelta(months=1) + timedelta(days=1)

    manage.delete_all_files_but_latest_daily(
        from_year=remove_from.year,
        from_month=remove_from.month,
        from_day=remove_from.day,
        to_year=remove_to.year,
        to_month=remove_to.month,
        to_day=remove_to.day,
        delete_tourney_data=delete_tourney_data,
    )

    manage.print_quota()


if __name__ == "__main__":
    util.init_logging(debug=settings.IS_DEBUG)
    clean_up_gdrive(util.get_utc_now(), remove_from=datetime(2019, 10, 1), delete_tourney_data=True)
