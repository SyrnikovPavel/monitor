# coding: utf-8

from ftplib import FTP
from zipfile import ZipFile
from bs4 import BeautifulSoup
import time
import traceback
import sys
import os
import datetime
from config import current_folder


folder_zip = current_folder + '/notifications/zip_files/'
folder_unzip = current_folder + '/notifications/unzip_files/'
file_already = current_folder + '/already2.txt'

def replace_full_name(name: str):
    "Замена длинных названий на более короткие"
    name = name.replace('ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ УЧРЕЖДЕНИЕ ЗДРАВООХРАНЕНИЯ', 'ГБУЗ')
    name = name.replace('ТЮМЕНСКОЙ ОБЛАСТИ', 'ТО')
    name = name.replace('ОБЛАСТНАЯ КЛИНИЧЕСКАЯ БОЛЬНИЦА', 'ОКБ')
    name = name.replace('ОБЛАСТНАЯ БОЛЬНИЦА', 'ОБ')
    name = name.replace('ГОСУДАРСТВЕННОЕ АВТОНОМНОЕ УЧРЕЖДЕНИЕ ЗДРАВООХРАНЕНИЯ', 'ГАУЗ')
    name = name.replace('МНОГОПРОФИЛЬНЫЙ КЛИНИЧЕСКИЙ МЕДИЦИНСКИЙ ЦЕНТР', 'МКМЦ')  
    return name

def get_files_from_zipfile(filename: str):
    "Фукнция возвращает список файлов в архиве"
    with ZipFile(filename, 'r') as zip_obj:
        file_names = zip_obj.namelist()
        return [file_name for file_name in file_names if ((file_name.endswith('.xml')) and (('fcsNotificationEA44' in file_name) or ('fcsNotificationZK504' in file_name)))]

def unzip_files_from_folder(folder_zip='notifications/zip_files/', folder_unzip='notifications/unzip_files/'):
    'Функция для разархивации архивов'
    for file in os.listdir(folder_zip):
        zip_filename = folder_zip + file
        with ZipFile(zip_filename, 'r') as zip_obj:
            file_names = zip_obj.namelist()
            for file_name in file_names:
                if file_name.endswith('.xml') and 'contract_' in file_name:
                    if os.path.exists(folder_unzip + file_name) is False:
                        zip_obj.extract(file_name, folder_unzip)
    return 0
    
def unzip_file(filename, archive_name, folder_with_archives='notifications/zip_files/', folder_with_files = 'notifications/unzip_files/'):
    'Функция для разархивации конкретного файла'
    zip_filename = folder_with_archives + archive_name
    with ZipFile(zip_filename, 'r') as zip_obj:
        if os.path.exists(folder_with_files + filename) is False:
            zip_obj.extract(filename, folder_with_files)
    return 0


def update_zip_files_in_base(files: list):
    "Функция для обновления списка архивов"

    data_source = [{'name': file, 'download_bool': False, 'unzip_bool': False, 'update_all_bool': False} for file in files]
    with db.atomic():
        for batch in chunked(data_source, 20):
            Archive.insert_many(batch).on_conflict_ignore().execute()
            
    return 0

def need_add(soup, okpd2_codes, stop_okpd2_codes, customer_codes):
    "Функция для определения - подходит ли нам эта закупка"
    codes_okpd2 = list(set([x.code.getText() for x in soup.find_all('okpd2') if x.code is not None] + [x.find('okpdcode').getText() for x in soup.find_all('okpd2')  if x.find('okpdcode') is not None]))
    codes_okpd2 += list(set([x.code.getText()[:x.code.getText().find('-')] for x in soup.find_all('ktru')]))
    codes_okpd2 = list(set(codes_okpd2))
    for x in stop_okpd2_codes:
        if x in [y[:len(x)] for y in codes_okpd2]:
            return False
    for x in okpd2_codes:
        if x in [y[:len(x)] for y in codes_okpd2]:
            return True
    for x in soup.find_all('customerrequirement'):
        if x.customer.regnum.getText() in customer_codes:
            return True
    return False

def get_ready_file(filename='already2.txt'):
    "функция получает список уже готовых архивов"
    with open(filename, 'r', encoding='utf8') as file:
        return file.read().split('\n')[:-1]
    
def write_ready_file(ready_file, filename='already2.txt'):
    "Функция записывает готовый архив в список"
    with open(filename, 'a', encoding='utf8') as file:
        file.write(ready_file + '\t' + str(datetime.date.today()) + '\n')
    return 0

class UserFTP(FTP):
    
    host='ftp.zakupki.gov.ru'
    user='free'
    passwd='free'
    
    def login(self):
        super().login(user=UserFTP.user, passwd=UserFTP.passwd)
        
    def download_zip_file_from_ftp(self, filename, folder='/fcs_regions/Tjumenskaja_obl/notifications/currMonth', outfolder='notifications/zip_files/'):
        "Функция для скачивания конкретного zip файла из папки на ftp сервере"
        self.cwd(folder)
        outfile = str(outfolder) + str(filename)
        if os.path.exists(outfile) is False:
            with open(outfile, 'wb') as f:
                self.retrbinary('RETR ' + filename, f.write)
        return 0
    
    def get_all_zip_files_from_ftp(self, folder='/fcs_regions/Tjumenskaja_obl/notifications/currMonth', outfolder='notifications/zip_files/'):
        "Функция для получения zip файлов из папки на ftp сервере"
        self.cwd(folder)
        files = [file for file in self.nlst() if ((file[-4:]=='.zip') & ('2014' not in file))]
        return files
    
    def download_all_zip_file_from_ftp(self, folder='/fcs_regions/Tjumenskaja_obl/notifications/currMonth', outfolder='notifications/zip_files/'):
        "Функция для скачивания zip файлов из папки на ftp сервере"
        self.cwd(folder)
        for file in self.nlst():
            if file[-4:]=='.zip':
                outfile = str(outfolder) + str(file)
                if os.path.exists(outfile) is False:
                    with open(outfile, 'wb') as f:
                        self.retrbinary('RETR ' + file, f.write)
                        print(file)
        return 0

def get_state_and_positions(filename):
    "Функция для обработки файла и получения информации о закупке и позициях"
    
    
    with open(filename, encoding='utf8') as file:
        result = file.read().replace('ns1:', '').replace('ns2:', '').replace('ns3:', '').replace('ns4:', '').replace('ns5:', '').replace('ns6:', '').replace('ns7:', '').replace('ns8:', '').replace('ns9:', '')

    with open(filename, 'w', encoding='utf8') as file:
        file.write(result)
    
    stop_okpd2_codes = [
        '21.20', #лекарственные средства
    ]
    
    okpd2_codes = [
        '43.39.11',
        '43.99.90.100',
        '01.3',
        '81.3',
        '01.29',
        '18.12',
        '26.60',
        '32.50',
        '02.40.10',
        '14.12.30',
        '38.11.29',
        '38.11.52',
        '82.99.19',
        '91.01.12',
        '13.93.19.120',
        '17.22.11.130',
        '18.13.30.000',
        '22.11.11.000',
        '25.62.20.000',
        '25.99.29.190',
        '43.11.10.000',
        '43.29.12.110',
        '43.29.19.140',
        '43.99.70.000',
        '43.99.90.190',
        '45.20.23.000',
        '81.22.12.000',
        '95.29.14.119',
        '96.01.12.129',
    ]
    
    customer_codes = [
        '03672000118', #заводоуковск 12
        '03672000080', #исетск 13
        '10675000059', #медицинский город
        '03672000133', #уват20
        '01673000021', #управа ЦАО
        '01673000019', #управа КАО
        '01673000030', #управа ЛАО
        '01673000013', #управа ВАО
        '03673000376', #служба заказчика ЦАО
        '03673000378', #служба заказчика ЛАО
        '03673000394', #служба заказчика КАО
        '03673000452', #служба заказчика ВАО

    ]
    
    state = {}
    positions = []
    with open(filename, 'r', encoding="utf8") as fobj:
        xml = fobj.read()
        soup = BeautifulSoup(xml, 'lxml')
        if need_add(soup, okpd2_codes, stop_okpd2_codes, customer_codes):
            place = soup.etp.find('name').getText()
            id_zak = soup.purchasenumber.getText()
            name_group_pos = soup.purchaseobjectinfo.getText().replace('\r', ' ').replace('\n', ' ').replace('  ', ' ')
            organization = ", ".join([replace_full_name(x.customer.fullname.getText()) for x in soup.find_all('customerrequirement')])

            if soup.startdate is not None:
                start_time = soup.startdate.getText()
            else:
                start_time = soup.startdt.getText()

            if soup.enddate is not None:
                end_time = soup.enddate.getText()
            else:
                end_time = soup.enddt.getText()

            start_time = datetime.datetime.strptime(start_time[:-6], '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.datetime.strptime(end_time[:-6], '%Y-%m-%dT%H:%M:%S')
            current_status = "Активная" if datetime.datetime.now() <= end_time else "Завершена"
            start_price = float(soup.maxprice.getText())
            address = soup.deliveryplace.getText()
            url = soup.href.getText()

            state = {
                'unique_id': id_zak + '_' + place, 
                'place': place,
                'id_zak': id_zak,
                'name_group_pos': name_group_pos,
                'organization': organization,
                'start_time': start_time,
                'end_time': end_time,
                'created_time': start_time,
                'current_status': current_status,
                'start_price': start_price,
                'address': address,
                'url': url,
                'send': False,
                'add_trello': False,
            }
                
            positions += [{
                    'unique_id': id_zak + '_' + place,
                    'name': position.find_all('name')[-1].getText() if len(position.find_all('name'))>1 else position.find_all('name')[0],
                    'amount': float(position.quantity.value.getText()) if position.quantity.value is not None else None,
                    'price': float(position.price.getText()) if position.price is not None else None
            } for position in soup.find_all('purchaseobject')]
    return state, positions
    
def get_states_zakupki():

    print("Получаем закупки с сайта zakupki.gov")
    
    global current_folder
    
    folder_zip = current_folder + '/notifications/zip_files/'
    folder_with_files = current_folder + '/notifications/unzip_files/'
    file_already = current_folder + '/already2.txt'
    
    print(file_already)

    ftp = UserFTP(UserFTP.host)
    ftp.login()
    files = ftp.get_all_zip_files_from_ftp(outfolder=folder_zip)

    already_files = [x.split('\t')[0] for x in get_ready_file(file_already) if datetime.datetime.strptime(x.split('\t')[1], '%Y-%m-%d').date() < datetime.date.today() - datetime.timedelta(3)]

    files = [x for x in files if x not in already_files] # смотрим, чтобы файлы не повторялись

    states = []
    positions = []


    for ftp_file in files:
        ftp.download_zip_file_from_ftp(ftp_file, outfolder=folder_zip) # скачиваем файл
        files_in_archive = get_files_from_zipfile(folder_zip + ftp_file)
        for file in files_in_archive:
            unzip_file(file, ftp_file, folder_with_archives=folder_zip, folder_with_files=folder_with_files) # разархивируем файл
            state, positions_state = get_state_and_positions(folder_with_files + file)
            if state not in states and state != {}:
                states.append(state)
                positions += positions_state
            os.remove(folder_with_files + file)

        write_ready_file(ftp_file, file_already)

        os.remove(folder_zip + ftp_file)

    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])
    
    return new_states, positions