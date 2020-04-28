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
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    end_time = datetime.datetime.now() + datetime.timedelta(2/24)
    
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    for table in soup.find_all('div', {'class': 'noticeTabBoxWrapper'}):
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds)>=2:
                key = tds[0].getText()
                value = tds[1].getText()
                if 'Дата и время окончания подачи заявок' in key:
                    if value != '':
                        try:
                            if value.find(' (МСК')>=0:
                                end_time = datetime.datetime.strptime(value[:value.find(' (МСК')], '%d.%m.%Y в %H:%M')
                            else:
                                end_time = datetime.datetime.strptime(value, '%d.%m.%Y %H:%M')
                        except ValueError:
                            print(value)
                            break
    
    return end_time

def get_states_from_url(url, ids, states):
    """Функция возвращает закупки с сайта zakupki.gov по заданному url"""
    
    try:
        d = feedparser.parse(url)

        for entry in d['entries']:
            if re.search('\d+', entry['title']).group(0) not in ids:
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
                                try:
                                    state.update({'start_price': float(value)})
                                except ValueError:
                                    state.update({'start_price': float(0)})
                            elif replaced_dict.get(key) == 'start_time':
                                state.update({'start_time':datetime.datetime.strptime(value, '%d.%m.%Y')})
                            elif replaced_dict.get(key) == 'created_time':
                                state.update({'created_time':datetime.datetime.strptime(value, '%d.%m.%Y')})
                            else:
                                state.update({replaced_dict.get(key): value})
                ids.append(re.search('\d+', entry['title']).group(0))
                if state not in states:
                    states.append(state)
    except requests.exceptions.ConnectionError as e:
        print(e)
    
    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])
    return ids, new_states


def get_states_zakupki():
    """Функция возвращает закупки с сайта zakupki.gov"""
    
    print("Получаем закупки с сайта zakupki.gov")
    
    states = []
    ids = []
    
    urls = {
        'Местоположение поставки: Тюмень': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277379&delKladrIdsCodes=72000000000&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение поставки: Курган': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277378&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение поставки: Челябинск': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277380&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение поставки: Екатеринбург': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277383&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение поставки: ХМАО': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277381&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение поставки: ЯНАО': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277382&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение заказчика: Курган': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3%2C01.29%2C18.12%2C26.60%2C32.50%2C02.40.10%2C38.11.29%2C38.11.52%2C82.99.19%2C91.01.12%2C13.93.19.120%2C17.22.11.130%2C18.13.30.000%2C22.11.11.000%2C25.62.20.000%2C25.99.29.190%2C43.11.10.000%2C43.29.12.110%2C43.29.19.140%2C43.99.70.000%2C43.99.90.190%2C45.20.23.000%2C81.22.12.000%2C95.29.14.119%2C96.01.12.129&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&customerPlace=5277378&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение заказчика: Челябинск': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3%2C01.29%2C18.12%2C26.60%2C32.50%2C02.40.10%2C38.11.29%2C38.11.52%2C82.99.19%2C91.01.12%2C13.93.19.120%2C17.22.11.130%2C18.13.30.000%2C22.11.11.000%2C25.62.20.000%2C25.99.29.190%2C43.11.10.000%2C43.29.12.110%2C43.29.19.140%2C43.99.70.000%2C43.99.90.190%2C45.20.23.000%2C81.22.12.000%2C95.29.14.119%2C96.01.12.129&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&customerPlace=5277380&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение заказчика: Екатеринбург': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3%2C01.29%2C18.12%2C26.60%2C32.50%2C02.40.10%2C38.11.29%2C38.11.52%2C82.99.19%2C91.01.12%2C13.93.19.120%2C17.22.11.130%2C18.13.30.000%2C22.11.11.000%2C25.62.20.000%2C25.99.29.190%2C43.11.10.000%2C43.29.12.110%2C43.29.19.140%2C43.99.70.000%2C43.99.90.190%2C45.20.23.000%2C81.22.12.000%2C95.29.14.119%2C96.01.12.129&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&customerPlace=5277383&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение заказчика: ХМАО': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3%2C01.29%2C18.12%2C26.60%2C32.50%2C02.40.10%2C38.11.29%2C38.11.52%2C82.99.19%2C91.01.12%2C13.93.19.120%2C17.22.11.130%2C18.13.30.000%2C22.11.11.000%2C25.62.20.000%2C25.99.29.190%2C43.11.10.000%2C43.29.12.110%2C43.29.19.140%2C43.99.70.000%2C43.99.90.190%2C45.20.23.000%2C81.22.12.000%2C95.29.14.119%2C96.01.12.129&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&customerPlace=5277381&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение заказчика: ЯНАО': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3%2C01.29%2C18.12%2C26.60%2C32.50%2C02.40.10%2C38.11.29%2C38.11.52%2C82.99.19%2C91.01.12%2C13.93.19.120%2C17.22.11.130%2C18.13.30.000%2C22.11.11.000%2C25.62.20.000%2C25.99.29.190%2C43.11.10.000%2C43.29.12.110%2C43.29.19.140%2C43.99.70.000%2C43.99.90.190%2C45.20.23.000%2C81.22.12.000%2C95.29.14.119%2C96.01.12.129&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&customerPlace=5277382&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Местоположение заказчика: Тюмень': 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3%2C01.29%2C18.12%2C26.60%2C32.50%2C02.40.10%2C38.11.29%2C38.11.52%2C82.99.19%2C91.01.12%2C13.93.19.120%2C17.22.11.130%2C18.13.30.000%2C22.11.11.000%2C25.62.20.000%2C25.99.29.190%2C43.11.10.000%2C43.29.12.110%2C43.29.19.140%2C43.99.70.000%2C43.99.90.190%2C45.20.23.000%2C81.22.12.000%2C95.29.14.119%2C96.01.12.129&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&customerPlace=5277379&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'Управление закупок Тюменской области': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&customerTitle=%D0%A3%D0%9F%D0%A0%D0%90%D0%92%D0%9B%D0%95%D0%9D%D0%98%D0%95+%D0%93%D0%9E%D0%A1%D0%A3%D0%94%D0%90%D0%A0%D0%A1%D0%A2%D0%92%D0%95%D0%9D%D0%9D%D0%AB%D0%A5+%D0%97%D0%90%D0%9A%D0%A3%D0%9F%D0%9E%D0%9A+%D0%A2%D0%AE%D0%9C%D0%95%D0%9D%D0%A1%D0%9A%D0%9E%D0%99+%D0%9E%D0%91%D0%9B%D0%90%D0%A1%D0%A2%D0%98&customerCode=01672000034&customerFz94id=629156&customerFz223id=187102&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        'ИНН: Управа ЦАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?searchString=&morphology=on&search-filter=&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&okpd2Ids=&okpd2IdsCodes=&af=on&placingWaysList=&placingWaysList223=&placingChildWaysList=&publishDateFrom=+&publishDateTo=&applSubmissionCloseDateFrom=+&applSubmissionCloseDateTo=&priceFromGeneral=%D0%9C%D0%B8%D0%BD%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F+%D1%86%D0%B5%D0%BD%D0%B0&priceFromGWS=%D0%9C%D0%B8%D0%BD%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F+%D1%86%D0%B5%D0%BD%D0%B0&priceFromUnitGWS=%D0%9C%D0%B8%D0%BD%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F+%D1%86%D0%B5%D0%BD%D0%B0&priceToGeneral=%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F+%D1%86%D0%B5%D0%BD%D0%B0&priceToGWS=%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F+%D1%86%D0%B5%D0%BD%D0%B0&priceToUnitGWS=%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F+%D1%86%D0%B5%D0%BD%D0%B0&currencyIdGeneral=-1&customerCode=01673000021&customerFz94id=774772&customerFz223id=&customerInn=&orderPlacement94_0=&orderPlacement94_1=&orderPlacement94_2=&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&npaHidden=&restrictionsToPurchase44=',
        'ИНН: Управа ВАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&customerCode=01673000013&customerFz94id=638616&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        'ИНН: Управа ЛАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&&customerCode=01673000030&customerFz94id=698477&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        'ИНН: Управа КАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&customerCode=01673000019&customerFz94id=774752&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        'ИНН: Служба заказчика ЦАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&currencyIdGeneral=-1&customerCode=03673000376&customerFz94id=791000&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1',
        'ИНН: Служба заказчика ВАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&customerCode=03673000452&customerFz94id=829217&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        'ИНН: Служба заказчика ЛАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&customerCode=03673000378&customerFz94id=803509&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        'ИНН: Служба заказчика КАО': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&customerCode=03673000394&customerFz94id=808861&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        'ИНН: ЛесПаркХоз': 'https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_500&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=UPDATE_DATE&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&currencyIdGeneral=-1&customerCode=03673000393&customerFz94id=808858&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3',
        
    }
    for name, url in urls.items():
        ids, states = get_states_from_url(url, ids, states)
        print(name)

    
    return states, []

if __name__ == '__main__':
    states = []
    ids = []
    url = 'http://zakupki.gov.ru/epz/order/extendedsearch/rss.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&fz44=on&fz223=on&sortBy=PUBLISH_DATE&okpd2IdsWithNested=on&okpd2Ids=8878464%2C73143%2C8873973%2C8874206%2C8874258%2C8874364%2C8874459%2C8874515%2C8876509%2C8878352%2C8878358%2C8879355%2C8879469%2C8882959%2C8884073%2C8884146%2C8885411%2C8886517%2C8886816%2C8889732%2C8889778%2C8889783%2C8889838%2C8889845%2C8889870%2C8891050%2C9398582%2C9398623&okpd2IdsCodes=43.39.11%2C43.99.90.100%2C01.3%2C81.3&af=on&publishDateFrom=+&applSubmissionCloseDateFrom=+&updateDateFrom=+&currencyIdGeneral=-1&customerPlaceWithNested=on&delKladrIdsWithNested=on&delKladrIds=5277379&delKladrIdsCodes=72000000000&contractStageList_0=on&contractStageList_1=on&contractStageList_2=on&contractStageList_3=on&contractStageList=0%2C1%2C2%2C3&contractPriceCurrencyId=-1'
    get_states_from_url(url, ids, states)


