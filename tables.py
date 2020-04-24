# coding: utf-8
from config import *
from peewee import *

db = SqliteDatabase(current_folder + '/database.db')


class BaseModel(Model):
    class Meta:
        database = db


class State(BaseModel):
    unique_id = TextField(unique=True, verbose_name="Уникальный id")
    place = TextField(verbose_name="Наименование площадки")
    id_zak = TextField(verbose_name="ID закупки")
    name_group_pos = TextField(null=True, verbose_name="Название закупки")
    organization = TextField(null=True, verbose_name="Название организации")
    start_time = DateTimeField(null=True, verbose_name="Дата начала подачи заявок")
    end_time = DateTimeField(null=True, verbose_name="Дата окончания подачи заявок")
    created_time = DateTimeField(null=True, verbose_name="Дата создания закупки")
    current_status = TextField(null=True, verbose_name="Текущий статус")
    start_price = FloatField(null=True, verbose_name="Начальная цена")
    address = TextField(null=True, verbose_name="Адрес закупки") 
    url = TextField(null=True, verbose_name="Ссылка на закупку") 
    send = BooleanField(default=False, verbose_name="Отправлено или нет")
    add_trello = BooleanField(default=False, verbose_name="Добавлено в трелло или нет")

    
class StatePosition(BaseModel):
    unique_id = ForeignKeyField(State, verbose_name="Уникальный id закупки")
    name = TextField(null=True, verbose_name="Название позиции")
    amount = IntegerField(null=True, verbose_name="Количество")
    price = FloatField(null=True, verbose_name="Цена")


db.create_tables([
    State,
    StatePosition
])