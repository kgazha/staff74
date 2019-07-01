# -*- coding: utf-8 -*-
import config
import os.path
from os import listdir
from os.path import isfile, join
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
from detect import detect_image


session = sessionmaker(bind=config.ENGINE)()
completed_tests_sql = open('completed_tests.sql').read()
completed_tests = session.execute(completed_tests_sql)
df = pd.DataFrame(completed_tests.fetchall(), columns=completed_tests.keys())
sent_cvs = []
# url = 'https://команда74.рф/konkurs/pluginfile.php'
url = 'https://команда74.рф/konkurs/pluginfile.php/49/assignsubmission_file/submission_files'


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
    form['ФИО'] = form['lastname'] + ' ' + form['firstname'] + ' ' + form['patronymic']
    form['E-mail'] = form['email']
    # form['Ссылка на видео'] = url + '/' + form['media_path']
    form['Ссылка на видео'] = form['video_url']
    form['Оценка видео'] = ''
    form['Оценка резюме'] = ''
    form['Средняя оценка за тесты (в процентах)'] = form['percents']
    form['Оценка за первый тест'] = form['grade_0']
    form['Оценка за второй тест'] = form['grade_1']
    form['Оценка за третий тест'] = form['grade_2']
    form['Оценка за четвертый тест'] = form['grade_3']
    form['Оценка за пятый тест'] = form['grade_4']
    form = form.drop(['username', 'firstname', 'lastname', 'percents', 'test_complited', 'patronymic',
                      'email', 'userid', 'video_url', 'grade_0', 'grade_1', 'grade_2', 'grade_3', 'grade_4'], axis=1)
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


def get_profile_photo_template(user_files_path, userid):
    filename = ''
    user_info_sql = """select contenthash, filename from mdl_files where 
                       id in (select picture from mdl_user
                       where id = '{0}')"""
    data = session.execute(user_info_sql.format(userid)).fetchall()
    if data:
        contenthash = data[0][0]
        filename = data[0][1]
        copy_user_files(contenthash, user_files_path, filename)
    return filename


def get_profile_photo_filename(user_files_path, template_filename):
    files = []
    for f in listdir(user_files_path):
        if isfile(join(user_files_path, f)) \
                and f.lower().split('.')[-1] in ['gif', 'jpe', 'jpeg', 'jpg', 'png', 'svg', 'svgz'] \
                and f.lower() != template_filename.lower():
            files.append(f)
    for file in files:
        result = detect_image(os.path.join(user_files_path, file),
                              os.path.join(user_files_path, template_filename))
        if result:
            return file
    return None


if os.path.isfile(config.SENT_CVS):
    with open(config.SENT_CVS, 'rb') as f:
        unpickler = pickle.Unpickler(f)
        sent_cvs = unpickler.load()

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report.html')
template_doc = env.get_template('report_doc.html')
rows = []
for idx, row in df.iterrows():
    # if row['userid'] not in sent_cvs:
        rows.append(row)
        sent_cvs.append(row['userid'])


with open(config.SENT_CVS, 'wb') as f:
    pickle.dump(sent_cvs, f)

if rows:
    user_files = []
    for row in rows:
        user_files_sql = open('user_files.sql').read()
        files = session.execute(user_files_sql.format(row['userid']))
        df_user_files = pd.DataFrame(files.fetchall(), columns=files.keys())
        user_files.append(df_user_files)
        for idx, file_row in df_user_files.iterrows():
            if 'submission_files' in file_row['filearea']:
                row['video_url'] = '/'.join([url, str(file_row['itemid']), file_row['filename']])
        # add marks for tests
        user_test_results_sql = open('user_test_results.sql').read()
        results = session.execute(user_test_results_sql.format(row['userid']))
        df_user_test_results = pd.DataFrame(results.fetchall(), columns=results.keys())
        for idx, val in df_user_test_results.iterrows():
            row['grade_' + str(idx)] = val

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
        user_files_path = os.path.join(destination_path, 'приложения')
        if not os.path.exists(user_files_path):
            os.makedirs(user_files_path)
        photo_path = ''
        for n, file_row in user_files[idx].iterrows():
            if 'submission_files' not in file_row['filearea']:
                # print(file_row['contenthash'], user_files_path, file_row['filename'])
                copy_user_files(file_row['contenthash'], user_files_path, file_row['filename'])
            if 'private' not in file_row['filearea'] and 'draft' in file_row['media_path'] \
                    and file_row['filename'].split('.')[-1] in ['gif', 'jpe', 'jpeg', 'jpg', 'png', 'svg', 'svgz']:
                photo_path = os.path.join(user_files_path, file_row['filename'])
        if not photo_path:
            profile_photo_template = get_profile_photo_template(user_files_path, row['userid'])
            detected_photo = get_profile_photo_filename(user_files_path, profile_photo_template)
            photo_path = os.path.join(user_files_path, detected_photo)
        else:
            img = Image.open(photo_path)
            basewidth = 113
            basehight = 151
            img.thumbnail((basewidth, basehight), Image.ANTIALIAS)
            image_filename = '.'.join(photo_path.split('.')[:-1]) + '_cv' + '.' + photo_path.split('.')[-1]
            img.save(image_filename)
        # pdf
        cv.__dict__.update({'photo': photo_path})
        output_from_parsed_template = template.render(cv.__dict__)
        with open("new_report.html", "w", encoding='utf-8') as f:
            f.write(output_from_parsed_template)
        report.make_pdf(os.path.join(destination_path, filename) + '.pdf')
