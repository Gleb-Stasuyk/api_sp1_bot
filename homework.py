import os
import requests
import telegram
import time
import logging

from dotenv import load_dotenv

logging.basicConfig(filename="log.txt", level=logging.INFO)
load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    date = {'from_date': 'current_timestamp'}
    try:
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            headers=headers,
            params=date).json()
        if homework_statuses.get('error'):
            logging.error("An error has happened! Error name: ",
                          homework_statuses['error']['error'])
            raise SystemExit()
        return homework_statuses
    except (requests.exceptions.RequestException, ValueError) as e:
        # Нужно выяснить какого типа исключения он бросает. - типа.RequestException?
        # зачем в прошлом ДЗ ловили ValueError я так и не понял
        # logger почему-то не сохраняет текст ошибк в файле
        logging.error(f"An error has happened! Error name: {e}")
        raise SystemExit()


def send_message(message):
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    send_message('Бот начал свою работу')
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
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(50)
            continue


if __name__ == '__main__':
    main()
