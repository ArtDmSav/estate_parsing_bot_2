import configparser
from pathlib import Path

# Absolut path
dir_path = Path.cwd()
path = Path(dir_path, 'config', 'config.ini')
config = configparser.ConfigParser()
config.read(path)

# Constants
BOT_TOKEN = config['Telegram']['bot_token']
BOT_USERNAME = config['Telegram']['bot_username']
USERNAME = config['Telegram']['username']
API_ID = config['Telegram']['api_id']
API_HASH = config['Telegram']['api_hash']
DEL_MSG_AFTER_DAY = 7
LOOP_SLEEP = 60 * 10  # loop restart every 10 min
CHECK_FOR_DEL_MSG_TIME = 144  # sleep(10min) * 144 = 24h
TELEGRAM_GROUPS = (config['Telegram']['group_1'], config['Telegram']['group_2'], config['Telegram']['group_3'])
