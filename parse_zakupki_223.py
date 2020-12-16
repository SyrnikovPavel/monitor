from ftplib import FTP, FTP_TLS
from zipfile import ZipFile
from bs4 import BeautifulSoup
import time
import traceback
import sys
import os
import datetime
import re
from config import current_folder

def need_add(soup, okpd2_codes, stop_okpd2_codes, customer_inns):
    "Функция для определения - подходит ли нам эта закупка"
    codes_okpd2 = list(set([x.code.getText() for x in soup.find_all('okpd2')]))
    codes_okpd2 = list(set(codes_okpd2))
    for x in stop_okpd2_codes:
        for y in codes_okpd2:
            min_len = min(len(x), len(y))
            if x[:min_len] == y[:min_len]:
                return False
    for x in okpd2_codes:
        for y in codes_okpd2:
            min_len = min(len(x), len(y))
            if x[:min_len] == y[:min_len]:
                return True
    for x in soup.find_all('customer'):
        if x.inn.getText() in customer_inns:
            return True
    return False

def get_files_from_zipfile(filename: str):
    "Фукнция возвращает список файлов в архиве"
    with ZipFile(filename, 'r') as zip_obj:
        file_names = zip_obj.namelist()
        return [file_name for file_name in file_names if file_name.endswith('.xml')]

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


def get_ready_file(filename='already_223.txt'):
    "функция получает список уже готовых архивов"
    with open(filename, 'r', encoding='utf8') as file:
        return file.read().split('\n')[:-1]
    
def write_ready_file(ready_file, filename='already_223.txt'):
    "Функция записывает готовый архив в список"
    with open(filename, 'a', encoding='utf8') as file:
        file.write(ready_file + '\t' + str(datetime.date.today()) + '\n')
    return 0


class UserFTP(FTP):
    
    host='ftp.zakupki.gov.ru'
    user='fz223free'
    passwd='fz223free'
    
    def login(self):
        super().login(user=UserFTP.user, passwd=UserFTP.passwd)
        
    def download_zip_file_from_ftp(self, filename, folder='/out/published/Tiumenskaya_obl/purchaseNotice/daily', outfolder='notifications/zip_files/'):
        "Функция для скачивания конкретного zip файла из папки на ftp сервере"
        self.cwd(folder)
        outfile = str(outfolder) + str(filename)
        if os.path.exists(outfile) is False:
            with open(outfile, 'wb') as f:
                self.retrbinary('RETR ' + filename, f.write)
        return 0
    
    def get_all_zip_files_from_ftp(self, folder='/out/published/Tiumenskaya_obl/purchaseNotice/daily', outfolder='notifications/zip_files/'):
        "Функция для получения zip файлов из папки на ftp сервере"
        self.cwd(folder)
        files = [file for file in self.nlst() if ((file[-4:]=='.zip') & ('2014' not in file))]
        return files
    
    def download_all_zip_file_from_ftp(self, folder='/out/published/Tiumenskaya_obl/purchaseNotice/daily', outfolder='notifications/zip_files/'):
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
    "Функция возвращает обработанные данные из файла"
    
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

    customer_inns = [
            '7215004008', #заводоуковск 12
            '7216001666', #исетск 13
            '7204006910', #медицинский город
            '7229000035', #ярково 24
            '7228000177', #ялуторовск 23
            '7225003941', #уват 20
            '7202029446', #управа ЦАО
            '7204006437', #управа КАО
            '7203107513', #управа ЛАО
            '7202184427', #управа ВАО
            '7202092511', #служба заказчика ЦАО
            '7203107513', #служба заказчика ЛАО
            '7204032331', #служба заказчика КАО
            '7203224792', #служба заказчика ВАО

    ]
    
    with open(filename, encoding='utf8') as file:
        result = file.read().replace('ns1:', '').replace('ns2:', '').replace('ns3:', '').replace('ns4:', '').replace('ns5:', '').replace('ns6:', '').replace('ns7:', '').replace('ns8:', '').replace('ns9:', '')

    with open(filename, 'w', encoding='utf8') as file:
        file.write(result)
       
    state = {}
    positions = []
    with open(filename, 'r', encoding="utf8") as fobj:
        xml = fobj.read()
        soup = BeautifulSoup(xml, 'lxml')
        
        if soup.electronicplaceinfo is not None and soup.applsubmisionstartdate is not None:
            if need_add(soup, okpd2_codes, stop_okpd2_codes, customer_inns):
                place = soup.electronicplaceinfo.find('name').getText()
                id_zak = soup.registrationnumber.getText()
                name_group_pos = soup.purchasenoticedata.find('name').getText().replace('\r', ' ').replace('\n', ' ').replace('  ', ' ')

                if soup.customer.shortname is not None:
                    organization = soup.customer.shortname.getText()
                else:
                    organization = soup.customer.fullname.getText()

                start_time = soup.applsubmisionstartdate.getText()
                end_time = soup.submissionclosedatetime.getText()


                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
                current_status = "Активная" if datetime.datetime.now() <= end_time else "Завершена"

                if soup.find('lot').initialsum is not None:
                    start_price = sum(float(lot.initialsum.getText()) for lot in soup.find_all('lot'))
                elif soup.find('lot').maxcontractprice is not None:
                    start_price = sum(float(lot.maxcontractprice.getText()) for lot in soup.find_all('lot'))
                else:
                    start_price = sum(float(lot.commodityitemprice.getText())*float(lot.qty.getText()) for lot in soup.find_all('lot'))



                address = ", ".join(list(set([place.address.getText() for place in soup.find_all('deliveryplace')])))
                url = soup.urlvsrz.getText()

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

                for lot in soup.find_all('lot'):
                    unique_id = id_zak + '_' + place
                    name = lot.subject.getText()
                    amount = float(lot.qty.getText()) if lot.qty is not None else 1
                    price = float(lot.commodityitemprice.getText()) if lot.commodityitemprice is not None else None
                    if price is None and lot.initialsum is not None:
                        price = float(lot.initialsum.getText())/amount
                    elif price is None and lot.maxcontractprice is not None:
                        price = float(lot.maxcontractprice.getText())/amount

                    positions += [{
                                    'unique_id': unique_id,
                                    'name': name,
                                    'amount': amount,
                                    'price': price
                    }]
                    
    return state, positions

def get_states_zakupki_223():

    print("Получаем закупки с сайта zakupki.gov (223 ФЗ)")
    
    global current_folder
    
    folder_zip = current_folder + '/notifications/zip_files/'
    folder_with_files = current_folder + '/notifications/unzip_files/'
    


    ftp = UserFTP(UserFTP.host, timeout=100)
    ftp.login()
    files = ftp.get_all_zip_files_from_ftp(outfolder=folder_zip)
    files = [x for x in files if datetime.datetime.strptime(re.search('_(\d{8})_', x).group(0), '_%Y%m%d_').date() >= datetime.date.today()-datetime.timedelta(10)] # смотрим, чтобы файлы не повторялись
    
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
        os.remove(folder_zip + ftp_file)

    unique_ids = []
    new_states = []
    for x in states:
        if x['unique_id'] not in unique_ids:
            if x not in new_states:
                new_states.append(x)
                unique_ids.append(x['unique_id'])

    
    return new_states, positions