# coding: utf-8

from mailer_me import Mailer
from config import login, pswrd
from otc_scrapper import *
from create_tables import db, Purchase, Item


def main(login, pswrd):
    print("Создаем объект мэйлер для рассылки")
    mail = Mailer(login=login, pswrd=pswrd, list_emails=['SyrnikovPavel@gmail.com', 'sursmirnav78@mail.ru','kx.perevalovo@mail.ru'])
    print("Запускаем функцию обновления")
    download_and_save_to_base(db)
    print("Забираем из базы неотправленные закупки ")
    purchases = {}
    for purchase in Purchase.select().where(Purchase.send == 0):
        items = Item.select().where(Item.otc_number == purchase)
        purchases.update({purchase: items})
    if len(purchases)>0:
        mail.send_mails(purchases)
    else:
        mail.send_email('Новых закупок нет', 'SyrnikovPavel@gmail.com')

if __name__=="__main__":
    main(login, pswrd)
