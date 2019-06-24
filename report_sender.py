import config
import os.path
import pickle
import pandas as pd
import xlsxwriter
import datetime
import report
from shutil import copyfile
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import sessionmaker


session = sessionmaker(bind=config.ENGINE)()
sql_form = open('user_files.sql').read()
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
    form['ФИО'] = form['lastname'] + ' ' + form['firstname']
    form['E-mail'] = form['email']
    form['Ссылка на видео'] = url + '/' + form['media_path']
    form['Оценка видео'] = ''
    form['Оценка резюме'] = ''
    form['Средняя оценка за тесты'] = form['percents']
    form = form.drop(['media_path', 'firstname', 'lastname', 'percents', 'username', 'email', 'filearea',
                      'contenthash', 'filename'], axis=1)
    return form


def get_actual_report_folder():
    path = os.path.join(config.BASE_DIR, datetime.date.today().strftime("%d_%m_%Y"))
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def copy_user_files(contenthash, repository_type, destination_path, filename):
    # user_files_sql = open('user_files.sql').read()
    # sql_result = session.execute(user_files_sql.format(userid))
    path = os.path.join(config.MOODLEDATA_DIR,
                        repository_type,
                        contenthash[:2],
                        contenthash[2:4],
                        contenthash)
    # destination_path = os.path.join(get_actual_report_folder(), username)
    # if not os.path.exists(destination_path):
    #     os.makedirs(destination_path)
    copyfile(path, os.path.join(destination_path, filename))


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
    # if row['username'] not in sent_cvs:
        rows.append(row)
        sent_cvs.append(row['username'])


with open(config.SENT_CVS, 'wb') as f:
    pickle.dump(sent_cvs, f)

if rows:
    video_rows = []
    for row in rows:
        if 'submission_files' in row['filearea']:
            video_rows.append(row)
    form = df_to_form(pd.DataFrame(video_rows))
    form_to_excel(form, 'report', form.keys())
    for idx, row in enumerate(rows):
        cv = report.get_user_cv_from_db(row['username'])
        output_from_parsed_template = template.render(cv.__dict__)
        with open("new_report.html", "w", encoding='utf-8') as f:
            f.write(output_from_parsed_template)
        destination_path = os.path.join(get_actual_report_folder(), row['username'])
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        filename = row['lastname'] + '_' + row['firstname']
        report.make_doc(os.path.join(destination_path, filename) + '.doc')
        if 'submission_files' not in row['filearea']:
            if 'private' not in row['filearea']:
                copy_user_files(row['contenthash'], 'video', destination_path, row['filename'])
            else:
                copy_user_files(row['contenthash'], 'scan', destination_path, row['filename'])
