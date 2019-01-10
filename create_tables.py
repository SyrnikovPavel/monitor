from peewee import *
from config import db_file

db = SqliteDatabase(db_file)


class BaseModel(Model):
    class Meta:
        database = db


class Purchase(BaseModel):
    otc_number = IntegerField(unique=True, verbose_name="Номер закупки в системе ОТС")
    otc_name = TextField(verbose_name="Название закупки")
    otc_customer = TextField(verbose_name="Наименование заказчика")
    otc_price = FloatField(verbose_name="Начальная цена закупки")
    otc_date_end_app = DateTimeField(verbose_name="Дата окончания подачи заявок")
    otc_url = TextField(verbose_name="Ссылка на закупку")
    send = BooleanField(default=False, verbose_name="Отправлено")


class Item(BaseModel):
    otc_number = ForeignKeyField(Purchase)
    otc_id = IntegerField(unique=True, verbose_name="Номер товара в системе ОТС")
    otc_name = TextField(verbose_name="Название товара")
    otc_okpd2_code = TextField(verbose_name="Код ОКПД2 товара")
    otc_okpd2_name = TextField(verbose_name="Название ОКПД2 товара")
    otc_price = FloatField(verbose_name="Начальная цена за товар")
    otc_count = FloatField(verbose_name="Количество товара")
    otc_sum = FloatField(verbose_name="Сумма за товар")

db.create_tables([Purchase, Item])
