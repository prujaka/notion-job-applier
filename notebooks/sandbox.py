import pandas as pd
from openai import OpenAI

from jobapplier.constants import (
    URL_JOB_TRACKER_2_DATABASE, API_HEADERS, OPENAI_KEY, CV_RAW_PATH,
    CV_RENAMED_PATH, DATA_PATH, API_HEADERS, URL_JOB_TRACKER_2_DATABASE
)
from jobapplier.api_requests import fetch_database_jsons
from jobapplier.constants import API_HEADERS, URL_JOB_TRACKER_2_DATABASE
from jobapplier.data_preprocessing import build_dataframe
from jobapplier.cv import cvfy
import shutil
from pathlib import Path
import requests

results = fetch_database_jsons(url=URL_JOB_TRACKER_2_DATABASE,
                               headers=API_HEADERS)

client = OpenAI(api_key=OPENAI_KEY)

prompt = "Check the website https://www.delos.so/ and tell what the company does."

response = client.responses.create(
    model="gpt-4.1",
    input=prompt
)
# print(response.output_text)


database = fetch_database_jsons(url=URL_JOB_TRACKER_2_DATABASE,
                                headers=API_HEADERS)
df = build_dataframe(database)
