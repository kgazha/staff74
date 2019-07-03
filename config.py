from sqlalchemy import create_engine


DATABASE_NAME = 'moodle'
DATABASE_HOST = '172.153.153.159:5433'
DATABASE_PASSWORD = ''

DATABASE_USER = 'postgres'
DATABASE_ENGINE = 'postgresql+psycopg2'
ENGINE = create_engine('{0}://{1}:{2}@{3}/{4}'.format(DATABASE_ENGINE,
                                                      DATABASE_USER,
                                                      DATABASE_PASSWORD,
                                                      DATABASE_HOST,
                                                      DATABASE_NAME))

PATH_WKTHMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

PROCESSED_USERS = 'processed_users.pkl'
BASE_DIR = r'Z:\команда74'
MOODLEDATA_DIR = r'C:\server\moodledata\repository'
