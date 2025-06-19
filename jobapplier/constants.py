from configparser import ConfigParser
from pathlib import Path

CONFIG_NAME = "config.ini"
CONFIG_PATH = Path(__file__).resolve().parent.parent / CONFIG_NAME

config = ConfigParser()
config.read(CONFIG_PATH)

NOTION_API_KEY = config['secrets']['api_key']
DATABASE_ID = config['databases']['database_id']

API_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}
URL_DATABASE = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

