# -*- coding: utf-8 -*-
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
from PIL import Image
# from selenium_parser import MoodleParser


session = sessionmaker(bind=config.ENGINE)()
completed_tests_sql = open('completed_tests.sql').read()
completed_tests = session.execute(completed_tests_sql)
df = pd.DataFrame(completed_tests.fetchall(), columns=completed_tests.keys())
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
    for idx, (n_data, data) in enumerate(form.iterrows()):
        for col_idx, (key, value) in enumerate(data.items()):
            worksheet.write(idx + 1, col_idx, value, row_format)
    workbook.close()


def df_to_form(df):
    form = df
    form['ФИО'] = form['lastname'] + ' ' + form['firstname']
    form['E-mail'] = form['email']
    # form['Ссылка на видео'] = url + '/' + form['media_path']
    form['Ссылка на видео'] = form['video_url']
    form['Оценка видео'] = ''
    form['Оценка резюме'] = ''
    form['Средняя оценка за тесты'] = form['percents']
    form = form.drop(['username', 'firstname', 'lastname', 'percents', 'test_complited',
                      'email', 'userid', 'video_url'], axis=1)
    return form


def get_actual_report_folder():
    path = os.path.join(config.BASE_DIR, datetime.date.today().strftime("%d_%m_%Y"))
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def copy_user_files(contenthash, destination_path, filename):
    repository_types = ['video', 'scan']
    for repository_type in repository_types:
        path = os.path.join(config.MOODLEDATA_DIR,
                            repository_type,
                            contenthash[:2],
                            contenthash[2:4],
                            contenthash)
        if os.path.exists(path):
            copyfile(path, os.path.join(destination_path, filename))


if os.path.isfile(config.SENT_CVS):
    with open(config.SENT_CVS, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        sent_cvs = unpickler.load()

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report.html')
template_doc = env.get_template('report_doc.html')
rows = []
for idx, row in df.iterrows():
    # if row['username'] not in sent_cvs:
        rows.append(row)
        sent_cvs.append(row['username'])


with open(config.SENT_CVS, 'wb') as f:
    pickle.dump(sent_cvs, f)

# mp = MoodleParser()
# mp.login()
# try:
#     mp.get_user_profile_photo(41, r'C:\projects\team74')
#     mp.get_user_profile_photo(14, r'C:\projects\team74')
# except Exception as ex:
#     print(ex)
# mp.close()
# exit()
if rows:
    user_files = []
    for row in rows:
        user_files_sql = open('user_files.sql').read()
        files = session.execute(user_files_sql.format(row['userid']))
        df_user_files = pd.DataFrame(files.fetchall(), columns=files.keys())
        user_files.append(df_user_files)
        for idx, file_row in df_user_files.iterrows():
            if 'submission_files' in file_row['filearea']:
                row['video_url'] = url + '/' + file_row['filename']
    form = df_to_form(pd.DataFrame(rows))
    form_to_excel(form, 'report', form.keys())
    for idx, row in enumerate(rows):  # video_rows
        cv = report.get_user_cv_from_db(row['userid'])
        output_from_parsed_template_doc = template_doc.render(cv.__dict__)
        with open("new_report_doc.html", "w", encoding='utf-8') as f:
            f.write(output_from_parsed_template_doc)
        destination_path = os.path.join(get_actual_report_folder(), row['lastname'] + ' ' + row['firstname'])
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        filename = row['lastname'] + '_' + row['firstname']
        report.make_doc(os.path.join(destination_path, filename) + '.doc')
        # print(user_files[idx])
        user_files_path = os.path.join(destination_path, 'приложения')
        if not os.path.exists(user_files_path):
            os.makedirs(user_files_path)
        photo_path = ''
        for n, file_row in user_files[idx].iterrows():
            if 'submission_files' not in file_row['filearea']:
                print(file_row['contenthash'], user_files_path, file_row['filename'])
                copy_user_files(file_row['contenthash'], user_files_path, file_row['filename'])
            if 'private' not in file_row['filearea'] and 'draft' in file_row['media_path'] \
                    and file_row['filename'].split('.')[-1] in ['gif', 'jpe', 'jpeg', 'jpg', 'png', 'svg', 'svgz']:
                # print('DA')
                photo_path = os.path.join(user_files_path, file_row['filename'])
        img = Image.open(photo_path)
        basewidth = 113
        basehight = 151
        # img = Image.open('somepic.jpg')
        #wpercent = (basewidth/float(img.size[0]))
        #hsize = int((float(img.size[1])*float(wpercent)))
        #img = img.resize((basewidth, basehight), Image.ANTIALIAS)
        img.thumbnail((basewidth, basehight), Image.ANTIALIAS)
        img.save(photo_path) 
        #img.thumbnail(128, Image.ANTIALIAS)
        #img.save(photo_path, "JPEG")
        # pdf
        cv.__dict__.update({'photo': photo_path})
        # print(cv.__dict__)
        output_from_parsed_template = template.render(cv.__dict__)
        with open("new_report.html", "w", encoding='utf-8') as f:
            f.write(output_from_parsed_template)
        report.make_pdf(os.path.join(destination_path, filename) + '.pdf')
