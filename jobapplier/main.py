import argparse
from cv import copy_and_rename_cvs
from api_requests import add_cover_letters
from constants import (LISTINGS_INIT_FILE, URL_TEST_DATABASE,
                       API_HEADERS, URL_JOB_TRACKER_2_DATABASE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action',
                        choices=['rename_cvs', 'fill_cover_letters'])
    args = parser.parse_args()

    if vars(args)['action'] == 'rename_cvs':
        copy_and_rename_cvs(listings_csv=LISTINGS_INIT_FILE)

    if vars(args)['action'] == 'fill_cover_letters':
        responses = add_cover_letters(database_url=URL_JOB_TRACKER_2_DATABASE,
                                      headers=API_HEADERS,
                                      block_type='paragraph')
        print("Cover letters are generated and added to the Notion database.")
