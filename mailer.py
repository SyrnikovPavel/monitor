from jinja2 import Template
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_html(states, template_file='template_tenders.html'):
    """Функция возвращает html данные для отправки"""
    html = open(template_file, encoding='utf8').read()
    template = Template(html)
    return template.render(states=states)
    
    
def send_email(message, to_email, login, pswrd, header='Новые закупки'):
    """
    Функция служит для отправки на почту сообщения прайса по одному адресу
    """

    gmail_user = login
    gmail_password = pswrd

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = header
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
