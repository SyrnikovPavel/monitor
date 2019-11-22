from flask import Flask
from flask import g, redirect, request, session, jsonify, abort, json
from trello import TrelloClient
from jinja2 import Template
from config import *
from tables import *
from monitor import get_one_tender, update_tenders_in_base
import datetime
import threading


app = Flask(__name__)
app.config.from_object(__name__)


def get_html_for_trello(state_dict, template_file='/home/SyrnikovPavel/mysite/otc/template_tender_trello.html'):
    """Функция возвращает html данные для отправки"""
    html = open(template_file, encoding='utf8').read()
    template = Template(html)
    return template.render(state_dict=state_dict)


def add_new_card(unique_id):
    """
    Функция добавляет карточку с информацией из базы данных
    """

    state_dict = get_one_tender(unique_id)

    if state_dict['state'].add_trello == False:

        client = TrelloClient(
            api_key=api_key,
            api_secret=api_secret,
        )

        places = {
            'otc': client.get_label(label_id='5b42f68c9c16fb124a1cd32d', board_id='5b42f68cfa7e02948429e696'),
            'zakupki': client.get_label(label_id='5b42f68c9c16fb124a1cd32b', board_id='5b42f68cfa7e02948429e696'),
            'other': client.get_label(label_id='5b42f68c9c16fb124a1cd329', board_id='5b42f68cfa7e02948429e696'),
            'portal': client.get_label(label_id='5b42f68c9c16fb124a1cd333', board_id='5b42f68cfa7e02948429e696'),
            'berezka': client.get_label(label_id='5b42f68c9c16fb124a1cd336', board_id='5b42f68cfa7e02948429e696'),
            'rts': client.get_label(label_id='5b42f68c9c16fb124a1cd328', board_id='5b42f68cfa7e02948429e696'),
        }

        place = state_dict['state'].place
        label = places.get(place)

        list_for_new = client.get_list('5b42f6d8787410608050c87e')

        card = list_for_new.add_card(
            labels=[label],
            name="Закупка {number}. {name}".format(number=state_dict['state'].id_zak, name=state_dict['state'].name_group_pos),
            desc=get_html_for_trello(state_dict).replace('\\n','\n').replace('\\t','\t'),
        )

        members = client.get_board(board_id='5b42f68cfa7e02948429e696').get_members()
        for member in members:
            card.add_member(member)
        if state_dict['state'].end_time is not None:
            card.set_due(state_dict['state'].end_time-datetime.timedelta(10/24))
        elif state_dict['state'].start_time is not None:
            card.set_due(state_dict['state'].start_time-datetime.timedelta(8/24))
        state_dict['state'].add_trello = True
        state_dict['state'].save()
        return 'Карточка успешно добавлена'
    else:
        return 'Карточка была добавлена ранее'


def from_request_to_dict(request):
    my_json = request.json
    data = json.loads(my_json)
    return data


@app.route('/tender_save', methods=['GET', 'POST'])
def tender_item_save():
    data = from_request_to_dict(request)
    if update_tenders_in_base(data['actual_states'], data['actual_positions']) == 0:
        return 'Sucsess'
    else:
        return "Что-то пошло не так"


@app.route('/tender/<unique_id>')
def add_page(unique_id):
    return add_new_card(unique_id)


if __name__ == "__main__":

    app.debug = True
    app.run(threaded=True)
