from jobapplier.constants import URL_DATABASE, API_HEADERS
import requests

search_response = requests.post(url=URL_DATABASE, headers=API_HEADERS)
search_response_dict = search_response.json()
