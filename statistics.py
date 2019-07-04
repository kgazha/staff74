# -*- coding: utf-8 -*-
import config
import os.path
import xlsxwriter
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


reports = ['activities', 'all_users']
[save_report(r) for r in reports]
