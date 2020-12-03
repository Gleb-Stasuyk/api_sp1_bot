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
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(
            url,
            headers=headers,
            params=date
        ).json()
        if homework_statuses.get('error'):
            error = (f'Homework status contains error: '
                     f'{homework_statuses["error"]["error"]} '
                     f'\non {url}, with params: {date}')
            raise RuntimeError(error)
        if homework_statuses.get('code') == 'not_authenticated':
            error = (f'Authorisation Error. not_authenticated '
                     f'\non {url}, with params: {date}')
            raise RuntimeError(error)
        return homework_statuses
    except (requests.exceptions.RequestException, ValueError) as e:
        error = (f'Request homework status failed with error:{e}. '
                 f'\non {url}, with params: {date}')
        raise RuntimeError(error)


def send_message(message):
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    send_message('Bot launch')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(1200)

        except Exception as e:
            exc_traceback = sys.exc_info()[2]
            logger.error(f'Problem: {e}, tb_lineno: {exc_traceback.tb_lineno}')
            time.sleep(5)


if __name__ == '__main__':
    path_to_logger = sys.argv[0]
    path_to_logger_dir = os.path.dirname(os.path.abspath(path_to_logger))
    logging.basicConfig(filename=sys.argv[0] + '.log', level=logging.ERROR,
                        format=u'%(filename)s[LINE:%(lineno)d]# '
                               u'%(levelname)-8s [%(asctime)s]  %(message)s\n')
    main()
