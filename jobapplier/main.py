import argparse
from cv import copy_and_rename_cvs
from cover_letter import add_cover_letters
from constants import LISTINGS_INIT_FILE


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action',
                        choices=['rename_cvs', 'fill_cover_letters'])
    args = parser.parse_args()

    if vars(args)['action'] == 'rename_cvs':
        copy_and_rename_cvs(listings_csv=LISTINGS_INIT_FILE)

    if vars(args)['action'] == 'fill_cover_letters':
        add_cover_letters(listings_init_csv=LISTINGS_INIT_FILE,
                          listings_with_covers_csv=LISTINGS_INIT_FILE)
