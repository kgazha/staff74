import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
import config
from sqlalchemy.orm import sessionmaker
import pandas as pd


session = sessionmaker(bind=config.ENGINE)()


class CV:
    db_codenames = {'dateofbirth': 'date_of_birth',
                    'workplace1': 'current_position',
                    'fieldofwork': 'current_activity_area',
                    'typeofwork': 'current_activity_type',
                    'work5years': 'professional_experience',
                    'workrealmanager': 'management_experience',
                    'workgov': 'government_experience',
                    'workrealdeal': 'management_experience_scale',
                    'workwhere': 'desired_authority_and_post_level',
                    'studyplus': 'additional_education',
                    'whoisit': 'rank',
                    'englichanin': 'foreign_languages',
                    'hobby': 'hobby',
                    'volunteer': 'social_activities_experience',
                    'govsecret': 'state_secrets_access',
                    'withwho': 'family_status',
                    'govsecretready': 'willingness_state_secrets_access',
                    'ayylmao': 'criminal_record',
                    'kids': 'children',
                    'army': 'military_service',
                    'study': 'education_level_and_direction',
                    'passportofcountry': 'citizenship',
                    'nagradas': 'awards_presence'
                    }

    activity_codenames = ['ecoandnature', 'thingandearth', 'selhoz', 'dorogi',
                          'cultandtourism', 'zkh', 'zdrav', 'studyandyoung',
                          'social', 'buildings', 'infotech', 'economyandfin']

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

    def update_cv(self, codename, value):
        self.__setattr__(self.db_codenames[codename], value)


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
    perspective_activities = []
    for idx, row in df.iterrows():
        if row['shortname'] == 'phonenumber1':
            cv.contacts = row['data'] + '; ' + row['email']
        elif row['shortname'] in cv.activity_codenames:
            if row['data'] == '1':
                perspective_activities.append(row['field_name'])
        else:
            cv.update_cv(row['shortname'], row['data'])
    if perspective_activities:
        cv.perspective_activity = '; '.join(perspective_activities)
    return cv


env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report.html')
cv = get_user_cv_from_db(2)
output_from_parsed_template = template.render(cv.__dict__)
with open("new_report.html", "w", encoding='utf-8') as f:
    f.write(output_from_parsed_template)
make_pdf()
# print_doc()
