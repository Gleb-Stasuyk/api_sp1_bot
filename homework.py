import logging
import os
import requests
import time

from dotenv import load_dotenv
import telegram

logging.basicConfig(filename="Log.log", level=logging.ERROR,
                    format=u'%(filename)s[LINE:%(lineno)d]# '
                           u'%(levelname)-8s [%(asctime)s]  %(message)s')
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
        verdict = 'Ревьюеру всё понравилось, ' + \
                  'можно приступать к следующему уроку.'
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
            raise RuntimeError("Homework status contains error: "
                               + homework_statuses['error']['error'])
        if homework_statuses.get('code') == 'not_authenticated':
            raise RuntimeError('Authorisation Error')
        if 'homeworks' not in homework_statuses:
            raise RuntimeError('Unexpected error while homework ststus get')
        return homework_statuses
    except (requests.exceptions.RequestException, ValueError) as e:
        raise RuntimeError(f'Get homework status failed with error:{e}')


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
                    new_homework['homeworks'][0]))
            current_timestamp = new_homework.get('current_date',
                                                 int(time.time()))
            time.sleep(1200)

        except Exception as e:
            logger.error(f'Unsuccessful bot launching with error: {e}')
            time.sleep(50)


if __name__ == '__main__':
    main()
