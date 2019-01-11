import datetime, time, requests, json
from bs4 import BeautifulSoup
from create_tables import db, Purchase, Item


def save_tender_on_server(data, server="http://syrnikovpavel.pythonanywhere.com"):
    data["otc_date_end_app"] = str(data["otc_date_end_app"])
    r = requests.post(str(server) + "/tender/save", json=json.dumps(data))
    time.sleep(1)
    print("Отправка данных по закупке на сервер")
    return r.status_code


def save_tenderitem_on_server(data, otc_number, server="http://syrnikovpavel.pythonanywhere.com"):
    r = requests.post(str(server) + "/tenderitem/save/" + str(otc_number), json=json.dumps(data))
    time.sleep(1)
    print("Отправка данных по позициям закупки на сервер")
    return r.status_code


def merge_two_dicts(x, y):
    """
    Функция для объединения двух словарей
    """
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def prepare_date(date_str: str):
    """
    Функция для обработки даты.
    Принимает на вход строку (но может и объект datetime.datetime)
    И преобразовывает его в datetime.datetime
    """

    months = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05',
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12',
    }

    if type(date_str) == datetime.datetime:
        # если объект == datetime.datetime
        return date_str

    else:
        # иначе
        # Проверка на соответствие типу
        assert type(date_str) == str, "Object must be str"
        # Удаление из строки лишних символов
        date_str = date_str.replace('г.', ' ').replace('МСК', '').replace('  ', '').replace('\n', '')
        # Если присутствуют месяцы не в цифровом виде, то замена из на цифры
        for month, value in months.items():
            date_str = date_str.replace(month, value)

        # если в конце строки пустота
        if date_str[-1:] == ' ':
            # удаляем его
            date_str = date_str[:-1]

        # Если строка пустая
        if date_str == '':
            # возвращаем None
            return None
        else:
            # Иначе
            # преобразовываем в объект datetime.datetime
            try:
                date_str = datetime.datetime.strptime(date_str, '%d %m %Y %H:%M')
                return date_str
            except ValueError as err:
                # если не выходит преобразовать, то шаблон не соответвует строке
                print("Time data '{0}' does not match format '%d %m %Y %H:%M'".format(date_str))
                return None


def get_main_info(soup: BeautifulSoup):
    """
    Функция принимает на вход распарсенную страницу.
    На выходе выдает основую информацию в формате dict.
    """

    main_table = soup.find_all("table")[0]
    info = {}
    for tr in main_table.find_all('tr'):
        key = tr.find_all('td')[0].getText().replace(' ', '')
        value = tr.find_all('td')[1].getText().replace("\xa0", "").replace(",", ".").replace(
            '\r', '').replace('\n', '').replace('  ', '').replace('(Все закупки организации)', '').replace(' руб.', '')
        if value[0] == " ":
            value = value[1:]
        info.update({key: value})

    info = {
        "platform": info['Площадка'],
        "otc_name": info['НаименованиеЗакупки'],
        "otc_customer": info['Заказчик'],
        "otc_price": float(info['Суммаконтракта']),
    }

    return info


def get_date_info(soup: BeautifulSoup):
    """
    Функция принимает на вход распарсенную страницу.
    На выходе выдает информацию по датам в формате dict.
    """
    date_table = soup.find_all("table")[1]
    info = {}
    for tr in date_table.find_all('tr'):
        key = tr.find_all('td')[0].getText().replace(' ', '')
        value = tr.find_all('td')[1].getText().replace("\xa0", "").replace(",", ".").replace(
            '\r', '').replace('\n', '').replace('  ', '').replace('(Все закупки организации)', '').replace(' руб.', '')
        if value != "":
            if value[0] == " ":
                value = value[1:]
            if value[-1] == " ":
                value = value[:-1]
        info.update({key: value})
        key = tr.find_all('td')[2].getText().replace(' ', '')
        value = tr.find_all('td')[3].getText().replace("\xa0", "").replace(",", ".").replace(
            '\r', '').replace('\n', '').replace('  ', '').replace(' МСК', '')
        if value != "":
            if value[0] == " ":
                value = value[1:]
            if value[-1] == " ":
                value = value[:-1]
        info.update({key: value})

    info = {
        "otc_date_end_app": prepare_date(info['Срококончанияподачиоферт']) + datetime.timedelta(2/24),
    }
    return info


def get_items(otc_number: int):
    """Функция возвращает данные о товарах в закупке"""
    url_pattern = "https://market.otc.ru/ProductRequest/ByGroup?groupId={0}"
    otc_url = url_pattern.format(otc_number)
    r = requests.get(otc_url)
    return r.json()['Data']


def save_to_base(info: dict):
    """
    Функция получает на вход словарь и сохраняет данные в базу.
    При успешном сохранении отправляет 0.
    """
    if Purchase.get_or_none(Purchase.otc_number == info.get('otc_number')) is None:
        pusrchase = Purchase.create(
            otc_number=info.get('otc_number'),
            otc_name=info.get('otc_name'),
            otc_customer=info.get('otc_customer'),
            otc_price=info.get('otc_price'),
            otc_date_end_app=info.get('otc_date_end_app'),
            otc_url=info.get('otc_url')
            )
        return 0
    else:
        return 1


def save_to_base_items(otc_number: int, data: dict):
    """
    Функция получает на вход объект с данными с отс маркета и сохраняет их в базу.
    При успешном сохранении отправляет 0.
    """

    purchase = Purchase.get_or_none(Purchase.otc_number == otc_number)
    if purchase is not None:
        for item in data:
            if Item.get_or_none(Item.otc_id == item['Id']) is None:
                item_base = Item.create(
                    otc_number=purchase,
                    otc_id=item['Id'],
                    otc_name=item['Name'],
                    otc_okpd2_code=item['Okpd2Code'],
                    otc_okpd2_name=item['Okpd2Name'],
                    otc_price=item['Price'],
                    otc_count=item['Count'],
                    otc_sum=item['Sum']
                )
    return 0


def get_and_save_data(otc_number: int):
    """
    Функция получает на вход данные и сохраняет их в базу
    """
    soup = None
    try:
        # константные переменные
        need_platform = [
            "OTC-market / Секция Тюменская область",
        ]  # переменная для хранения рассматриваемых площадок для закупок

        url_pattern = "https://market.otc.ru/ProductRequestGroup/Index/{0}"  # паттерн для создания url

        # основное тело функции
        otc_url = url_pattern.format(otc_number)  # создание url
        print(otc_url)
        r = requests.get(otc_url)  # запрос на сервер
        if r.status_code != 500:
            soup = BeautifulSoup(r.content, 'lxml')  # распарсивание страницы
            main_info = get_main_info(soup)  # получение основных данных о закупке
            date_info = get_date_info(soup)  # получение информации о датах закупки
            info = merge_two_dicts(main_info, date_info)  # объединение двух словарей
            info.update({
                'otc_number': otc_number,
                'otc_url': otc_url
            })  # добавление в словари информации о номере закупки и url
            if info['platform'] in need_platform:  # Если платформа из запроса соответствует необходимым
                if save_to_base(info) == 0:  # Если закупку удлось сохранить
                    save_tender_on_server(info)
                    print("Закупка {0}. '{1}' успешно сохранена".format(info['otc_number'], info['otc_name']))
                    data = get_items(otc_number)  # получаем данные по объектам закупки
                    print("Получаем данные по товарам по данной закупке")
                    save_to_base_items(otc_number, data)  # сохраняем их в базу
                    save_tenderitem_on_server(data, otc_number)
                    print("Товары успешно получены и сохранены в базу")
            return 0
        else:
            return 1
    except IndexError:
        return soup


def get_information(otc_number: int):
    """
    Функция собирает информацию информацию по закупками из отс маркета.
    Возвращает последний номер закупки.
    """
    # константные переменные
    last_otc_number = otc_number
    need_platform = [
        "OTC-market / Секция Тюменская область",
    ]  # переменная для хранения рассматриваемых площадок для закупок
    url_pattern = "https://market.otc.ru/ProductRequestGroup/Index/{0}"  # паттерн для создания url

    # основное тело функции
    end_bool = True  # Переменная для определения конца цикла

    while end_bool:  # пока переменная не сигнализирует о конце цикла, выполнять
        soup = get_and_save_data(otc_number)  # получить и сохранить данные о закупке
        otc_number += 1  # увеличить номер закупки на 1
        if soup != 0:  # если возникла ошибка, скорее всего закончился список тендеров
            if soup.find("h4", {'class': 'text-center'})\
                    .getText() == " Закупка не найдена.  Документа не существует, либо у вас нет прав на просмотр. ":
                otc_number += 1  # если так и есть проверяем следующую закупку, вдруг просто урл битый
                otc_url = url_pattern.format(otc_number)
                r = requests.get(otc_url)  # отправляем запрос
                soup = BeautifulSoup(r.content, 'lxml')  # парсим страницу
                if soup.find("h4", {'class': 'text-center'})\
                        .getText() == " Закупка не найдена.  Документа не существует, либо у вас нет прав на просмотр. ":
                    last_otc_number = otc_number - 2  # если действительно нет закупки, то это последний номер закупки
                    end_bool = False  # конец цикла
                    print("Последний действующий номер ОТС {0}".format(last_otc_number))
        elif soup == 1:
            last_otc_number = otc_number - 1 # если действительно нет закупки, то это последний номер закупки
            end_bool = False  # конец цикла
            print("Последний действующий номер ОТС {0}".format(last_otc_number))
    return last_otc_number


def download_and_save_to_base(db):
    """
    Функция добывает и сохраняет данные в базу.
    """
    print("Подключаемся к базе")
    #  db.connect()
    print("Получаем последний номер закупки")
    otc_number = Purchase.select().order_by(Purchase.id.desc()).get().otc_number
    print("Добавляем информацию по закупкам")
    last_number = get_information(otc_number)
    return 0
