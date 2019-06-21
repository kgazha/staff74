import config
import os.path
import pickle
import pandas as pd
import xlsxwriter
import datetime
import report
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import sessionmaker


session = sessionmaker(bind=config.ENGINE)()
sql_form = open('completed.sql').read()
sql_result = session.execute(sql_form)
df = pd.DataFrame(sql_result.fetchall(), columns=sql_result.keys())
sent_cvs = []
url = 'https://команда74.рф/konkurs/pluginfile.php'


def get_header_format(workbook):
    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_text_wrap()
    header_format.set_align('center')
    header_format.set_align('vcenter')
    return header_format


def get_row_format(workbook):
    row_format = workbook.add_format()
    row_format.set_text_wrap()
    row_format.set_align('left')
    row_format.set_align('top')
    return row_format


def form_to_excel(form, form_name, columns):
    file_name = form_name + datetime.datetime.today().strftime("_%H_%M") + '.xlsx'
    folder_path = os.path.join(config.BASE_DIR, datetime.date.today().strftime("%d_%m_%Y"))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    workbook = xlsxwriter.Workbook(os.path.join(folder_path, file_name))
    worksheet = workbook.add_worksheet(name='Отчёт')
    worksheet.set_column(0, len(columns), 20)
    header_format = get_header_format(workbook)
    row_format = get_row_format(workbook)
    for idx, key in enumerate(columns):
        worksheet.write(0, idx, key, header_format)
    for idx, data in form.iterrows():
        for col_idx, (key, value) in enumerate(data.items()):
            worksheet.write(idx + 1, col_idx, value, row_format)
    workbook.close()


def df_to_form(df):
    form = df
    form['ФИО'] = df['lastname'] + ' ' + df['firstname']
    form['E-mail'] = df['email']
    form['Ссылка на видео'] = url + '/' + df['video_path']
    form['Оценка видео'] = ''
    form['Оценка резюме'] = ''
    form['Средняя оценка за тесты'] = df['percents']
    form = form.drop(['video_path', 'firstname', 'lastname', 'percents', 'username', 'email'], axis=1)
    return form


if os.path.isfile(config.SENT_CVS):
    with open(config.SENT_CVS, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        sent_cvs = unpickler.load()

# form = df_to_form(df)
# form_to_excel(form, 'report', form.keys())
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report.html')
rows = []
for idx, row in df.iterrows():
    if row['username'] not in sent_cvs:
        rows.append(row)
        sent_cvs.append(row['username'])


with open(config.SENT_CVS, 'wb') as f:
    pickle.dump(sent_cvs, f)

if rows:
    form = df_to_form(pd.DataFrame(rows))
    form_to_excel(form, 'report', form.keys())

    for idx, row in enumerate(rows):
        cv = report.get_user_cv_from_db(row['username'])
        output_from_parsed_template = template.render(cv.__dict__)
        with open("new_report.html", "w", encoding='utf-8') as f:
            f.write(output_from_parsed_template)
        report.make_pdf(os.path.join(config.BASE_DIR, datetime.date.today().strftime("%d_%m_%Y"), row['username']) + '.pdf')
