# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
import time
import datetime
import json
import traceback

from tables import *

def merge_two_dicts(x, y):
    """
    Функция для объединения двух словарей
    """
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def prepare_date(date_str: str):
    """
    Функция для обработки даты.
    Принимает на вход строку (но может и объект datetime.datetime)
    И преобразовывает его в datetime.datetime
    """

    months = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05',
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12',
    }

    if type(date_str) == datetime.datetime:
        # если объект == datetime.datetime
        return date_str

    else:
        # иначе
        # Проверка на соответствие типу
        assert type(date_str) == str, "Object must be str"
        # Удаление из строки лишних символов
        date_str = date_str.replace('г.', ' ').replace('МСК', '').replace('  ', '').replace('\n', '')
        # Если присутствуют месяцы не в цифровом виде, то замена из на цифры
        for month, value in months.items():
            date_str = date_str.replace(month, value)

        # если в конце строки пустота
        if date_str[-1:] == ' ':
            # удаляем его
            date_str = date_str[:-1]

        # Если строка пустая
        if date_str == '':
            # возвращаем None
            return None
        else:
            # Иначе
            # преобразовываем в объект datetime.datetime
            try:
                date_str = datetime.datetime.strptime(date_str, '%d %m %Y %H:%M')
                return date_str
            except ValueError as err:
                # если не выходит преобразовать, то шаблон не соответвует строке
                print("Time data '{0}' does not match format '%d %m %Y %H:%M'".format(date_str))
                return None


def get_main_info(soup: BeautifulSoup):
    """
    Функция принимает на вход распарсенную страницу.
    На выходе выдает основую информацию в формате dict.
    """

    main_table = soup.find_all("table")[0]
    info = {}
    for tr in main_table.find_all('tr'):
        key = tr.find_all('td')[0].getText().replace(' ', '')
        value = tr.find_all('td')[1].getText().replace("\xa0", "").replace(",", ".").replace(
            '\r', '').replace('\n', '').replace('  ', '').replace('(Все закупки организации)', '').replace(' руб.', '')
        if value is not None and value != "":
            if value[0] == " ":
                value = value[1:]
            info.update({key: value})

    info = {
        "name_group_pos": info['НаименованиеЗакупки'],
        "organization": info['Заказчик'],
        "start_price": float(info['Суммаконтракта']),
    }

    return info


def get_date_info(soup: BeautifulSoup):
    """
    Функция принимает на вход распарсенную страницу.
    На выходе выдает информацию по датам в формате dict.
    """
    date_table = soup.find_all("table")[1]
    info = {}
    for tr in date_table.find_all('tr'):
        key = tr.find_all('td')[0].getText().replace(' ', '')
        value = tr.find_all('td')[1].getText().replace("\xa0", "").replace(",", ".").replace(
            '\r', '').replace('\n', '').replace('  ', '').replace('(Все закупки организации)', '').replace(' руб.', '')
        
        if value != "":
            if value[0] == " ":
                value = value[1:]
            if value[-1] == " ":
                value = value[:-1]
        info.update({key: value})
        key = tr.find_all('td')[2].getText().replace(' ', '')
        value = tr.find_all('td')[3].getText().replace("\xa0", "").replace(",", ".").replace(
            '\r', '').replace('\n', '').replace('  ', '').replace(' МСК', '')
        if value != "":
            if value[0] == " ":
                value = value[1:]
            if value[-1] == " ":
                value = value[:-1]
        info.update({key: value})

    info = {
        "end_time": prepare_date(info['Срококончанияподачиоферт']) + datetime.timedelta(2/24),
        'start_time': None,
        'created_time': None,
    }
    return info


def get_items(otc_number: int):
    """Функция возвращает данные о товарах в закупке"""
    
    url_pattern = "https://market.otc.ru/ProductRequest/ByGroup?groupId={0}"
    otc_url = url_pattern.format(otc_number)
    r = requests.get(otc_url)
    positions = [{
        'unique_id': str(otc_number) + '_otc',
        'name': x['Name'], 
        'amount': x['Count'], 
        'price': x['Price']
    } for x in r.json()['Data']] 
    return positions

def get_active_tenders():
    """Функция возвращает номера активных тендеров"""
    url_search = 'https://otc.ru/tenders/Search/Lite?SearchForm.HasPrepayment=on&SearchForm.Region=7200000000000%7C6&SearchForm.State=1&SearchForm.DocumentSearchEnabled=true&SearchForm.WithdrawnSearchEnabled=False&SearchForm.HasApplications=on&SearchForm.CurrencyCode=643&SearchForm.SectionIds=91&SearchForm.SectionIds=84&SearchForm.OrganizationLevels=All&SearchForm.OrganizationLevels=Fz223&SearchForm.OrganizationLevels=Fz44&SearchForm.OrganizationLevels=Pprf615&SearchForm.OrganizationLevels=Small&SearchForm.OrganizationLevels=Commercial&SearchForm.IsSmallAndAverageBusiness=on&FilterData.SortingField=DatePublished&FilterData.SortingDirection=Desc&FilterData.PageSize=500&FilterData.PageIndex=1&'
    r = requests.get(url_search)
    soup = BeautifulSoup(r.content, 'lxml')
    tender_numbers = list(set([int(re.search('/\d+-', x.get('href')).group(0).replace('/','').replace('-','')) for x in soup.find_all('a', {'class': 'panel_name'})]))
    real_count = int(re.search('\d+', soup.find('div', {'class': 'row search-form-result-counter'}).getText()).group(0))
    assert len(tender_numbers) == real_count, 'Количество тендеров в поиске не совпадает с результатом'
    return tender_numbers

def get_one_state(otc_number: int):
    'Функция возвращает данные по одной закупке'
    url_pattern = "https://market.otc.ru/ProductRequestGroup/Index/{0}"
    otc_url = url_pattern.format(otc_number)
    r = requests.get(otc_url)
    soup = BeautifulSoup(r.content, 'lxml')
    main_info = get_main_info(soup)  # получение основных данных о закупке
    date_info = get_date_info(soup)  # получение информации о датах закупки
    state = merge_two_dicts(main_info, date_info)  # объединение двух словарей
    state.update({
        'unique_id': str(otc_number) + '_otc',
        'place': 'otc',
        'current_status': 'Активная',
        'address': None,
        'id_zak': otc_number,
        'url': otc_url,
        'send': False,
        'add_trello': False,
    })
    position = get_items(otc_number)
    return state, position

def get_states_otc():
    tender_numbers = get_active_tenders()
    tender_number_not_in_base = []
    for tender_number in tender_numbers:
        if State.get_or_none(State.unique_id==str(tender_number)+'_otc') is None:
            tender_number_not_in_base.append(tender_number)
    states = []
    positions = []
    for otc_number in tender_number_not_in_base:
        state, position = get_one_state(otc_number)
        states += [state]
        positions += position
    return states, positions

if __name__ == '__main__':
    data = get_states_otc()
    message = get_html(data)
    send_email(message, "SyrnikovPavel@gmail.com", "SyrnikovPavel@gmail.com", "Nastya26042015")
    send_email(message, "sursmirnav78@mail.ru", "SyrnikovPavel@gmail.com", "Nastya26042015")