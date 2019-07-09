# -*- coding: utf-8 -*-
import config
import os.path
import xlsxwriter
import datetime
import pandas as pd
from report_sender import get_header_format, get_row_format
from sqlalchemy.orm import sessionmaker


session = sessionmaker(bind=config.ENGINE)()


def save_to_excel(df, filename):
    folder_path = os.path.join(config.STATISTICS_DIR)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    workbook = xlsxwriter.Workbook(os.path.join(folder_path, filename))
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, len(df.keys()), 20)
    header_format = get_header_format(workbook)
    row_format = get_row_format(workbook)
    for idx, key in enumerate(df.keys()):
        worksheet.write(0, idx, key, header_format)
    for idx, (n_data, data) in enumerate(df.iterrows()):
        for col_idx, (key, value) in enumerate(data.items()):
            worksheet.write(idx + 1, col_idx, value, row_format)
    workbook.close()


def save_report(report_name):
    activities_sql = open(report_name + '.sql').read()
    activities = session.execute(activities_sql)
    df_activities = pd.DataFrame(activities.fetchall(), columns=activities.keys())
    filename = report_name + '.xlsx'
    save_to_excel(df_activities, filename)


def save_total_statistics():
    total_statistics_sql = open('total_statistics.sql').read()
    total_statistics = session.execute(total_statistics_sql)
    data = total_statistics.fetchall()
    values = []
    for row in data:
        row_values = []
        for val in row:
            row_values.append(str(val).encode('cp1251').decode('utf8'))
        values.append(row_values)
    df = pd.DataFrame(values, columns=total_statistics.keys())
    path = os.path.join(config.STATISTICS_DIR, datetime.date.today().strftime("%d_%m_%Y"))
    if not os.path.exists(path):
        os.mkdir(path)
    save_to_excel(df, os.path.join(datetime.date.today().strftime("%d_%m_%Y"), 'Общая статистика.xlsx'))


reports = ['activities', 'all_users']
[save_report(r) for r in reports]
save_total_statistics()
