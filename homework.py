import logging
import os
import requests
import sys
import time

from dotenv import load_dotenv
import telegram

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)
logger = logging.getLogger(__name__)
path_to_logger = sys.argv[0]
path_to_logger_dir = os.path.dirname(os.path.abspath(path_to_logger))
name = 'Log.log'
filename = os.path.join(path_to_logger_dir, name)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    date = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            headers=headers,
            params=date
        ).json()
        if homework_statuses.get('error'):
            error = (f'Homework status contains error: '
                     f'{homework_statuses["error"]["error"]}')
            logger.error(error)
            raise RuntimeError(error)
        if homework_statuses.get('code') == 'not_authenticated':
            error = f'Authorisation Error. not_authenticated'
            logger.error(error)
            raise RuntimeError(error)
        return homework_statuses
    except (requests.exceptions.RequestException, ValueError) as e:
        error = f'Request homework status failed with error:{e}.'
        logger.error(error)
        raise RuntimeError(error)


def send_message(message):
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(1200)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    logging.basicConfig(filename=filename, level=logging.ERROR,
                        format=u'%(filename)s[LINE:%(lineno)d]# '
                               u'%(levelname)-8s [%(asctime)s]  %(message)s')
    main()
