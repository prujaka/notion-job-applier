import json
import requests
from requests.models import Response


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


def stage_is_none(entry: dict) -> bool:
    """Check whether the 'Stage' property of a JSON entry is None.

    Returns:
        bool: True if the 'Stage' property is None, False otherwise.
    """
    return entry['properties']['Stage']['select'] is None


def add_code_block(text: str, block_id: str, headers: dict) -> Response:
    """Append a plain text code block to the specified Notion block or page.

    Args:
        text (str): The text content to include in the code block.
        block_id (str): The ID of the parent block or page to append
            the code block to.
        headers (str): Notion API headers for a PATCH request.

    Returns:
        Response: The HTTP response object returned by the Notion API.
    """
    children = build_codeblock_json(text)
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.patch(url, headers=headers, data=json.dumps(children))
    return response


def build_codeblock_json(text: str):
    """
    Build a Notion code block JSON object from a plain text string.

    Args:
        text (str): The text content to include in the code block.

    Returns:
        dict: A dictionary representing the Notion code block payload,
            wrapped in a 'children' list.
    """
    children = {
        "children": [
            {
                "type": "code",
                "code": {
                    "caption": [],
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": text
                        }
                    }],
                    "language": "plain text"
                }
            }
        ]
    }
    return children
