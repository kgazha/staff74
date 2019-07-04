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
from detect import detect_image


session = sessionmaker(bind=config.ENGINE)()
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


env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report.html')
template_doc = env.get_template('report_doc.html')


class User:
    def __init__(self, userid=None, video_url=None, username=None, lastname=None,
                 firstname=None, patronymic=None, email=None, city=None):
        self.userid = userid
        self.video_url = video_url
        self.username = username
        self.lastname = lastname
        self.firstname = firstname
        self.patronymic = patronymic
        self.email = email
        self.city = city
        self.firstaccess = None
        self.confirmed = 0
        self._percents = 0
        self.test_completed = 0
        self.grades = []
        self.files = []

    @property
    def percents(self):
        return self._percents

    @percents.setter
    def percents(self, value):
        self._percents = int(value)

    def __str__(self):
        return ' '.join([self.lastname, self.firstname, self.patronymic])

    def __repr__(self):
        return 'user_' + str(self.userid)

    def get_user_main_info(self):
        user_info_sql = open('main_user_info.sql').read()
        user_info = session.execute(user_info_sql.format(self.userid))
        df_user_info = pd.DataFrame(user_info.fetchall(), columns=user_info.keys())
        for idx, row in df_user_info.iterrows():
            for key in row.keys():
                self.__setattr__(key, row[key])

    def get_user_files(self):
        user_files_sql = open('user_files.sql').read()
        files = session.execute(user_files_sql.format(self.userid))
        df_user_files = pd.DataFrame(files.fetchall(), columns=files.keys())
        for idx, row in df_user_files.iterrows():
            file = File()
            for key in row.keys():
                file.__setattr__(key, row[key])
            self.files.append(file)

    def get_user_video_presentation(self):
        if not self.files:
            self.get_user_files()
        for file_obj in self.files:
            if 'submission_files' in file_obj.filearea:
                self.video_url = '/'.join([url, str(file_obj.itemid), file_obj.filename])

    def get_test_results(self):
        user_test_results_sql = open('user_test_results.sql').read()
        results = session.execute(user_test_results_sql.format(self.userid))
        df_user_test_results = pd.DataFrame(results.fetchall(), columns=results.keys())
        for idx, val in df_user_test_results.iterrows():
            self.grades.append(int(val))

    def get_user_info(self):
        self.get_user_main_info()
        self.get_user_rest_info()

    def get_user_rest_info(self):
        self.get_user_files()
        self.get_user_video_presentation()
        self.get_test_results()


class File:
    def __init__(self, contenthash=None, media_path=None, filearea=None,
                 filename=None, itemid=None):
        self.contenthash = contenthash
        self.media_path = media_path
        self.filearea = filearea
        self.filename = filename
        self._itemid = itemid

    @property
    def itemid(self):
        return self._itemid

    @itemid.setter
    def itemid(self, value):
        if not pd.isnull(value):
            self._itemid = int(value)

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename


class Report:
    @staticmethod
    def get_successful_users():
        successful_users = []
        completed_tests_sql = open('completed_tests.sql').read()
        completed_tests = session.execute(completed_tests_sql)
        df = pd.DataFrame(completed_tests.fetchall(), columns=completed_tests.keys())
        for idx, row in df.iterrows():
            user = User()
            for key in row.keys():
                user.__setattr__(key, row[key])
            successful_users.append(user)
        return successful_users

    @staticmethod
    def get_new_successful_users():
        successful_users = Report.get_successful_users()
        processed_user_ids = Report.get_processed_user_ids()
        new_successful_users = []
        if not processed_user_ids:
            new_successful_users = successful_users
        else:
            for user in successful_users:
                if user.userid not in processed_user_ids:
                    new_successful_users.append(user)
        return new_successful_users

    @staticmethod
    def get_processed_user_ids():
        if os.path.isfile(config.PROCESSED_USERS):
            with open(config.PROCESSED_USERS, 'rb') as file:
                unpickler = pickle.Unpickler(file)
                return unpickler.load()

    @staticmethod
    def save_processed_user_ids(processed_user_ids):
        processed_user_ids += Report.get_processed_user_ids()
        with open(config.PROCESSED_USERS, 'wb') as file:
            pickle.dump(processed_user_ids, file)

    @staticmethod
    def _get_user_row(user):
        row = pd.Series()
        row['ФИО'] = user.lastname + ' ' + user.firstname + ' ' + user.patronymic
        row['E-mail'] = user.email
        row['Ссылка на видео'] = user.video_url
        row['Оценка видео'] = ''
        row['Оценка резюме'] = ''
        row['Средняя оценка за тесты (в процентах)'] = user.percents
        row['Оценка за первый тест'] = user.grades[0]
        row['Оценка за второй тест'] = user.grades[1]
        row['Оценка за третий тест'] = user.grades[2]
        row['Оценка за четвертый тест'] = user.grades[3]
        row['Оценка за пятый тест'] = user.grades[4]
        return row

    @staticmethod
    def get_report_form(users):
        rows = [Report._get_user_row(user) for user in users]
        report_form = pd.DataFrame(rows)
        return report_form

    @staticmethod
    def form_to_excel(form):
        file_name = 'Отчёт' + datetime.datetime.today().strftime("_%H_%M") + '.xlsx'
        folder_path = os.path.join(config.BASE_DIR, datetime.date.today().strftime("%d_%m_%Y"))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        workbook = xlsxwriter.Workbook(os.path.join(folder_path, file_name))
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, len(form.keys()), 20)
        header_format = get_header_format(workbook)
        row_format = get_row_format(workbook)
        for idx, key in enumerate(form.keys()):
            worksheet.write(0, idx, key, header_format)
        for idx, (n_data, data) in enumerate(form.iterrows()):
            for col_idx, (key, value) in enumerate(data.items()):
                worksheet.write(idx + 1, col_idx, value, row_format)
        workbook.close()


class UserContent:
    def __init__(self, user):
        self.user = user
        self.cv = report.get_user_cv_from_db(user.userid)
        self.applications_folder_name = 'приложения'
        self.filename = user.lastname + '_' + user.firstname
        self.destination_path = self.__get_destination_path()
        self.user_files_path = self.__get_user_files_path()

    def __get_destination_path(self):
        destination_path = os.path.join(get_actual_report_folder(),
                                        self.user.lastname + '_' + self.user.firstname)
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        else:
            while os.path.exists(destination_path):
                destination_path += ' ' + str(self.user.userid)
            os.makedirs(destination_path)
        return destination_path

    def __get_user_files_path(self):
        user_files_path = os.path.join(self.destination_path, self.applications_folder_name)
        if not os.path.exists(user_files_path):
            os.makedirs(user_files_path)
        return user_files_path

    def get_photo_path(self):
        photo_path = ''
        for file in self.user.files:
            if 'submission_files' not in file.filearea:
                copy_user_files(file.contenthash, self.user_files_path, file.filename)
            if 'private' not in file.filearea and 'draft' in file.media_path \
                    and file.filename.split('.')[-1] in ['gif', 'jpe', 'jpeg', 'jpg', 'png', 'svg', 'svgz']:
                photo_path = os.path.join(self.user_files_path, file.filename)
        if not photo_path:
            profile_photo_template = get_profile_photo_template(self.user_files_path, self.user.userid)
            if not profile_photo_template:
                return photo_path
            detected_photo = get_profile_photo_filename(self.user_files_path, profile_photo_template)
            photo_path = os.path.join(self.user_files_path, detected_photo)
        else:
            img = Image.open(photo_path)
            basewidth = 113
            basehight = 151
            img.thumbnail((basewidth, basehight), Image.ANTIALIAS)
            image_filename = '.'.join(photo_path.split('.')[:-1]) + '_cv' + '.' + photo_path.split('.')[-1]
            img.save(image_filename)
        return photo_path

    def cv_to_doc(self):
        output_from_parsed_template_doc = template_doc.render(self.cv.__dict__)
        with open("new_report_doc.html", "w", encoding='utf-8') as file:
            file.write(output_from_parsed_template_doc)
        report.make_doc(os.path.join(self.destination_path, self.filename) + '.doc')

    def cv_to_pdf(self):
        photo_path = self.get_photo_path()
        self.cv.__dict__.update({'photo': photo_path})
        output_from_parsed_template = template.render(self.cv.__dict__)
        with open("new_report.html", "w", encoding='utf-8') as f:
            f.write(output_from_parsed_template)
        report.make_pdf(os.path.join(self.destination_path, self.filename) + '.pdf')

    def copy_user_file(self, file):
        repository_types = ['video', 'scan']
        for repository_type in repository_types:
            path = os.path.join(config.MOODLEDATA_DIR,
                                repository_type,
                                file.contenthash[:2],
                                file.contenthash[2:4],
                                file.contenthash)
            if os.path.exists(path):
                copyfile(path, os.path.join(self.user_files_path, file.filename))

    def copy_user_files(self):
        for file in self.user.files:
            if 'submission_files' not in file.filearea:
                self.copy_user_file(file)


def get_user_data(userid):
    user = User(userid=userid)
    user.get_user_info()
    content = UserContent(user)
    content.copy_user_files()
    content.cv_to_pdf()


if __name__ == '__main__':
    # get_user_data(461)
    r = Report()
    users = r.get_new_successful_users()
    if users:
        [user.get_user_info() for user in users]
        form = Report.get_report_form(users)
        Report.form_to_excel(form)
        for user in users:
            uc = UserContent(user)
            uc.copy_user_files()
            uc.cv_to_doc()
            uc.cv_to_pdf()
        processed_user_ids = [user.userid for user in users]
        r.save_processed_user_ids(processed_user_ids)
