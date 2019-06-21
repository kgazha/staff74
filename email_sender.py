import smtplib
from email.message import EmailMessage
import pickle
import os.path
import config


sent_emails = []
s = smtplib.SMTP(config.SMTP_SERVER)

if os.path.isfile(config.SENT_EMAILS_FILENAME):
    with open(config.SENT_EMAILS_FILENAME, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        sent_emails = unpickler.load()

print(sent_emails)


def send_email(email_to, subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_FROM
    msg['To'] = email_to
    s.send_message(msg)


with open(config.SUCCESSFUL_TEMPLATE) as f:
    content = f.read()

mail_to = 'k.gazha@mininform74.ru'


if mail_to not in sent_emails:
    send_email(mail_to, 'theme', content.format('username'))
    sent_emails.append(mail_to)
    with open(config.SENT_EMAILS_FILENAME, 'wb') as f:
        pickle.dump(sent_emails, f)

s.quit()
