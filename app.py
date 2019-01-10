from flask import Flask
from flask import g, redirect, request, session, jsonify, abort, json
from trello import TrelloClient
from config import login, pswrd
from peewee import *
from create_tables import db, Purchase, Item
from otc_scrapper import save_to_base, save_to_base_items
import sender
import datetime
import threading

app = Flask(__name__)
app.config.from_object(__name__)


def form_desc_for_cards(purchase, items):
    """
    Функция формирует описание закупки
    """
    mail = "Срок окончания подачи заявки: {otc_date_end_app} \
    \n\nСумма заявки: {otc_price:0,.2f}\n\nЗаказчик:  {otc_customer} \
    \n\n[Ссылка на закупку]({otc_url})\n\n".format(
            otc_date_end_app=purchase.otc_date_end_app,
            otc_price=purchase.otc_price,
            otc_customer=purchase.otc_customer,
            otc_url=purchase.otc_url,
        )
    mail += "---\n\nОбъекты закупки:\n\n\n\n"
    for item in items:
        mail += "- {otc_name}\t{otc_price:0,.2f}\t{otc_count}\t{otc_sum:0,.2f}\n\n".format(
            otc_name=item.otc_name,
            otc_price=item.otc_price,
            otc_count=item.otc_count,
            otc_sum=item.otc_sum,
        )
    mail += "---"
    return mail


def add_new_card(id_purchase):
    """
    Функция добавляет карточку с информацией из базы данных
    """
    purchase = Purchase.select().where(Purchase.otc_number == int(id_purchase)).get()
    items = Item.select().where(Item.otc_number == purchase)
    client = TrelloClient(
        api_key='3a950be8d9a067357e8aa3b6f7637fb7',
        api_secret='fd100381b0c68994d56a7bab23a0155577f9a877f93c7026a76f3c21c405e373',
    )

    list_for_new = client.get_list('5b42f6d8787410608050c87e')
    red_label = client.get_label(label_id='5b42f68c9c16fb124a1cd32d', board_id='5b42f68cfa7e02948429e696')
    card = list_for_new.add_card(
        labels=[red_label],
        name="Закупка {otc_number}. {otc_name}".format(otc_number=purchase.otc_number, otc_name=purchase.otc_name),
        desc=form_desc_for_cards(purchase, items),
    )
    members = client.get_board(board_id='5b42f68cfa7e02948429e696').get_members()
    for member in members:
        card.add_member(member)
    card.set_due(purchase.otc_date_end_app-datetime.timedelta(10/24))
    return 0


def from_request_to_dict(request):
    my_json = request.json

    data = json.loads(my_json)
    return data


@app.route('/tenderitem/save/<int:otc_id>', methods=['GET', 'POST'])
def tender_item_save(otc_id):
    """
    Get JSON in format
    [
      {
        'Count': 2.0,
        'Id': 802568,
        'Name': 'Тумба под аппаратуру 800х400х600',
        'Okpd2Code': '31.01.12.150',
        'Okpd2Name': 'Тумбы офисные деревянные',
        'OkpdCode': '',
        'Price': 1950.0,
        'PriceHasValue': True,
        'Sum': 3900.0,
        'Unit': 'ШТ',
        'UnitCode': '796'
      },
      {
        'Count': 2.0,
        'Id': 802568,
        'Name': 'Тумба под аппаратуру 800х400х600',
        'Okpd2Code': '31.01.12.150',
        'Okpd2Name': 'Тумбы офисные деревянные',
        'OkpdCode': '',
        'Price': 1950.0,
        'PriceHasValue': True,
        'Sum': 3900.0,
        'Unit': 'ШТ',
        'UnitCode': '796'
      }
    ]

    """
    data = from_request_to_dict(request)
    save_to_base_items(otc_id, data)
    return "Sucsess"


@app.route('/tender/save', methods=['GET', 'POST'])
def tender_save():
    """
    Get JSON in format
    {
        'otc_customer': 'name_customer',
        'otc_date_end_app': data,
        'otc_name': 'name_zakup',
        'otc_number': numer_zakup,
        'otc_price': price_zakup,
        'otc_url': 'url_zakup',
        'platform': 'platform_zakup'
    }
    """
    data = from_request_to_dict(request)
    save_to_base(data)
    return "Sucsess"


@app.route('/update')
def update():
    # the long running process...
    t = threading.Thread(target=sender.main, args=(login, pswrd,))
    t.start()
    # end the long running process
    return jsonify({"success": True})


@app.route('/tender/<otc_number>')
def add_page(otc_number):
    add_new_card(otc_number)
    return "Sucsecc"


if __name__ == "__main__":

    app.debug = True
    app.run(threaded=True)
