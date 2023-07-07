from config import Config, LOGGER, log_file, user_data, config_dict
from pyrogram import Client
from asyncio import get_event_loop
from time import time
from bot.helper.other.database import Database
from requests import get
from os.path import exists
from ml_config import download_dict_lock, status_reply_dict_lock, queue_dict_lock, status_reply_dict, download_dict, Interval, DRIVES_NAMES, DRIVES_IDS, INDEX_URLS, GLOBAL_EXT_FILTER, aria2_options, queued_dl, queued_up, non_queued_dl, non_queued_up, aria2, aria2c_global


def dw_file_from_url(url, filename):
        r = get(url, allow_redirects=True, stream=True, timeout=60)
        with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024 * 10):
                        if chunk:
                                fd.write(chunk)
        return

botloop = get_event_loop()
botStartTime = time()
DATABASE = True if len(Config.MONGODB_URI) and not Config.MONGODB_URI=='False' else False


if not DATABASE:
        db = False
        LOGGER.info('MongoDB URI Not Found')
else:
        db = Database(close=False)
        botloop.run_until_complete(db.load_user_data())
        botloop.run_until_complete(db.load_config())


if not config_dict:
    for var in vars(Config):
        if not var.startswith('__'):
            config_dict[var] = vars(Config)[var]
    LOGGER.info('Config Imported From Local')
    if DATABASE:
            botloop.run_until_complete(db.save_config())
else:
    newVar = False
    for var in vars(Config):
        if not var.startswith('__') and var not in config_dict:
            config_dict[var] = vars(Config)[var]
            newVar = True
    if newVar and DATABASE:
            botloop.run_until_complete(db.save_config())
    LOGGER.info('Config Imported From Database')



if config_dict['ALLOWED_CHATS']:
    for id_ in config_dict['ALLOWED_CHATS']:
        if id_ not in user_data:
                user_data[int(id_.strip())] = {'is_auth': True}
        else:
                user_data[int(id_.strip())]['is_auth'] = True


if config_dict['SUDO_USERS']:
    for id_ in config_dict['SUDO_USERS']:
        if id_ not in user_data:
                user_data[int(id_.strip())] = {'is_sudo': True}
        else:
                user_data[int(id_.strip())]['is_sudo'] = True


if len(config_dict['RCLONE_CONFIG_URL']) and str(config_dict['RCLONE_CONFIG_URL']).startswith('http'):
    LOGGER.info(f"Downloading Rclone Config File: {config_dict['RCLONE_CONFIG_URL']}")
    dw_file_from_url(config_dict['RCLONE_CONFIG_URL'], 'rclone.conf')

if not exists('rclone.conf'):
    LOGGER.warning("Rclone Config File Not Found")

bot = Client(
    "Nik66Bot",
    api_id=config_dict['Telegram_API_ID'],
    api_hash=config_dict['Telegram_API_HASH'],
    bot_token=config_dict['Telegram_BOT_TOKEN'],
    max_concurrent_transmissions=10)
