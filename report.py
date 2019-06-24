import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
import config
from sqlalchemy.orm import sessionmaker
import pandas as pd
import win32com.client


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
                    'nagradas': 'awards_presence',
                    'otchestvo': 'patronymic'
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
    configuration = pdfkit.configuration(wkhtmltopdf=config.PATH_WKTHMLTOPDF)
    pdfkit.from_file(os.path.join(os.path.curdir, "new_report.html"), name, configuration=configuration)


def make_doc(name="out.doc"):
    word = win32com.client.Dispatch('Word.Application')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    doc = word.Documents.Add(os.path.join(current_dir, 'new_report.html'))
    doc.SaveAs(os.path.join(current_dir, name), FileFormat=0)
    doc.Close()
    word.Quit()


def print_doc(name="out.pdf"):
    os.startfile(name, "print")


def get_user_cv_from_db(username):
    with open('cv_info.sql', 'r') as f:
        query = f.read()
    df = pd.DataFrame(session.execute(query.format(username)).fetchall(),
                      columns=['username', 'firstname', 'lastname', 'email',
                               'icq', 'skype', 'institution', 'department',
                               'address', 'city', 'description', 'middlename',
                               'alternatename', 'shortname', 'field_name', 'data'])
    cv = CV()
    cv.fio = df.T[0]['lastname'] + ' ' + df.T[0]['firstname']
    perspective_activities = []
    for idx, row in df.iterrows():
        if row['shortname'] == 'phonenumber1':
            cv.contacts = row['data'] + '; ' + row['email']
        elif row['shortname'] == 'otchestvo':
            cv.fio += ' ' + row['data']
        elif row['shortname'] in cv.activity_codenames:
            if row['data'] == '1':
                perspective_activities.append(row['field_name'])
        else:
            cv.update_cv(row['shortname'], row['data'])
    if perspective_activities:
        cv.perspective_activity = '; '.join(perspective_activities)
    return cv


if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report.html')
    cv = get_user_cv_from_db('suadmin')
    output_from_parsed_template = template.render(cv.__dict__)
    with open("new_report.html", "w", encoding='utf-8') as f:
        f.write(output_from_parsed_template)
    # make_pdf()
    # make_doc()
    # print_doc()
