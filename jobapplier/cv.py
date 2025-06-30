import shutil
import string

import pandas as pd
from nltk.tokenize import word_tokenize
from unidecode import unidecode

from constants import CV_RAW_PATH, CV_RENAMED_PATH, DATA_PATH


def get_sep(lang: str):
    if lang == 'FR':
        return '-'
    elif lang == 'EN':
        return '_'
    else:
        raise KeyError("Please choose the language from ['EN', 'FR']")


def cvfy(text: str, lang: str) -> str:
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


def copy_and_rename_cvs(listings_csv):
    df_listings = pd.read_csv(DATA_PATH.joinpath(listings_csv))
    job_titles = df_listings['job_title'].to_list()
    languages = df_listings['language'].to_list()
    cv_filenames = [
        cvfy(title, lang) + ".pdf" for (title, lang) in
        zip(job_titles, languages)
    ]
    cv_paths_raw = sorted(CV_RAW_PATH.glob("*.pdf"))
    cv_paths_to_rename = [
        CV_RENAMED_PATH.joinpath(filename) for filename in cv_filenames
    ]
    for (cv_raw, cv_to_rename) in zip(cv_paths_raw, cv_paths_to_rename):
        shutil.copy(cv_raw, cv_to_rename)

    return None
