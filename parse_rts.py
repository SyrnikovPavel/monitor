# coding: utf-8

import requests
import time
import datetime

def get_states_rts():
    "Функция возвращает закупки с rts-маркета"
    
    print("Получаем закупки с сайта rts")

    states = []
    positions = []

    url = "https://zmo-new-webapi.rts-tender.ru/market/api/v1/trades/publicsearch2"

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Length': '544',
        'Content-Type': 'application/json',
        'CurrentUrl': 'https://market.rts-tender.ru/search/sell?s=1&regs=4500000000000&regs=5500000000000&regs=6600000000000&regs=7200000000000&regs=8600000000000&regs=8900000000000&regs=7400000000000&okpd2s=43.39.11&okpd2s=43.99.90.100&okpd2s=01.3&okpd2s=81.3&okpd2s=01.29&okpd2s=18.12&okpd2s=26.60&okpd2s=32.50&okpd2s=02.40.10&okpd2s=14.12.30&okpd2s=38.11.29&okpd2s=38.11.52&okpd2s=82.99.19&okpd2s=91.01.12&okpd2s=13.93.19.120&okpd2s=17.22.11.130&okpd2s=18.13.30.000&okpd2s=22.11.11.000&okpd2s=25.62.20.000&okpd2s=25.99.29.190&okpd2s=43.11.10.000&okpd2s=43.29.12.110&okpd2s=43.29.19.140&okpd2s=43.99.70.000&okpd2s=43.99.90.190&okpd2s=45.20.23.000&okpd2s=81.22.12.000&okpd2s=95.29.14.119&okpd2s=96.01.12.129&smp=0&sts=0&sort=-PublicationDate',
        'GoogleClientId': '1141161001.1574398235',
        'Host': 'zmo-new-webapi.rts-tender.ru',
        'Origin': 'https://market.rts-tender.ru',
        'Referer': 'https://market.rts-tender.ru/search/sell?s=1&regs=4500000000000&regs=5500000000000&regs=6600000000000&regs=7200000000000&regs=8600000000000&regs=8900000000000&regs=7400000000000&okpd2s=43.39.11&okpd2s=43.99.90.100&okpd2s=01.3&okpd2s=81.3&okpd2s=01.29&okpd2s=18.12&okpd2s=26.60&okpd2s=32.50&okpd2s=02.40.10&okpd2s=14.12.30&okpd2s=38.11.29&okpd2s=38.11.52&okpd2s=82.99.19&okpd2s=91.01.12&okpd2s=13.93.19.120&okpd2s=17.22.11.130&okpd2s=18.13.30.000&okpd2s=22.11.11.000&okpd2s=25.62.20.000&okpd2s=25.99.29.190&okpd2s=43.11.10.000&okpd2s=43.29.12.110&okpd2s=43.29.19.140&okpd2s=43.99.70.000&okpd2s=43.99.90.190&okpd2s=45.20.23.000&okpd2s=81.22.12.000&okpd2s=95.29.14.119&okpd2s=96.01.12.129&smp=0&sts=0&sort=-PublicationDate',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'UserGuid': '0bfa0502-a79e-4bb1-9ab8-340843ec5aea',
        'XXX-TenantId-Header': '132',
    }

    json_item = {
        "FilterSource": 1,
        "Paging": {
            "Page": 1,
            "ItemsPerPage": 500
        },
        "PaginationEventType": 0,
        "Sorting": [{
            "field": "PublicationDate",
            "title": "По новизне",
            "direction": "Descending",
            "active": True
        }],
        "Filtering": [{
            "Title": "Регионы поставки",
            "ShortName": "regs",
            "Type": 0,
            "Value": [
                "4500000000000", "5500000000000", "6600000000000", "7200000000000", "8600000000000", "8900000000000",
                "7400000000000"
            ],
            "Name": "KladrCodeRegions"
        }, {
            "Title": "Тип поиска",
            "ShortName": "t",
            "Type": 1,
            "Value": 1,
            "Name": "MarketSearchAction"
        }, {
            "Title": "Окпд2 коды",
            "ShortName": "okpd2s",
            "Type": 0,
            "Value": [
                "43.39.11", "43.99.90.100", "01.3", "81.3", "01.29", "18.12", "26.60", "32.50", "02.40.10", "14.12.30",
                "38.11.29", "38.11.52", "82.99.19", "91.01.12", "13.93.19.120", "17.22.11.130", "18.13.30.000",
                "22.11.11.000", "25.62.20.000", "25.99.29.190", "43.11.10.000", "43.29.12.110", "43.29.19.140",
                "43.99.70.000", "43.99.90.190", "45.20.23.000", "81.22.12.000", "95.29.14.119", "96.01.12.129"
            ],
            "Name": "Okpd2Codes"
        }, {
            "Title": "Признак малого и среднего предпринимательства",
            "ShortName": "smp",
            "Type": 1,
            "Value": 0,
            "Name": "SmpFilterState"
        }, {
            "Title": "Статус",
            "ShortName": "sts",
            "Type": 1,
            "Value": [0],
            "Name": "Statuses"
        }]}

    r = requests.post(url=url, headers=headers, json=json_item)

    for item_data in r.json()['data']['items']:
        try:
            pub_date = datetime.datetime.strptime(item_data.get('PublicationDate'),
                                                  '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(5 / 24)
            end_date = datetime.datetime.strptime(item_data.get('FillingApplicationEndDate'),
                                                  '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(5 / 24)
        except ValueError:
            try:
                pub_date = datetime.datetime.strptime(item_data.get('PublicationDate'),
                                                      '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(5 / 24)
                end_date = datetime.datetime.strptime(item_data.get('FillingApplicationEndDate'),
                                                      '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(5 / 24)
            except ValueError:
                pub_date = datetime.datetime.now()
                end_date = datetime.datetime.now()
        # print(item_data.get('PublicationDate'))
        state = {
            'unique_id': str(item_data.get('Id')) + '_rts',
            'place': 'rts',
            'id_zak': str(item_data.get('Id')),
            'name_group_pos': item_data.get('Name'),
            'organization': item_data.get('CustomerName'),
            'start_time': pub_date,
            'end_time': end_date,
            'created_time': pub_date,
            'current_status': item_data.get('StateString'),
            'start_price': item_data.get('Price'),
            'address': item_data.get('DeliveryKladrRegionName'),
            'url': 'https://zmo.rts-tender.ru/Trade/ViewTrade?id=' + str(item_data.get('Id')),
            'send': False,
            'add_trello': False,
        }
        if state not in states:
            states.append(state)
            headers2 = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/json',
                'currenturl': 'https://market.rts-tender.ru/search/sell/{0}/request'.format(item_data.get('Id')),
                'googleclientid': '1542855268.1582003209',
                'origin': 'https://market.rts-tender.ru',
                'referer': 'https://market.rts-tender.ru/search/sell/{0}/request'.format(item_data.get('Id')),
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
                'userguid': '434bbe57-1c21-4ab2-bd86-a8076aa911e6',
                'xxx-tenantid-header': '132',
            }
            r = requests.get(
                'https://zmo-new-webapi.rts-tender.ru/market/api/v1/trades/{0}'.format(item_data.get('Id')),
                headers=headers2)
            if r.status_code == 200:
                positions += [{
                    'unique_id': str(item_data.get('Id')) + '_rts',
                    'name': x['Name'],
                    'amount': int(x['Quantity']) if x['Quantity'] is not None else None,
                    'price': float(x['Price']) if x['Price'] is not None else None
                } for x in r.json()['data']['Products']]
                time.sleep(1)

    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])
    return new_states, positions
