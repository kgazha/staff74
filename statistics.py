# -*- coding: utf-8 -*-
import config
import os.path
import xlsxwriter
import datetime
import pandas as pd
from report_sender import get_header_format, get_row_format
from sqlalchemy.orm import sessionmaker


session = sessionmaker(bind=config.ENGINE)()


class Statistics:
    def __init__(self, sql_filename, report_destination):
        self.sql_filename = sql_filename
        self.report_destination = report_destination

    def save_df_to_excel(self, df, filename):
        if not os.path.exists(self.report_destination):
            os.makedirs(self.report_destination)
        workbook = xlsxwriter.Workbook(os.path.join(self.report_destination, filename))
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

    def get_data_from_db(self):
        sql = open(self.sql_filename).read()
        sql_result = session.execute(sql)
        df = pd.DataFrame(sql_result.fetchall(), columns=sql_result.keys())
        return df

    def get_decoded_data_from_db(self):
        sql = open(self.sql_filename).read()
        sql_result = session.execute(sql)
        data = sql_result.fetchall()
        values = []
        for row in data:
            row_values = []
            for val in row:
                row_values.append(str(val).encode('cp1251').decode('utf8'))
            values.append(row_values)
        df = pd.DataFrame(values, columns=sql_result.keys())
        return df

    def data_from_db_to_excel(self, excel_filename, decoded=False):
        if decoded:
            df = self.get_decoded_data_from_db()
        else:
            df = self.get_data_from_db()
        self.save_df_to_excel(df, excel_filename)


if __name__ == '__main__':
    sql_total_statistics = 'total_statistics.sql'
    excel_total_statistics = 'Общая статистика.xlsx'
    excel_activities = 'Статистика по направлениям.xlsx'
    sql_filenames = ['activities.sql', 'all_users.sql']
    excel_filenames = ['activities.xlsx', 'all_users.xlsx']
    destination_path = os.path.join(config.STATISTICS_DIR, datetime.date.today().strftime("%d_%m_%Y"))
    reports = [Statistics(sql, config.STATISTICS_DIR) for sql in sql_filenames]
    [report.data_from_db_to_excel(excel_filenames[idx]) for idx, report in enumerate(reports)]
    reports[0].report_destination = destination_path
    reports[0].data_from_db_to_excel(excel_activities)
    total_statistics = Statistics(sql_total_statistics, destination_path)
    total_statistics.data_from_db_to_excel(excel_total_statistics, decoded=True)
