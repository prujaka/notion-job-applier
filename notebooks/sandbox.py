import pandas as pd

from jobapplier.constants import (URL_DATABASE, API_HEADERS, CV_RAW_PATH,
                                  CV_RENAMED_PATH, DATA_PATH)
from jobapplier.cv import cvfy
import shutil
from pathlib import Path
import requests

