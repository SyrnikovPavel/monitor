# coding: utf-8

import requests
import datetime
import time
from mailer import get_html, send_email 

def get_states_portal():
    """Функция возвращает сформированные позиции"""
    
    print("Получаем закупки с сайта portal")
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-length': '253',
        'content-type': 'application/json',
        'cookie': 'mos_id=CllGxlx+Y666cwxbdUZLAgA=; _ym_uid=1558338722192603260; _ym_d=1558338722; _ga=GA1.2.2057817595.1558338723; ls.Cart=%5B%5D; ls.Comparisons=%5B%5D; .AspNet.SharedPpCookie=CfDJ8HOt7-85a65HjqTXqgNd6m8i_Ob4kka03GnmTZCcu4nArIPxBc4i3ZOp8Xp42vKpHPmbKXVzQGx7FFILSe77kaStfVp8TxGwnZFItTpE3u9LlO2AAJVsDLhcs1IpxblYxL1XlTBXrhx8yl9GKwWbtHlmtn3W-__2-t-wxBNpNVOFWySo8W_13PrIEDEhi81yC2lSjXLaRfjLh0mz0yrWdp9RpiM9x-rwu_yPPT7KxkU7GXkwY4m1u6pgJRQE-tu3yc8_Q1f0i5hGxJktMtcdm0ktUFkCe5-tsv4GVcf1a9EBH_x8FSU8VZj24acDUHiqkDPT5WTliSAKJIXNQuyH8j4Hw4zKrMAFBJT3Gl05XPoHT2g-NMOBc_fiVZzsY2a1pwCRZwrPxg_BEimCDm8QiNffXCAeAQJsGbO1rXDBB7guxnEHQcLxuC6zudaRbwNOdF6aXdcMAJQTYcLzo1-Qu3NxO4oLzqQLz_u8E-233WrYfePHpQyu87xg5JCFKtpLFQ996Fi0qcMH78xxEXolyJusOFN-tmLETJv5VJaSNeGiF4xc1-QNwtAOJcVCzoaNVmXuGzvdxi_CKjzHTtBMOzGj8-4Fc4t6eZtlyoM8IbzTnTPHIFQnHHoKSNvrzhs3xVu7jbNqXPy1VXEd4XypGJQo2pMep3-N_LGKA2YKCivQQTk_gSkeP1XnLJ-fzfPehRNWiuhAtdozS7PGjbGPyh3yUoXvNSvdcofoLACbF9fdfH_WJxiKGpgwXHy1h7yLxeOREjq41UQUorpuIO13KgkYsnkoj2KHoBQ0qO76uUZpNMVXrNjW6Rls85p-QW6sPUAaGs5z37RfkpExhkcbWBOL1l8pJCA7QE9c61aNQXWu6zXGN9FfNJQhgB5_2Uwpm4NvsPxDrBkFBv79_lsg6YpAeZ8unndGkAAQgCzM5a1vt7lmdPlZ6Y1jyqI_J-NLHMiNK2IbYxvaW0ET1nTIfsbGW2xYWLYm2sqH5TvLmvlKBbAbwp30R3byEqEbgMCGuQ; _ym_isad=1; _ym_visorc_19942426=w; _ym_visorc_14112952=b',
        'origin': 'https://zakupki.mos.ru',
        'referer': 'https://zakupki.mos.ru/purchase/list?page=1&perPage=10&sortField=relevance&sortDesc=true&filter=%7B%22regionPaths%22%3A%5B%22.4422.%22%5D%2C%22auctionSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B19000002%5D%7D%2C%22needSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B20000002%5D%7D%2C%22tenderSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B5%5D%7D%7D',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    }
    
    states = []
    positions = []
    
    jsons = [
        {"filter":{"regionPaths":[".4422."],"auctionSpecificFilter":{"stateIdIn":[19000002]},"needSpecificFilter":{"stateIdIn":[20000002]},"tenderSpecificFilter":{"stateIdIn":[5]}},"order":[{"field":"relevance","desc":True}],"withCount":True,"take":1000,"skip":0},
        {"filter":{"regionPaths":[".192."],"auctionSpecificFilter":{"stateIdIn":[19000002]},"needSpecificFilter":{"stateIdIn":[20000002]},"tenderSpecificFilter":{"stateIdIn":[5]}},"order":[{"field":"relevance","desc":True}],"withCount":True,"take":1000,"skip":0},
    ]
    
    for js in jsons:
        r = requests.post('https://old.zakupki.mos.ru/api/Cssp/Purchase/PostQuery', headers=headers, json=js)
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
