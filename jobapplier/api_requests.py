import json

import requests
from requests.models import Response

from jobapplier.cover_letter import build_letter
from jobapplier.data_preprocessing import build_dataframe


def stage_is_none(entry: dict) -> bool:
    """Check whether the 'Stage' property of a JSON entry is None.

    Args:
        entry: Notion database JSON entry.

    Returns:
        bool: True if the 'Stage' property is None, False otherwise.
    """
    return entry['properties']['Stage']['select'] is None


def build_rich_text(text):
    """
    Build a Notion rich text JSON object from a plain text string. If the input
    text's length exceeds 2000 characters, break it down into chunks.

    Args:
        text (str): The text content to include in the rich text object.

    Returns:
        dict: Notion rich text object.
    """
    max_len = 2000
    chunks = [text[i:i + max_len] for i in range(0, len(text), max_len)]
    rich_text = [{
        "type": "text",
        "text": {
            "content": chunk
        }
    } for chunk in chunks]
    return rich_text


def build_codeblock_json(text: str):
    """
    Build a Notion code block JSON object from a plain text string.

    Args:
        text (str): The text content to include in the code block.

    Returns:
        dict: A dictionary representing the Notion code block payload,
            wrapped in a 'children' list.
    """
    rich_text = build_rich_text(text)
    children = {
        "children": [
            {
                "object": "block",
                "type": "code",
                "code": {
                    "caption": [],
                    "rich_text": rich_text,
                    "language": "plain text"
                }
            }
        ]
    }

    return children


def build_paragraph_json(text: str) -> dict:
    """
    Build a Notion paragraph JSON object from a plain text string.

    Args:
        text (str): The text content to include in the paragraph.

    Returns:
        dict: A dictionary representing the Notion paragraph payload,
            wrapped in a 'children' list.
    """
    rich_text = build_rich_text(text)
    children = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text
                }
            }
        ]
    }
    return children


def add_block(text: str, block_id: str, headers: dict,
              block_type: str) -> Response:
    """Append a block to the specified Notion block or page.
    Reference: https://developers.notion.com/reference/patch-block-children

    Args:
        text (str): The text content to include in the block.
        block_id (str): The ID of the parent block or page to append
            the code block to.
        headers (str): Notion API headers for a PATCH request.
        block_type (str): Type of Notion block to create.
            Supported values: 'code', 'paragraph'.

    Returns:
        Response: The HTTP response object returned by the Notion API.
    """
    if block_type == 'code':
        children = build_codeblock_json(text)
    elif block_type == 'paragraph':
        children = build_paragraph_json(text)
    else:
        children = build_paragraph_json(text)
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.patch(url, headers=headers, data=json.dumps(children))
    return response


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


def add_cover_letters(database_url: str, headers: dict):
    results = fetch_database_jsons(url=database_url, headers=headers)
    df_full = build_dataframe(results)
    columns = ['page_id', 'job_title', 'company', 'language']
    df_pending = df_full.loc[df_full['stage'].isna(), columns]
    df_pending['cover_letter'] = df_pending.apply(
        lambda row: build_letter(row['language'], row['company'],
                                 row['job_title']), axis=1)

    responses = []
    for index, row in df_pending.iterrows():
        response = add_block(text=row['cover_letter'],
                             block_id=row['page_id'],
                             headers=headers,
                             block_type='paragraph')
        responses.append(response)

    return responses
