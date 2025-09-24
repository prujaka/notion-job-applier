import shutil
import string

import pandas as pd
from nltk.tokenize import word_tokenize
from unidecode import unidecode

from jobapplier.api_requests import fetch_database_jsons
from jobapplier.constants import CV_RAW_PATH, CV_RENAMED_PATH, DATA_PATH
from jobapplier.data_preprocessing import build_dataframe


def get_sep(lang: str):
    if lang == 'FR':
        return '-'
    elif lang == 'EN':
        return '_'
    else:
        raise KeyError("Please choose the language from ['EN', 'FR']")


def cvfy(text: str, lang: str) -> str:
    """Make the string 'Data Scientist' look like 'cv-data-scientist'"""
    text = text.replace('/', ' ')
    for c in string.punctuation:
        text = text.replace(c, '')
    for c in string.digits:
        text = text.replace(c, '')
    text = unidecode(text)
    text = text.lower()
    tokens = word_tokenize(text)
    sep = get_sep(lang)
    text = sep.join(tokens)
    return f'cv{sep}{text}'


def copy_and_rename_cvs(url: str, headers: dict):
    """Take CVs named with only numbers, cvfy their names and save."""
    all_pages = fetch_database_jsons(url=url,
                                     headers=headers)
    df_jobs = build_dataframe(all_pages)
    df_active_apps = (df_jobs[df_jobs['stage'].isna()]
                      .sort_values(by='position', ascending=False))
    job_titles = df_active_apps['job_title'].to_list()
    languages = df_active_apps['language'].to_list()
    cv_filenames = [
        cvfy(title, lang) + '.pdf' for (title, lang) in
        zip(job_titles, languages)
    ]
    cv_paths_raw = sorted(CV_RAW_PATH.glob('*.pdf'))
    cv_paths_to_rename = [
        CV_RENAMED_PATH.joinpath(filename) for filename in cv_filenames
    ]
    for (cv_raw, cv_to_rename) in zip(cv_paths_raw, cv_paths_to_rename):
        shutil.copy(cv_raw, cv_to_rename)

    return None
