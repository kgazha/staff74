from sqlalchemy import create_engine


DATABASE_NAME = 'moodle'
DATABASE_HOST = '10.14.1.94'
DATABASE_PASSWORD = 'Ue<tH%2HfP6GhJDfQl&!'

DATABASE_USER = 'postgres'
DATABASE_ENGINE = 'postgresql+psycopg2'
ENGINE = create_engine('{0}://{1}:{2}@{3}/{4}'.format(DATABASE_ENGINE,
                                                      DATABASE_USER,
                                                      DATABASE_PASSWORD,
                                                      DATABASE_HOST,
                                                      DATABASE_NAME))

PATH_WKTHMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

EMAIL_FROM = 'k.gazha@mininform74.ru'
UNSUCCESSFUL_TEMPLATE = 'unsuccessful_template.txt'
SUCCESSFUL_TEMPLATE = 'successful_template.txt'
SENT_EMAILS_FILENAME = 'sent_emails.pkl'
SENT_CVS = 'sent_cvs.pkl'
SMTP_SERVER = 'mail.gov74.ru'
BASE_DIR = 'Z:\Отчеты OTRS\CallCenter'
