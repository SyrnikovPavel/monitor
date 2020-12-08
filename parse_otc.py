# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
import time
import datetime
import json
import traceback

from tables import *

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
        if len(tr.find_all('td')) != 0:
            key = tr.find_all('td')[0].getText().replace(' ', '')
            value = tr.find_all('td')[1].getText().replace("\xa0", "").replace(",", ".").replace(
                '\r', '').replace('\n', '').replace('  ', '').replace('(Все закупки организации)', '').replace(' руб.', '')
            #print(key, value)
            if value is not None and value != "":
                if value[0] == " ":
                    value = value[1:]
                info.update({key: value})

    info = {
        "name_group_pos": info['НаименованиеЗакупки'],
        "organization": info['Заказчик'],
        "start_price": float(info.get('Суммаконтракта', info.get('Сумма'))),
    }

    return info


def get_date_info(soup: BeautifulSoup):
    """
    Функция принимает на вход распарсенную страницу.
    На выходе выдает информацию по датам в формате dict.
    """
    date_table = soup.find_all("table")[2]
    info = {}
    for tr in date_table.find_all('tr'):
        if len(tr.find_all('td')) != 0:
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
        "end_time": prepare_date(info['Срококончанияподачиоферт']) + datetime.timedelta(2/24),
        'start_time': None,
        'created_time': None,
    }
    return info


def get_items(otc_number: int):
    """Функция возвращает данные о товарах в закупке"""
    
    url_pattern = "https://market.otc.ru/ProductRequest/ByGroup?groupId={0}"
    otc_url = url_pattern.format(otc_number)
    r = requests.get(otc_url)
    positions = [{
        'unique_id': str(otc_number) + '_otc',
        'name': x['Name'], 
        'amount': int(x['Count']), 
        'price': float(x['Price'])
    } for x in r.json()['Data']] 
    return positions

def get_active_tenders_old():
    """Функция возвращает номера активных тендеров"""
    url_search = 'https://otc.ru/tenders?searchform.currencycode=643&searchform.organizationlevels=all&searchform.organizationlevels=fz223&searchform.organizationlevels=fz44&searchform.organizationlevels=pprf615&searchform.organizationlevels=small&searchform.organizationlevels=commercial&searchform.organizationstags=%5B%5D&searchform.period=4&searchform.region=7200000000000%7C&searchform.sectionids=91&searchform.sectionids=84&searchform.saleschannel=1'
    r = requests.get(url_search)
    soup = BeautifulSoup(r.content, 'lxml')

    if 'По запросу ничего не найдено' in soup.find('h2', {'itemprop': 'offers'}).getText():
        return []
    else:
        tender_numbers = list(set([int(re.search('/\d+-', x.get('href')).group(0).replace('/','').replace('-','')) for x in soup.find_all('a', {'class': 'panel_name'})]))
        if soup.find('div', {'class': 'row search-form-result-counter'}) is not None:
            real_count = int(re.search('\d+', soup.find('div', {'class': 'row search-form-result-counter'}).getText()).group(0))
        else:
            real_count = int(re.search('\d+', soup.find('h2', {'itemprop': 'offers'}).getText()).group(0))
        #assert len(tender_numbers) == real_count, 'Количество тендеров в поиске не совпадает с результатом'
        return tender_numbers
        
def get_active_tenders():
    """Функция возвращает номера активных тендеров"""
    url_search = 'https://otc.ru/microservices-otc/order/api/order/Search'
    headers = {
        #':authority': 'otc.ru',
        #':method': 'POST',
        #':path': '/microservices-otc/order/api/order/Search',
        #':scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-length': '681',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': '_ym_uid=1550729275319671314; _ga=GA1.2.1452771010.1550729276; _fbp=fb.1.1550729275898.768014267; ViewType=1; __exponea_etc__=aa6370c4-7230-4caf-8fd9-8be01169ba1d; gaIsValuable=1; FiltersToggle=%7B%22PriceToggler%22%3Afalse%2C%22ApplicationGuaranteeToggler%22%3Afalse%2C%22ContractGuaranteeToggler%22%3Afalse%2C%22DatePublishedToggler%22%3Afalse%2C%22ApplicationEndDateToggler%22%3Afalse%2C%22HasApplicationsToggler%22%3Afalse%2C%22OrganizationLevelsToggler%22%3Afalse%2C%22MarketPlacesSectionsToggler%22%3Atrue%2C%22ClassifiersToggler%22%3Afalse%7D; bd_userID=694981; IsCrmUser=False; AnonymousId=cd1cf174-fac6-4725-9119-4074a82b0172; _ym_d=1582614127; gaVisitorUuid=bef680ee-e28c-4e6a-b7b2-5305281dcf05; ASP.NET_SessionId=jf0ryzbdbej4xd4q55s5z0s3; _gid=GA1.2.840408994.1583994543; __exponea_time2__=-1.7677123546600342; _ym_isad=1; _ym_visorc_18136627=w; _pk_ref..3f7a=%5B%22%22%2C%22%22%2C1584073235%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses..3f7a=*',
        'origin': 'https://otc.ru',
        'referer': 'https://otc.ru/tenders?searchform.currencycode=643&searchform.organizationlevels=all&searchform.organizationlevels=fz223&searchform.organizationlevels=fz44&searchform.organizationlevels=pprf615&searchform.organizationlevels=small&searchform.organizationlevels=commercial&searchform.organizationstags=%5B%5D&searchform.period=4&searchform.region=7200000000000%7C&searchform.sectionids=91&searchform.sectionids=84&searchform.saleschannel=1',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36', 
    }

    json_search = {
        "filter_settings":{
            "isPersonal":True,
            "state":1,
            "keywords_list":[],
            "exclude_keywords_list":[],
            "universal_region":"7200000000000|",
            "delivery_city":None,
            "delivery_region":None,
            "okpd2":None,
            "is_doc_search":True,
            "purchase_methods":None,
            "currency_code":"643",
            "prepayment":None,
            "has_applications":None,
            "organization_levels":["all","Fz223","Fz44","pprf615","Small","Commercial"],
            "isApplicationWithoutSignatureAllowed":False,
            "section_ids":["91","84"],
            "organizationsTags":[],
            "is_msp":None,
            "sales_channels":["1"],
            "region":None,
        },

        "page_settings":{
            "sorting_field":"DatePublished",
            "sorting_direction":"Desc",
            "page_size":20,
            "page_index":1,
            "not_get_content_highlights":True
        },
        "saveToHistory":False
    }
    r = requests.post(url_search, headers=headers, json=json_search)
    soup = BeautifulSoup(r.content, "lxml")

    if r.json()['ErrorMessage'] is None:
        real_count = r.json()['Result']['TotalCount']
        tender_numbers = [x['TenderId'] for x in r.json()['Result']['Tenders']]
        # assert len(tender_numbers) == real_count, 'Количество тендеров в поиске не совпадает с результатом'
        return tender_numbers
    else:
        return []

def get_added_tenders():
    json_search = {
        "filter_settings":{
            "isPersonal":True,
            "state":1,
            "keywords_list":[],
            "exclude_keywords_list":[],
            "universal_region":None,
            "delivery_city":None,
            "delivery_region":None,
            "okpd2":None,
            "is_doc_search":False,
            "purchase_methods":[],
            "min_price":None,
            "max_price":None,
            "currency_code":643,
            "min_application_guarantee":None,
            "max_application_guarantee":None,
            "min_contract_guarantee":None,
            "max_contract_guarantee":None,
            "prepayment":None,
            "has_applications":None,
            "organization_levels":["Fz223","Fz44","Commercial","Pprf615"],
            "isApplicationWithoutSignatureAllowed":False,
            "section_ids":["84","91"],
            "organizationsTags":[],
            "is_msp":None,
            "publish_date_from":None,
            "publish_date_to":None,
            "aplication_end_date_from":None,
            "aplication_end_date_to":None,
            "combinedTradeRegistrationNumber":None,
            "sales_channels":[1],
            "publication_date_period":None,
            "region":"7200000000000|6"
        },
        "page_settings":{
            "sorting_field":"DatePublished",
            "sorting_direction":"Desc",
            "page_size":200,
            "page_index":1
        },
        "securityToken":"922BA9DC6C5B4736FB89051A8C1AB16BA7A68A8E11931B4B62F94D71ECB99CF872D210BF186BA7E45A8F6A9C2BADF9EBEA0FFF392B9506F266668BC3217DDF355E1DAD6DE61CAE776F0015D633B59BE42CF0581FB2AB7CD23946657B6BE77635083F7F8E669BDC89D2AD10A4B9F16D1623F2738CDD334F97477A0EB0A34E50EEFA16FD8833345CBC2F9CB659FB3BD62C654CDD792297C890B745BEBAC82BA2A8BF7DA885D40482FC95E4500E049D77D458E842615DA5267107A0BADA9A7CC37290103B2A25B2E18231FEDF58A4DEAEB7D3EFA63A7C2A7CFA23AA16C326B105472F79ACFF04F6D685CAA9076F773605FAB8C60B44CC804D788404A27F0F2EB450BDF26D8E05287240F0296CA07A3BCE222518FE3EE187092AA54F92164000F14099DE5BF7986B1849F6646607264CA2E16B84AC2645AE4B919DB2C2C2DD0D1516ABEFF5306158D97680622C96762DED81B28A1AC2C00ECC5332B0D297BF07308EA92D2FB8564B0C22F2D65C90A9DBE0FBD02D241B472E12F71DAC6484B543AAF29D1E6D485E53605A4C0B56F9FB2ED0351B538D5ED805AD502927897C74579EAF8BB9E8733CC341D0D3BCFD6D1B981B4ACBBDFEED1CAB55C729C30429C43EB50E9FF1B341FE360C084EE631C13A0EF715E1808AF3D77582A39C1A78F808414723B23DDE9EB253CDFD6093B2BF5FB52B3B69F408CC87AD89299BAA7DE1E866A2C73DB04C802468901EF540DAB0BA209B8FF7E8058A706B1BEDFADBA044DA466218E542260A43B844995EBDFEAA9F38D4DC17B8FF2326088BA19A4CDFC3BAA42D70871C87A810716A852466890A882DA70C865476D8439A349CD56737FF1E4A0BD9B40103D843BF7AD7DCC74928D8328E5A6F8C68FDB6C0E765FFF48CA4EBDB476FD5A1F9297C1F60EACC5FAD60009EB262E547DEB7A8B3A88DDB02F97FEE9B829A9962591FF28FDCADE45E882837F3274B34B303E16F4A13DB314E44D17F928A9A05DFC4805A9E1270203F7E4E78676A899D57A25D1FEA44FDFB422F3C298DA2C99698013EF5615DC5B8EA8B18CE01A1834F9F81F551CB6ABD11740393D6A8A54C3544EE7A1249C889DF9E2DDEB3674F780C9C271CE2D32A2793EC5C08E8C008D4B92F7BB611C26B4E7ACBFDEE70BCF72A19B4AA0F51B68124191748B9389AC0BF58B4FC8DE9FBCD572A3A886A791349467EE2939A37EDAD4BE8D4ED85CC6759C04A9747757918DBDD423404A2A532E523CA99A5B92312003615B939533B2C7C004F488A31C16CD8D49B5D73D6C629F3D9362649E51FB3FE35AD055EA107A7712A44CCF06B97FD86DC681662C2D452223C65019434D5ED166F8151AEF5A12ED7BB9CB59D7C2C11AEFCBE30D5D14B98C3F58DC8E6DF8E66A3DD80F88CFD5670C94CB24EA20171DA1ACFD1B225616B48778F69360770E6C2B1EE98ED5CEF69A40495B91E004458AD00868DC7DB46674BF3759593E7EE073790213194DEE2D5C099736D8FB29C8B7DFA3F4B0D5A4E5D795FDEF1894BCD3F0348AC8607357E3B5E78ACC91507DCD8A897B07D28A327983BB6AC48B9E20035C4082E3F3D53F5E9EDDD0910F4AB504137CFC831A9717BB2A1A86CE3E6FBFA8662F555F46D12F6AF561898B838876E9723A2B57263EFD173822864B54C6EA8D4F71F848468E658BD48231CB215CF99CC29D76F770E90E86110B080D987908B79562DE01D260315DFC1CF045C9270DDC55166000278B12972C11D90DC54355F337CB12668FA0FA3B0A5F1B329A80AB0D649E8855064CDCA3FA42F5AED86BA35AD5E895A6021A18277ED041A3DBDD2BD228CEFF76E9F85F5B9CD96FB3F410F41C6C7E4EBD529BBF21FF9AE218242E52CB88B83B4AAF5AABF192E96160EA99919",
        "saveToHistory":True}

    headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '544',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',    
        }

    url = 'https://otc.ru/microservices-otc/order/api/order/Search'

    r = requests.post(url=url, headers=headers, json=json_search)
    results = r.json()['Result']['Tenders']
    return [x['TenderId'] for x in results]


def get_one_state(otc_number: int):
    'Функция возвращает данные по одной закупке'
    url_pattern = "https://market.otc.ru/ProductRequestGroup/Index/{0}"
    otc_url = url_pattern.format(otc_number)
    try:
        r = requests.get(otc_url)
        soup = BeautifulSoup(r.content, 'lxml')
        main_info = get_main_info(soup)  # получение основных данных о закупке
        date_info = get_date_info(soup)  # получение информации о датах закупки
        state = merge_two_dicts(main_info, date_info)  # объединение двух словарей
        state.update({
            'unique_id': str(otc_number) + '_otc',
            'place': 'otc',
            'current_status': 'Активная',
            'address': None,
            'id_zak': otc_number,
            'url': otc_url,
            'send': False,
            'add_trello': False,
        })
        position = get_items(otc_number)
        return state, position
    except IndexError as err:
        traceback.print_exc()
        print(otc_url)

def get_states_otc():

    print("Получаем закупки с сайта otc")
    
    tender_numbers = get_active_tenders()
    tender_numbers += get_added_tenders()
    tender_numbers = list(set(tender_numbers))
    tender_number_not_in_base = []
    for tender_number in tender_numbers:
        if State.get_or_none(State.unique_id==str(tender_number)+'_otc') is None:
            tender_number_not_in_base.append(tender_number)
    states = []
    positions = []
    for otc_number in tender_number_not_in_base:
        state, position = get_one_state(otc_number)
        if state not in states:
            states += [state]
            positions += position
        
    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])
    return new_states, positions

if __name__ == '__main__':
    data = get_states_otc()
    message = get_html(data)
    send_email(message, "SyrnikovPavel@gmail.com", "SyrnikovPavel@gmail.com", "Nastya26042015")
    send_email(message, "sursmirnav78@mail.ru", "SyrnikovPavel@gmail.com", "Nastya26042015")