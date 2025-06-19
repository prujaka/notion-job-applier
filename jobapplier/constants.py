from configparser import ConfigParser


config = ConfigParser()
config.read('../config.ini')

API_KEY = config['secrets']['api_key']
DATABASE_ID = config['databases']['database_id']
