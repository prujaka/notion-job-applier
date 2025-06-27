import pandas as pd

from jobapplier.constants import (URL_DATABASE, API_HEADERS, CV_RAW_PATH,
                                  CV_RENAMED_PATH, DATA_PATH)
from jobapplier.cv import cvfy
import shutil
from pathlib import Path
import requests
import pandas


df_listings = pd.read_csv(DATA_PATH.joinpath("listings.csv"))
job_titles = df_listings['job_title'].to_list()
languages = df_listings['language'].to_list()
cv_filenames = [
    cvfy(title, lang) + ".pdf" for (title, lang) in zip(job_titles, languages)
]
cv_paths_raw = sorted(CV_RAW_PATH.glob("*.pdf"))
cv_paths_to_rename = [
    CV_RENAMED_PATH.joinpath(filename) for filename in cv_filenames
]
for (cv_raw, cv_to_rename) in zip(cv_paths_raw, cv_paths_to_rename):
    shutil.copy2(cv_raw, cv_to_rename)
