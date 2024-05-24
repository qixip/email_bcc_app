import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import aiosmtplib

class LoginFailedException(Exception):
    pass

def read_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

def read_emails_from_csv(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        return [row[0] for row in reader]

def split_email_list(email_list, n=50):
    for i in range(0, len(email_list), n):
        yield email_list[i:i + n]

async def send_email(email_list, subject, content, attachments=None, embedded_images=None):
    config = read_config()
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']
    email_address = config['email_address']
    email_password = config['email_password']

    fixed_text = """ 
    --
    Daniela Monica GUZU
    psiholog expert/psihoterapeut
    danielaguzu.ro
    psiholog-sector3.ro
    expertpsiholog@yahoo.com
    0770244914

    Dacă dorești să nu mai primești mail-uri din partea noastră, dă replay la acest mail cu "UNSUBSCRIBE"

    Toate cele bune!"""

    content += fixed_text

    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = ', '.join(email_list)
    msg['Subject'] = subject

    plain_text_content = MIMEText(content, 'plain')
    msg.attach(plain_text_content)

    if attachments:
        for attachment in attachments:
            msg.attach(attachment)

    if embedded_images:
        for image in embedded_images:
            msg.attach(image)

    try:
        server = aiosmtplib.SMTP(smtp_server, smtp_port, start_tls=True)
        await server.connect()
        await server.login(email_address, email_password)
        await server.send_message(msg)
        await server.quit()
    except aiosmtplib.SMTPAuthenticationError:
        raise LoginFailedException("SMTP authentication failed")
    except Exception as e:
        raise Exception("Failed to send email:", e)