# coding: utf-8

import requests
import datetime
import time
from mailer import get_html, send_email 

def get_states_portal():
    """Функция возвращает сформированные позиции"""
    
    print("Получаем закупки с сайта portal")
    
    states = []
    positions = []
    
    urls = [
        'https://old.zakupki.mos.ru/api/Cssp/Purchase/Query?queryDto=%7B%22filter%22%3A%7B%22regionPaths%22%3A%5B%22.4422.%22%5D%2C%22auctionSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B19000002%5D%7D%2C%22needSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B20000002%5D%7D%2C%22tenderSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B5%5D%7D%7D%2C%22order%22%3A%5B%7B%22field%22%3A%22relevance%22%2C%22desc%22%3Atrue%7D%5D%2C%22withCount%22%3Atrue%2C%22take%22%3A100%2C%22skip%22%3A0%7D',
        'https://old.zakupki.mos.ru/api/Cssp/Purchase/Query?queryDto=%7B%22filter%22%3A%7B%22regionPaths%22%3A%5B%22.192.%22%5D%2C%22auctionSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B19000002%5D%7D%2C%22needSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B20000002%5D%7D%2C%22tenderSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B5%5D%7D%7D%2C%22order%22%3A%5B%7B%22field%22%3A%22relevance%22%2C%22desc%22%3Atrue%7D%5D%2C%22withCount%22%3Atrue%2C%22take%22%3A100%2C%22skip%22%3A0%7D',
        'https://old.zakupki.mos.ru/api/Cssp/Purchase/Query?queryDto=%7B%22filter%22%3A%7B%22regionPaths%22%3A%5B%22.56969.%22%5D%2C%22auctionSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B19000002%5D%7D%2C%22needSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B20000002%5D%7D%2C%22tenderSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B5%5D%7D%7D%2C%22order%22%3A%5B%7B%22field%22%3A%22relevance%22%2C%22desc%22%3Atrue%7D%5D%2C%22withCount%22%3Atrue%2C%22take%22%3A100%2C%22skip%22%3A0%7D'
    ]
    
    for url in urls:
        r = requests.get(url)
        items = r.json()['items']
        
        for item in items:
            if item['needId'] is not None:
                need_bool = True
                url_pattern = 'https://old.zakupki.mos.ru/#/need/{0}'
            else:
                need_bool = False
                url_pattern = 'https://zakupki.mos.ru/auction/{0}'
            
            start_price = 0.0
            if item['startPrice'] is not None:
                start_price = float(item['startPrice'])
            
            state = {
                'unique_id': str(item['number']) + '_portal', 
                'place': 'portal',
                'id_zak': int(item['number']),
                'name_group_pos': item['name'],
                'organization': item['customers'][0]['name'],
                'start_time': datetime.datetime.strptime(item['beginDate'], '%d.%m.%Y %H:%M:%S') + datetime.timedelta(2/24),
                'end_time': datetime.datetime.strptime(item['endDate'], '%d.%m.%Y %H:%M:%S') + datetime.timedelta(2/24),
                'created_time': datetime.datetime.strptime(item['beginDate'], '%d.%m.%Y %H:%M:%S') + datetime.timedelta(2/24),
                'current_status': item['stateName'],
                'start_price': start_price,
                'address': None,
                'url': url_pattern.format(item['number']),
                'send': False,
                'add_trello': False,
            }
            if state not in states:
                states.append(state)
                if need_bool:
                    r = requests.get('https://old.zakupki.mos.ru/api/Cssp/Need/GetEntity?id={0}'.format(item['number']))
                    if r.status_code == 200:
                        positions += [{
                            'unique_id': str(item['number']) + '_portal',
                            'name': x['name'], 
                            'amount': x['amount'], 
                            'price': x['cost']
                        } for x in r.json()['items']] 
                else:
                    r = requests.get('https://old.zakupki.mos.ru/api/Cssp/OfferAuction/GetEntity?id={0}'.format(item['number']))
                    if r.status_code == 200:
                        positions += [{
                            'unique_id': str(item['number']) + '_portal',
                            'name': x['offerAuctionItem'].get('offerSkuName'), 
                            'amount': int(x['currentValue']), 
                            'price': x['costPerUnit']
                        } if x['offerAuctionItem'] is not None else {
                            'unique_id': str(item['number']) + '_portal',
                            'name': 'Без названия', 
                            'amount': int(x['currentValue']), 
                            'price': x['costPerUnit']
                        } for x in r.json()['items']] 
                        
    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])
    
    return new_states, positions

if __name__ == '__main__':
    data = get_states_portal()
    message = get_html(data, template_file='template_portal.html')
    header = 'Новые закупки Портал Поставщиков'
    send_email(message, "SyrnikovPavel@gmail.com", "SyrnikovPavel@gmail.com", "Nastya26042015", header=header)
    send_email(message, "sursmirnav78@mail.ru", "SyrnikovPavel@gmail.com", "Nastya26042015", header=header)

