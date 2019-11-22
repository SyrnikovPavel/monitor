# coding: utf-8

import feedparser
import requests
from bs4 import BeautifulSoup
import datetime
import re

def get_endtime(url):
    """Функция возвращает дату окончания подачи заявок"""
    end_time = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    for table in soup.find_all('div', {'class': 'noticeTabBoxWrapper'}):
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds)>=2:
                key = tds[0].getText()
                value = tds[1].getText()
                if 'Дата и время окончания подачи заявок' in key:
                    if value.find(' (МСК')>=0:
                        end_time = datetime.datetime.strptime(value[:value.find(' (МСК')], '%d.%m.%Y в %H:%M')
                    else:
                        end_time = datetime.datetime.strptime(value, '%d.%m.%Y %H:%M')
                    break
    
    return end_time

def get_states_zakupki():
    """Функция возвращает закупки с сайта zakupki.gov"""
    
    url = 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8885411%2C8873973%2C8874206%2C8874364%2C8874515%2C8884073%2C9398623&okpd2IdsCodes=22.11.11.000%2C01.3%2C81.3%2C18.12&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277379&delKladrIdsCodes=72000000000&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1'
    d = feedparser.parse(url)
    
    states = []

    for entry in d['entries']:

        state = {
            'place': 'zakupki',
            'id_zak': re.search('\d+', entry['title']).group(0),
            'unique_id': str(re.search('\d+', entry['title']).group(0)) + '_zakupki',
            'organization': entry['author'],
            'url': entry['link'],
            'end_time': get_endtime(entry['link']),
            'address': None,
            'send': False,
            'add_trello': False,
        }


        replaced_dict = {
            'Наименование объекта закупки: ': 'name_group_pos',
            'Обновлено: ': 'start_time',
            'Размещено: ': 'created_time',
            'Этап размещения: ': 'current_status',
            'Начальная цена контракта: ': 'start_price',
        }

        for x in entry['summary'].split('<br/>'):
            soup = BeautifulSoup(x, 'lxml')
            strong = soup.find('strong')
            if strong is not None:
                key = strong.getText()
                value = soup.getText().replace(key,'').replace(' Валюта: Российский рубль', '')
                if key in replaced_dict:
                    if replaced_dict.get(key) == 'start_price':
                        state.update({'start_price': float(value)})
                    elif replaced_dict.get(key) == 'start_time':
                        state.update({'start_time':datetime.datetime.strptime(value, '%d.%m.%Y')})
                    elif replaced_dict.get(key) == 'created_time':
                        state.update({'created_time':datetime.datetime.strptime(value, '%d.%m.%Y')})
                    else:
                        state.update({replaced_dict.get(key): value})
        states.append(state)
    
    return states, []
