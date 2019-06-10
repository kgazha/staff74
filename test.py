import unittest
from report import get_user_cv_from_db


class TestGetReport(unittest.TestCase):
    def test_get_user_cv_from_db(self):
        user_id = 2
        cv = get_user_cv_from_db(user_id)
        true_values = {'fio': 'ПользовательАдминистратор',
                       'contacts': '880553530; I.Aksenov@mininform74.ru',
                       'date_of_birth': '802720800',
                       'citizenship': 'Россия',
                       'current_position': 'ОГБУ ЧРЦНИТ',
                       'current_activity_area': 'Поддержка moodle',
                       'current_activity_type': 'dev-ops',
                       'professional_experience': 'ayylmao',
                       'management_experience': 'более или менее',
                       'government_experience': 'присутствует',
                       'management_experience_scale': 'небольшой',
                       'awards_presence': 'да',
                       'desired_authority_and_post_level': 'мининформ',
                       'perspective_activity': '',
                       'family_status': 'Не замужем, не женат',
                       'children': 'нет',
                       'military_service': 'нет',
                       'education_level_and_direction': 'бакалавр ит',
                       'additional_education': 'не очень',
                       'rank': 'отсутствует',
                       'foreign_languages': 'казахский',
                       'hobby': 'vidiya',
                       'social_activities_experience': 'отсутствует',
                       'state_secrets_access': 'отсутствует',
                       'criminal_record': 'отсутствует',
                       'willingness_state_secrets_access': 'отсутствует'}
        self.assertEqual(true_values, cv.__dict__)
