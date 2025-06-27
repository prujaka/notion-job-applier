import argparse
from jobapplier.cv import copy_and_rename_cvs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', choices=['rename_cvs'])
    args = parser.parse_args()

    if vars(args)['action'] == 'rename_cvs':
        copy_and_rename_cvs()
