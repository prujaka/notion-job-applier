import argparse
from cv import copy_and_rename_cvs
from api_requests import add_cover_letters, company_substring_entries
from constants import (LISTINGS_INIT_FILE, URL_TEST_DATABASE,
                       API_HEADERS, URL_JOB_TRACKER_2_DATABASE)
from tabulate import tabulate

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    choices = ['rename_cvs', 'fill_cover_letters', 'if_applied']
    parser.add_argument('-a', '--action', choices=choices)
    parser.add_argument('-c', '--company')
    args = parser.parse_args()

    if vars(args)['action'] == 'rename_cvs':
        copy_and_rename_cvs(url=URL_JOB_TRACKER_2_DATABASE, headers=API_HEADERS)

    if vars(args)['action'] == 'fill_cover_letters':
        responses = add_cover_letters(database_url=URL_JOB_TRACKER_2_DATABASE,
                                      headers=API_HEADERS,
                                      block_type='paragraph')

    if vars(args)['action'] == 'if_applied':
        company = vars(args)['company']
        df_applied = company_substring_entries(
            substring=company,
            url=URL_JOB_TRACKER_2_DATABASE,
            headers=API_HEADERS
        )
        print(tabulate(df_applied, headers='keys', tablefmt='psql'))
