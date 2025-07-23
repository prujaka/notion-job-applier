import requests


def fetch_database_jsons(url: str, headers: dict) -> list:
    """
    Fetch all paginated JSON entries from a Notion database and return them
    as a list.

    Args:
        url (str): The Notion API endpoint URL for querying the database.
        headers (dict): A dictionary of HTTP headers including authorization
            and version info.

    Returns:
        list: A list of all database entry objects returned by the Notion API.
    """
    has_more = True
    cursor = None
    results = []
    body = {}

    while has_more:
        if not cursor:
            search_response = requests.post(url=url, headers=headers)
        else:
            search_response = requests.post(url=url, headers=headers, json=body)

        search_response_dict = search_response.json()
        has_more = search_response_dict["has_more"]
        cursor = search_response_dict["next_cursor"]
        body = {"start_cursor": cursor}

        results_loc = search_response_dict["results"]
        results += results_loc

    return results
