import requests
import datetime
import time
import re
from bs4 import BeautifulSoup

def get_datetime(text: str):
    "Функция возвращает дату в формате datetime"
    date_str = re.search("\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", text).group(0)
    return datetime.datetime.strptime(date_str, "%d.%m.%Y %H:%M")

def get_states_tektorg():
    "Функция возвращает закупки с площадки tektorg тюменский портал поставщиков"
    
    print("Получаем закупки с сайта tektorg")
    
    states = []
    positions = []
    
    url = "https://www.tektorg.ru/portal_tyumen/procedures?lang=ru&status=270&limit=500"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    for procedure in soup.find_all("div", {"class": "section-procurement__item"}):
        id_zak = re.search("\d+", procedure.find("div", {"class": "section-procurement__item-numbers"}).getText()).group(0)
        name_group_pos = procedure.find("a", {"class": "section-procurement__item-title"}).getText()
        organization = procedure.find_all("div", {"class": "section-procurement__item-description"})[0].a.getText()
        start_time = get_datetime(procedure.find_all("div", {"class": "section-procurement__item-dateTo"})[0].getText())
        end_time = get_datetime(procedure.find_all("div", {"class": "section-procurement__item-dateTo"})[1].getText())
        created_time = start_time

        url = "https://www.tektorg.ru" + procedure.find("a", {"class": "section-procurement__item-title"}).get("href")

        state = {
            'unique_id': str(id_zak) + '_tektorg', 
            'place': 'tektorg',
            'id_zak': int(id_zak),
            'name_group_pos': name_group_pos,
            'organization': organization,
            'start_time': start_time,
            'end_time': end_time,
            'created_time': created_time,
            'current_status': "active",
            'start_price': None,
            'address': None,
            'url': url,
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