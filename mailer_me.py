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
            Добрый день!<br/>
            Высылаю новые закупки.<br/><br/>

        """
        for purchase, items in purchases.items():
            mail += """
            <b> Закупка {otc_number}. {otc_name} </b><br/>
            Срок окончания подачи заявки: <b> {otc_date_end_app} </b><br/>
            Сумма заявки: <b> {otc_price:0,.2f} </b><br/>
            <small> Заказчик:  {otc_customer} </small><br/>
            <a href="{otc_url}"> Перейти к закупке </a><br/>
            """.format(
                otc_number=purchase.otc_number,
                otc_name=purchase.otc_name,
                otc_date_end_app=purchase.otc_date_end_app,
                otc_price=purchase.otc_price,
                otc_customer=purchase.otc_customer,
                otc_url=purchase.otc_url,
            )
            mail += """
                    <table>
                        <tr>
                            <th> Наименование </th>
                            <th> Цена </th>
                            <th> Количество </th>
                            <th> Сумма </th>
                        </tr>
                    """
            for item in items:
                mail += """
                        <tr>
                            <td> {otc_name} </td>
                            <td> <b>{otc_price:0,.2f}</b> </td>
                            <td> {otc_count} </td>
                            <td> <b>{otc_sum:0,.2f}</b> </td>
                        </tr>
                        """.format(
                    otc_name=item.otc_name,
                    otc_price=item.otc_price,
                    otc_count=item.otc_count,
                    otc_sum=item.otc_sum,
                )
            mail += """</table><br/><br/>"""
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
