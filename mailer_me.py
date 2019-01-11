import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer:
    def __init__(self, login, pswrd, list_emails):
        self.login = login
        self.pswrd = pswrd
        self.list_emails = list_emails

    def formate_msg(self, purchases):
        """
        Функция формирует данные на отправку.
        Также функция ставит отметку отправлено в базу данных
        """

        mail = """
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <title>Новые закупки</title>
                <style type="text/css">
                    .all_items{
                       margin: 2%;
                    }
                    .one_item{
                      display: grid;
                      grid-auto-rows: auto auto auto auto;
                      margin-bottom: 3%;
                    }
                    .header{
                      font-weight: bold;
                    }
                    .header a{
                      text-decoration: none;
                    }
                    .main_info{
                      display: grid;
                      grid-template-rows: auto;
                      grid-template-columns: auto auto auto;
                    }
                    .value{
                      font-weight: bold;
                    }
                    .items{
                      display: grid;
                      grid-template-columns: repeat(4, 1fr);
                      border-top: 1px solid black;
                      border-right: 1px solid black;
                    }
                    .items > div {
                        padding: 8px 4px;
                        border-left: 1px solid black;
                        border-bottom: 1px solid black;
                    }
                    .table_header{
                      font-weight: bold;
                    }

                    .trello{
                      margin-top: 0.5%;
                    }
                </style>
            </head>
            <body>
            Добрый день!<br/>
            Высылаю новые закупки<br/>
            <div class="all_items">

        """
        for purchase, items in purchases.items():
            mail += """
            <div class="one_item">
            <div class="header">
                <a href="{otc_url}"">
                    Закупка {otc_number}. {otc_name}
                </a>
            </div>
            <div class="main_info">
                <div class="date">Срок окончания подачи заявки: <div class="value"> {otc_date_end_app}</div></div>
                <div class="amount">Сумма заявки: <div class="value"> {otc_price:0,.2f}</div></div>
                <div class="customer">Заказчик: <div class="value"> {otc_customer} </div></div>
            </div>
            """.format(
                otc_number=purchase.otc_number,
                otc_name=purchase.otc_name,
                otc_date_end_app=purchase.otc_date_end_app,
                otc_price=purchase.otc_price,
                otc_customer=purchase.otc_customer,
                otc_url=purchase.otc_url,
            )
            mail += """
                    <div class="items">
                        <div class="table_header">Наименование	</div>
                        <div class="table_header">Цена	</div>
                        <div class="table_header">Количество </div>
                        <div class="table_header">Сумма </div>
                    """
            for item in items:
                mail += """
                        <div class="table_item">{otc_name}</div>
                        <div class="table_item">{otc_price:0,.2f}</div>
                        <div class="table_item">{otc_count}</div>
                        <div class="table_item">{otc_sum:0,.2f}</div>
                """.format(
                    otc_name=item.otc_name,
                    otc_price=item.otc_price,
                    otc_count=item.otc_count,
                    otc_sum=item.otc_sum,
                )
            mail += """
                </div>
                <div class="trello"><a href="syrnikovpavel.pythonanywhere.com/tender/{otc_number}">Добавить в трелло</a></div>
            </div>""".format(
                otc_number=purchase.otc_number,
            )
            purchase.send = True
            purchase.save()
        return mail

    def send_email(self, message, to_email):
        """
        Функция служит для отправки на почту сообщения об обновлении прайса по одному адресу
        """

        gmail_user = self.login
        gmail_password = self.pswrd

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Новые закупки ОТС"
        msg['From'] = gmail_user
        msg['To'] = to_email

        # Create the body of the message (a plain-text and an HTML version).
        text = message
        html = message

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
            s.login(gmail_user, gmail_password)
            s.sendmail(gmail_user, to_email, msg.as_string())
            s.quit()
        return 0

    def send_mails(self, purchases):
        print("Формируем сообщение")
        message = self.formate_msg(purchases)
        for to_email in self.list_emails:
            print("Отправляем письма")
            self.send_email(message, to_email)
