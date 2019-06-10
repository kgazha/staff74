import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
import config
from sqlalchemy.orm import sessionmaker
import pandas as pd


session = sessionmaker(bind=config.ENGINE)()


class CV:
    def __init__(self):
        self.fio = ''
        self.contacts = ''
        self.date_of_birth = ''
        self.citizenship = ''
        self.current_position = ''
        self.current_activity_area = ''
        self.current_activity_type = ''
        self.professional_experience = ''
        self.management_experience = ''
        self.government_experience = ''
        self.management_experience_scale = ''
        self.awards_presence = ''
        self.desired_authority_and_post_level = ''
        self.perspective_activity = ''
        self.family_status = ''
        self.children = ''
        self.military_service = ''
        self.education_level_and_direction = ''
        self.additional_education = ''
        self.rank = ''
        self.foreign_languages = ''
        self.hobby = ''
        self.social_activities_experience = ''
        self.state_secrets_access = ''
        self.criminal_record = ''


def make_pdf(name="out.pdf"):
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    configuration = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    pdfkit.from_file("C:\\projects\\team74\\new_report.html", name, configuration=configuration)


def print_doc(name="out.pdf"):
    os.startfile(name, "print")


def get_user_cv_from_db(user_id):
    with open('cv_info.sql', 'r') as f:
        query = f.read()
    df = pd.DataFrame(session.execute(query.format(user_id)).fetchall(),
                      columns=['username', 'firstname', 'lastname', 'email',
                               'icq', 'skype', 'institution', 'department',
                               'address', 'city', 'description', 'middlename',
                               'alternatename', 'shortname', 'field_name', 'data'])
    cv = CV()
    cv.fio = df.T[0]['lastname'] + df.T[0]['firstname']
    for idx, row in df.iterrows():
        if row['shortname'] == 'phonenumber1':
            cv.contacts = row['data'] + '; ' + row['email']
        if row['shortname'] == 'dateofbirth':
            cv.date_of_birth = row['data']
        if row['shortname'] == 'workplace1':
            cv.current_position = row['data']
        if row['shortname'] == 'fieldofwork':
            cv.current_activity_area = row['data']
        if row['shortname'] == 'typeofwork':
            cv.current_activity_type = row['data']
        if row['shortname'] == 'work5years':
            cv.professional_experience = row['data']
        if row['shortname'] == 'workrealmanager':
            cv.management_experience = row['data']
        if row['shortname'] == 'workgov':
            cv.government_experience = row['data']
        if row['shortname'] == 'workrealdeal':
            cv.management_experience_scale = row['data']
        if row['shortname'] == 'workwhere':
            cv.desired_authority_and_post_level = row['data']
        if row['shortname'] == 'studyplus':
            cv.additional_education = row['data']
        if row['shortname'] == 'whoisit':
            cv.rank = row['data']
        if row['shortname'] == 'englichanin':
            cv.foreign_languages = row['data']
        if row['shortname'] == 'hobby':
            cv.hobby = row['data']
        if row['shortname'] == 'volunteer':
            cv.social_activities_experience = row['data']
        if row['shortname'] == 'govsecret':
            cv.state_secrets_access = row['data']
        if row['shortname'] == 'withwho':
            cv.family_status = row['data']
        if row['shortname'] == 'govsecretready':
            cv.willingness_state_secrets_access = row['data']
        if row['shortname'] == 'ayylmao':
            cv.criminal_record = row['data']
        if row['shortname'] == 'kids':
            cv.children = row['data']
        if row['shortname'] == 'army':
            cv.military_service = row['data']
        if row['shortname'] == 'study':
            cv.education_level_and_direction = row['data']
        if row['shortname'] == 'passportofcountry':
            cv.citizenship = row['data']
        if row['shortname'] == 'nagradas':
            cv.awards_presence = row['data']
    return cv


env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report.html')
cv = get_user_cv_from_db(2)
output_from_parsed_template = template.render(cv.__dict__)
with open("new_report.html", "w", encoding='utf-8') as f:
    f.write(output_from_parsed_template)
make_pdf()
