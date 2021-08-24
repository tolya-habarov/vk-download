import re
import os
import sys
import time
import requests
import logging

import vk_api
from vk_api.audio import VkAudio


logger = logging.getLogger(__name__)

LOGIN = ''
PASSWORD = ''
MUSIC_DIR = 'music'
FORBIDDEN_CHARS = r'@$%&\/:*?"\'<>|~`\#\^+={}\[\];!'

def config_logger():
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('.log')
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.ERROR)

    log_format = '%(asctime)s|%(name)s|%(levelname)s|%(message)s'
    console_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setFormatter(logging.Formatter(log_format))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

def vk_auth(login, password):
    def auth_handler():
        key = input('Enter authentication code: ')
        return key, False

    def captcha_handler(captcha):
        key = input(f'Enter captcha code: {captcha.get_url()} ').strip()
        return captcha.try_again(key)

    session = vk_api.VkApi(
        login,
        password,
        auth_handler=auth_handler,
        captcha_handler=captcha_handler,
    )

    try:
        session.auth()
    except vk_api.AuthError:
        logger.exception('Fail auth.')
        raise

    logger.info('Authentication successful')
    return session

def write_audio(request, file_name):
    try:
        if not os.path.exists(MUSIC_DIR):
            os.makedirs(MUSIC_DIR)

        file_path = os.path.join(MUSIC_DIR, f'{file_name}.mp3')
        with open(file_path, 'wb') as f:
            f.write(request.content)
    except OSError:
        logger.exception(f'Fail audio store to file: {file_name}')

def download_audio(url, artist, title):
    try:
        file_name = re.sub(FORBIDDEN_CHARS, '', f'{artist}-{title}')

        r = requests.get(url)
        assert r.status_code == 200

        write_audio(r, file_name)
    except (requests.RequestException, AssertionError):
        logger.exception(f'Fail audio download: {file_name}')
    else:
        logger.info(f'Success download: {file_name}')

def main():
    try:
        session = vk_auth(LOGIN, PASSWORD)

        vk_audio = VkAudio(session)
        for i in vk_audio.get_iter():
            download_audio(i['url'], i['artist'], i['title'])
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        logger.exception('Something went wrong')

if __name__ == '__main__':
    config_logger()
    main()