# coding: utf-8

import requests
import datetime
import time

from mailer import get_html, send_email 

def load_current_zak():
    """Функция выгружает с площадки текущие котировки по Тюменской области"""
    
    url_pattern = 'https://agregatoreat.ru/api/els/purchase/list?page={0}&filter%5BsubjectRF%5D%5B0%5D=%D0%BE%D0%B1%D0%BB%20%D0%A2%D1%8E%D0%BC%D0%B5%D0%BD%D1%81%D0%BA%D0%B0%D1%8F&filter%5BisEat%5D=1&orderTypeCode=103&sort=id%3Adesc&dExcludes=exPurchases&statusPurchases=2'

    items = []
    all_pages = True
    page = 1

    while all_pages:
        try:
            r = requests.get(url_pattern.format(page))
            data = r.json()
            items += data['items']

            if data['start'] + data['perPage'] >= data['total']:
                all_pages = False

            page += 1
            time.sleep(1)
        except:
            time.sleep(2)
            data = r.json()
            items += data['items']

            if data['start'] + data['perPage'] >= data['total']:
                all_pages = False

            page += 1
            time.sleep(1)
            
    assert len(items) == data['total'], 'Количество элементов в выгрузке не равно декларируемому'
    
    return items

def form_positions(items):
    """Функция формирует позиции в верном формате"""
    states = []
    positions = []
    for item in items:
        if item['delivery']['address'].get('full') is not None:
            address = item['delivery']['address']['full']
        else:
            address = item['customer']['organization']['eat_addresses'][0]['address_str']
        state = {
            'unique_id': str(item['id']) + '_berezka',
            'place': 'berezka',
            'id_zak': item['id'],
            'name_group_pos': item['condition']['nameTRY'],
            'organization': item['condition']['organizationFullName'],
            'start_time': datetime.datetime.strptime(item['orderStart'], '%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.datetime.strptime(item['orderStart'], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(7/24),
            'created_time': datetime.datetime.strptime(item['created_at'], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(3),
            'current_status': item['status'],
            'start_price': float(item['condition']['startfinalprice']),
            'address': address,
            'url': "https://agregatoreat.ru/purchase/{0}/order-info#specification".format(item['id']),
            'send': False,
            'add_trello': False,
        }
        if state not in states:
            states.append(state)
            positions += [{'unique_id': str(item['id']) + '_berezka','name': x['label']['<all_channels>']['<all_locales>'], 'amount': x['qty'], 'price': None} if x['label'] != [] else {'unique_id': str(item['id']) + '_berezka','name': x['family']['labels']['ru_RU'], 'amount': x['qty'], 'price': None} for x in item['products']]
    
    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])
    return new_states, positions

def get_states_ber():
    """Функция возвращает сформированные позиции"""
    
    print("Получаем закупки с сайта berezka")
    
    items = load_current_zak()
    return form_positions(items)

if __name__ == '__main__':
    data = get_positions_ber()
    message = get_html(data)
    send_email(message, "SyrnikovPavel@gmail.com", "SyrnikovPavel@gmail.com", "Nastya26042015")
    send_email(message, "sursmirnav78@mail.ru", "SyrnikovPavel@gmail.com", "Nastya26042015")