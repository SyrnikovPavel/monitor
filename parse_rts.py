# coding: utf-8

import requests
import time
import datetime

def get_states_rts():
    "Функция возвращает закупки с rts-маркета"
    
    print("Получаем закупки с сайта rts")
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Length': '544',
        'Content-Type': 'application/json',
        'CurrentUrl': 'https://market.rts-tender.ru/search?st=0&t=1&reg=8600000000000&sort=-PublicationDate',
        'GoogleClientId': '1141161001.1574398235',
        'Host': 'zmo-new-webapi.rts-tender.ru',
        'Origin': 'https://market.rts-tender.ru',
        'Referer': 'https://market.rts-tender.ru/search?st=0&t=1&reg=8600000000000&sort=-PublicationDate',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'UserGuid': '0bfa0502-a79e-4bb1-9ab8-340843ec5aea',
        'XXX-TenantId-Header': '132',      
    }


    states = []
    positions = []
    
    jsons_items = [{
        "Filtering":[
            {
                "Title":"Ключевые слова",
                "Name":"KeyWords",
                "ShortName":"q",
                "Type":0,
                "Value":""
            },
            {
                "Title":"Статус",
                "Name":"Status",
                "ShortName":"st",
                "Type":1,
                "Value":[0]
            },
            {
                "Title":"Тип поиска",
                "Name":"MarketSearchAction",
                "ShortName":"t",
                "Type":1,
                "Value":1
            },
            {
                "Title":"Регион поставки",
                "Name":"KladrCodeRegion",
                "ShortName":"reg",
                "Type":0,
                "Value":"8600000000000"
            }
        ],
        "PaginationEventType":0,
        "Sorting":[
            {
                "direction":"Descending",
                "field":"PublicationDate"
            }
        ],
        "Paging":
        {
            "Page":1,
            "ItemsPerPage":200
        },
        "FilterSource":5
    },
    {
        "Filtering":
        [
            {
                "Title":"Регион поставки",
                "Name":"KladrCodeRegion",
                "ShortName":"reg",
                "Type":0,
                "Value":"7200000000000"
            },
            {
                "Title":"Статус",
                "Name":"Status",
                "ShortName":"st",
                "Type":1,
                "Value":[0]
            },
            {
                "Title":"Тип поиска",
                "Name":"MarketSearchAction",
                "ShortName":"t",
                "Type":1,
                "Value":1
            }
        ],
        "PaginationEventType":0,
        "Sorting":[
            {
                "direction":"Descending",
                "field":"PublicationDate"
            }
        ],
        "Paging":{
            "Page":1,
            "ItemsPerPage":9
        },"FilterSource":5
    },
    {
        "Filtering":
        [
            {
                "Title":"Регион поставки",
                "Name":"KladrCodeRegion",
                "ShortName":"reg",
                "Type":0,
                "Value":"7400000000000"
            },
            {
                "Title":"Статус",
                "Name":"Status",
                "ShortName":"st",
                "Type":1,
                "Value":[0]
            },
            {
                "Title":"Тип поиска",
                "Name":"MarketSearchAction",
                "ShortName":"t",
                "Type":1,
                "Value":1
            }
        ],
        "PaginationEventType":0,
        "Sorting":[
            {
                "direction":"Descending",
                "field":"PublicationDate"
            }
        ],
        "Paging":{
            "Page":1,
            "ItemsPerPage":9
        },"FilterSource":5
    },
    {
        "Filtering":
        [
            {
                "Title":"Регион поставки",
                "Name":"KladrCodeRegion",
                "ShortName":"reg",
                "Type":0,
                "Value":"4500000000000"
            },
            {
                "Title":"Статус",
                "Name":"Status",
                "ShortName":"st",
                "Type":1,
                "Value":[0]
            },
            {
                "Title":"Тип поиска",
                "Name":"MarketSearchAction",
                "ShortName":"t",
                "Type":1,
                "Value":1
            }
        ],
        "PaginationEventType":0,
        "Sorting":[
            {
                "direction":"Descending",
                "field":"PublicationDate"
            }
        ],
        "Paging":{
            "Page":1,
            "ItemsPerPage":9
        },"FilterSource":5
    }, 
    {
        "Filtering":
        [
            {
                "Title":"Регион поставки",
                "Name":"KladrCodeRegion",
                "ShortName":"reg",
                "Type":0,
                "Value":"6600000000000"
            },
            {
                "Title":"Статус",
                "Name":"Status",
                "ShortName":"st",
                "Type":1,
                "Value":[0]
            },
            {
                "Title":"Тип поиска",
                "Name":"MarketSearchAction",
                "ShortName":"t",
                "Type":1,
                "Value":1
            }
        ],
        "PaginationEventType":0,
        "Sorting":[
            {
                "direction":"Descending",
                "field":"PublicationDate"
            }
        ],
        "Paging":{
            "Page":1,
            "ItemsPerPage":9
        },"FilterSource":5
    }, 
    {
        "Filtering":
        [
            {
                "Title":"Регион поставки",
                "Name":"KladrCodeRegion",
                "ShortName":"reg",
                "Type":0,
                "Value":"6600000000000"
            },
            {
                "Title":"Статус",
                "Name":"Status",
                "ShortName":"st",
                "Type":1,
                "Value":[0]
            },
            {
                "Title":"Тип поиска",
                "Name":"MarketSearchAction",
                "ShortName":"t",
                "Type":1,
                "Value":1
            }
        ],
        "PaginationEventType":0,
        "Sorting":[
            {
                "direction":"Descending",
                "field":"PublicationDate"
            }
        ],
        "Paging":{
            "Page":1,
            "ItemsPerPage":9
        },"FilterSource":5
    },  
    ]


    for json_items in jsons_items:
        r = requests.post(url="https://zmo-new-webapi.rts-tender.ru/market/api/v1/trades/publicsearch2", headers=headers, json=json_items)
        time.sleep(2)
        data = r.json()['data']['items']

        for item_data in data:
            try:
                pub_date = datetime.datetime.strptime(item_data.get('PublicationDate'), '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(5/24)
                end_date = datetime.datetime.strptime(item_data.get('FillingApplicationEndDate'), '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(5/24)
            except ValueError:
                try:
                    pub_date = datetime.datetime.strptime(item_data.get('PublicationDate'), '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(5/24)
                    end_date = datetime.datetime.strptime(item_data.get('FillingApplicationEndDate'), '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(5/24)
                except ValueError:
                    pub_date = datetime.datetime.now()
                    end_date = datetime.datetime.now()
            #print(item_data.get('PublicationDate'))
            state = {
                'unique_id': str(item_data.get('Id')) + '_rts',
                'place': 'rts',
                'id_zak': str(item_data.get('Id')),
                'name_group_pos':item_data.get('Name'),
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

    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])
    return new_states, positions
