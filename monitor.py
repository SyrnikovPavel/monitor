# coding: utf-8

from tables import *
from mailer import *
from config import *
import json
import requests
import time
from parse_portal import get_states_portal
from parse_ber import get_states_ber
from parse_otc import get_states_otc
from parse_zakupki import get_states_zakupki
from parse_rts import get_states_rts
from parse_techtorg import get_states_tektorg

def find_actual_tenders():
    """Функция находит на всех площадках актуальные тендеры"""

    actual_states = []
    actual_positions = []

    actual_states_portal, actual_positions_portal = get_states_portal()
    actual_states += actual_states_portal
    actual_positions += actual_positions_portal

    actual_states_ber, actual_positions_ber = get_states_ber()
    actual_states += actual_states_ber
    actual_positions += actual_positions_ber
    
    actual_states_tektorg, actual_positions_tektorg = get_states_tektorg()
    actual_states += actual_states_tektorg
    actual_positions += actual_positions_tektorg

    #actual_states_otc, actual_positions_otc = get_states_otc()
    #actual_states += actual_states_otc
    #actual_positions += actual_positions_otc
    
    actual_states_zakupki, actual_positions_zakupki = get_states_zakupki()
    actual_states += actual_states_zakupki
    actual_positions += actual_positions_zakupki
    
    actual_states_rts, actual_positions_rts = get_states_rts()
    actual_states += actual_states_rts
    actual_positions += actual_positions_rts
    
    n_actual_states = []
    for actual_state in actual_states:
        if actual_state not in n_actual_states:
            n_actual_states.append(actual_state)
            
    n_actual_positions = []
    for actual_position in actual_positions:
        if actual_position not in n_actual_positions:
            n_actual_positions.append(actual_position)
    
    return n_actual_states, n_actual_positions


def update_tenders_in_base(actual_states, actual_positions):
    """Функция обновляет актуальные тендеры в базе"""
    actual_states_not_in_base = []
    for actual_state in actual_states:
        if State.get_or_none(State.unique_id==actual_state['unique_id']) is None:
            actual_states_not_in_base.append(actual_state)
       
    with db.atomic():
        for batch in chunked(actual_states_not_in_base, 20):
            State.insert_many(batch).execute()
            
    actual_states_unique_ids = [x['unique_id'] for x in actual_states_not_in_base]
    actual_positions_not_in_base = []
    for actual_position in actual_positions:
        if type(actual_position['unique_id']) != State:
            if actual_position['unique_id'] in actual_states_unique_ids:
                actual_position['unique_id'] = State.get(State.unique_id==actual_position['unique_id'])
                actual_positions_not_in_base.append(actual_position)
        else:
            if actual_position['unique_id'] in actual_states_unique_ids:
                actual_positions_not_in_base.append(actual_position)
    with db.atomic():
        for batch in chunked(actual_positions_not_in_base, 100):
            StatePosition.insert_many(batch).execute()
    return 0


def save_tender_on_server(data, server="http://syrnikovpavel.pythonanywhere.com"):
    for row in data['actual_states']:
        if row['start_time'] is not None:
            row['start_time'] = str(row['start_time'])
       
        if row['end_time'] is not None:
            row['end_time'] = str(row['end_time'])
            
        if row['created_time'] is not None:
            row['created_time'] = str(row['created_time'])

    r = requests.post(str(server) + "/tender_save", json=json.dumps(data))
    time.sleep(1)
    print("Отправка данных по закупке на сервер")
    return r.status_code


def get_all_tenders_not_send():
    """Функция возвращает все неотправленные тендеры"""
    states = {}
    for state in State.select().where(State.send==False):
        states.update({state.unique_id: {'state': state}})
        positions = [x for x in StatePosition.select().where(StatePosition.unique_id==state)]
        states[state.unique_id].update({'positions':positions}) 
    return states


def get_one_tender(unqiue_id: str):
    """Функция возвращает данные по тендеру"""
    state = State.get_or_none(State.unique_id==unqiue_id)
    if state is not None:
        positions = [x for x in StatePosition.select().where(StatePosition.unique_id==state)]
        return {'state': state, 'positions': positions}
    else:
        return {}
    

def send_tenders(states, current_folder):
    """Функция служит для отправки письма и сохранения данных в базу"""
    html = get_html(states, template_file = current_folder + '/template_tenders.html')
    if send_email(html, "SyrnikovPavel@gmail.com", lgn, pswrd, header='Новые закупки') == 0:
        for unique_id, state_dict in states.items():
            state_dict['state'].send = True
            state_dict['state'].save()
    else:
        send_tenders(states, current_folder)
    send_email(html, "sursmirnav78@mail.ru", lgn, pswrd, header='Новые закупки')
    send_email(html, "89129295427@mail.ru", lgn, pswrd, header='Новые закупки')


def main():
    """Функция для основной логики программы"""
    actual_states, actual_positions = find_actual_tenders()
    print(save_tender_on_server({'actual_states':actual_states, 'actual_positions':actual_positions}))
    update_tenders_in_base(actual_states, actual_positions)
    not_send_states = get_all_tenders_not_send()
    if not_send_states != {}:
        send_tenders(not_send_states, current_folder)


if __name__ == '__main__':
    main()