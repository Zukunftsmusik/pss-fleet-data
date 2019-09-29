

import os
import sys
import time

import alliances
import gdrive
import pydrive
import utility as util


PWD = os.getcwd()
sys.path.insert(0, f'{PWD}/')


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





if __name__ == '__main__':
    main()