__author__ = ['Volkov Aleksey']
__version__ = '1.0.0'

import os
import sys
import csv
import asyncio
import configparser
from typing import List
from itertools import chain

import bs4.element
from telegram import Bot
from bs4 import BeautifulSoup
from cloudscraper import create_scraper

PATH_TO_INI_FILE = 'config.ini'

if len(sys.argv) == 2:
    PATH_TO_INI_FILE = sys.argv[1]
if len(sys.argv) > 2:
    print('Передано слишком много агрументов')
    sys.exit(3)

config = configparser.ConfigParser()
config.read(PATH_TO_INI_FILE)

try:
    URL = config.get('FAB', 'url')
except configparser.NoSectionError:
    if not os.path.exists(PATH_TO_INI_FILE):
        print(f'Не найден путь до конфигурационного файла {PATH_TO_INI_FILE}')
        sys.exit(1)
    else:
        print(f'Не найдена секция FAB в конфиг файле {PATH_TO_INI_FILE}')
        sys.exit(2)

URL = config.get('FAB', 'url')
URL_FREE_ASSETS = config.get('FAB', 'url_free_assets')
TG_TOKEN = config.get('TELEGRAM', 'token')
TG_CHANT_ID = config.get('TELEGRAM', 'chat_id')
HEADERS = {'Referer': URL, 'Accept-Language': 'ru-RU,ru;q=0.9'}
BROWSER = {'browser': 'chrome', 'platform': 'windows', 'mobile': False}
INTERPRETER = 'nodejs'
CSV_FILE_NAME = config.get('CSV', 'file')


async def tg_send_message(tg_bot: Bot, send_data: List[str]):
    """Отправка сообщений в канал телеграма

    Args:
        tg_bot: Авторизированый бот телеграма
        send_data: Список сообщений для отправки
    """
    for message in send_data:
        await tg_bot.send_message(chat_id=TG_CHANT_ID, text=message)
        await asyncio.sleep(1)


class Assets:
    """Ресурс"""
    __first_div: List[bs4.element.Tag] = None

    def __init__(self, assets_info: bs4.element.Tag) -> None:
        """Инициализация

        Args:
            assets_info: Информация ресурса с HTML странички.
        """
        self.assets_info = assets_info

    @property
    def first_div(self) -> List[bs4.element.Tag]:
        """Первичный DIV блок. Хранит в себе информацию об имени и
        изображения ресурса"""
        if not self.__first_div:
            self.__first_div = self.assets_info.find_all('div')
        return self.__first_div

    @property
    def name(self) -> str:
        """Получение имени ресурса

        Returns:
            Имя ресурса
        """
        return self.first_div[0].find('div').find('div').find('a').find('div').text

    @property
    def images(self) -> bs4.element.Tag:
        """Получение изображения ресурса

        Returns:
            Изображение ресурса
        """
        return self.first_div[1]


def main():
    scraper = create_scraper(browser=BROWSER, interpreter=INTERPRETER)
    response = scraper.get(url=URL_FREE_ASSETS, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        with open(CSV_FILE_NAME, 'r', newline='', encoding='utf-8') as csv_file:
            save_assets = list(csv.reader(csv_file))
            chain_assets = tuple(chain(*save_assets))
    except FileNotFoundError:
        open(CSV_FILE_NAME, 'w').close()
        save_assets = chain_assets = []

    send_data = []
    for element in soup.find_all('div', class_='fabkit-Stack-root nTa5u2sc'):
        assets = Assets(element)
        if not assets.name in chain_assets:
            send_data.append(assets.name)
            save_assets.append([assets.name])

    if send_data:
        bot = Bot(token=TG_TOKEN)
        asyncio.run(tg_send_message(bot, send_data))

        with open(CSV_FILE_NAME, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(save_assets)

    else:
        print('Изменений нет')


if __name__ == '__main__':
    main()
