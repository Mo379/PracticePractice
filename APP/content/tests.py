import os
from django.test import TestCase
from content.util.GeneralUtil import TagGenerator
from content.util.ContentCRUD import \
        QuestionCRUD, \
        PointCRUD, \
        SpecificationCRUD
from content.util.ContentSync import \
        QuestionSync, \
        PointSync, \
        SpecificationSync, \
        VideoSync
from content.models import \
        Question, \
        Point, \
        Video, \
        Specification
from decouple import config as decouple_config


# Utility testing
class UTILITY_Tests(TestCase):
    def setUp(self):
        # Question objects
        self.Question = Question
        self.q_crud_obj = QuestionCRUD()
        self.q_sync_obj = QuestionSync()
        # Point objects
        self.Point = Point
        self.p_crud_obj = PointCRUD()
        self.p_sync_obj = PointSync()
        # Video objects
        self.Video = Video
        self.v_sync_obj = VideoSync()
        # Specificatio objects
        self.Specification = Specification
        self.s_crud_obj = SpecificationCRUD()
        self.s_sync_obj = SpecificationSync()
        # Utility objects
        self.TagGenerator = TagGenerator

    def test_TagGenerator(self):
        x = self.TagGenerator()
        self.assertEqual(len(x), 10)
        self.assertEqual(type(x), str)

    def test_crud_question(self):
        # create
        c_status = self.q_crud_obj.Create(
                'Z_test/A_test/B_test/C_test/D_test/questions'
            )
        # sync
        s_status = self.q_sync_obj.sync(subdir='Z_test/')
        # update using stock json file
        question = self.Question.objects.all()[0]
        data_dir = decouple_config('data_dir')
        test_file = os.path.join(data_dir, 'templates', 'question2.json')
        new_content = open(test_file, 'r').read()
        u_status = self.q_crud_obj.Update(
                question.q_unique_id, new_content
            )
        # read updated version
        r_status = u_check = self.q_crud_obj.Read(question.q_unique_id)
        # delete
        d_status = self.q_crud_obj.Delete(question.q_unique_id)
        # check that all of the above works correctly
        self.assertEqual(c_status, 1)
        self.assertEqual(s_status, 1)
        self.assertEqual(type(r_status), str)
        self.assertNotEqual(len(r_status), 0)
        #
        self.assertEqual(u_status, 1)
        # update specific field of the json and check
        self.assertEqual(u_check, new_content)
        # delete file and check it doesnt exist
        self.assertEqual(d_status, 1)

    def test_crud_point(self):
        # create
        c_status = self.p_crud_obj.Create(
                'Z_test/A_test/B_test/C_test/D_test'
            )
        # sync
        s_status = self.p_sync_obj.sync(subdir='Z_test/')
        # update using stock json file
        point = self.Point.objects.all()[0]
        data_dir = decouple_config('data_dir')
        test_file = os.path.join(data_dir, 'templates', 'point2.json')
        new_content = open(test_file, 'r').read()
        u_status = self.p_crud_obj.Update(
                point.p_unique_id, new_content
            )
        # read updated version
        r_status = u_check = self.p_crud_obj.Read(point.p_unique_id)
        # delete
        d_status = self.p_crud_obj.Delete(point.p_unique_id)
        # check that all of the above works correctly
        self.assertEqual(c_status, 1)
        self.assertEqual(s_status, 1)
        self.assertEqual(type(r_status), str)
        self.assertNotEqual(len(r_status), 0)
        #
        self.assertEqual(u_status, 1)
        # update specific field of the json and check
        self.assertEqual(u_check, new_content)
        # delete file and check it doesnt exist
        self.assertEqual(d_status, 1)

    def test_crud_spec(self):
        # create
        c_status = self.s_crud_obj.Create(
                'Z_test/A_test/B_test',
                'test01'
            )
        # sync
        s_status = self.s_sync_obj.sync(subdir='Z_test/')
        # update using stock json file
        spec = self.Specification.objects.all()[0]
        data_dir = decouple_config('data_dir')
        test_file = os.path.join(data_dir, 'templates', 'specification2.json')
        new_content = open(test_file, 'r').read()
        u_status = self.s_crud_obj.Update(
                spec.spec_board, spec.spec_name, new_content
            )
        # read updated version
        r_status = u_check = self.s_crud_obj.Read(
                spec.spec_board, spec.spec_name
            )
        # delete
        d_status = self.s_crud_obj.Delete(spec.spec_board, spec.spec_name)
        # check that all of the above works correctly
        self.assertEqual(c_status, 1)
        self.assertEqual(s_status, 1)
        self.assertEqual(type(r_status), str)
        self.assertNotEqual(len(r_status), 0)
        #
        self.assertEqual(u_status, 1)
        # update specific field of the json and check
        self.assertEqual(u_check, new_content)
        # delete file and check it doesnt exist
        self.assertEqual(d_status, 1)

    def test_sync_video(self):
        pass


# URL testing
class URL_pages_Tests(TestCase):
    def test_homepage(self):
        response = self.client.get('/my/')
        self.assertEqual(response.status_code, 200)

    def test_hub(self):
        response = self.client.get('/my/hub')
        self.assertEqual(response.status_code, 200)

    def test_statistics(self):
        response = self.client.get('/my/statistics')
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get('/my/content')
        self.assertEqual(response.status_code, 200)

    def test_content_questions(self):
        response = self.client.get('/my/content/questions')
        self.assertEqual(response.status_code, 200)

    def test_content_question(self):
        response = self.client.get('/my/content/question')
        self.assertEqual(response.status_code, 200)

    def test_content_notes(self):
        response = self.client.get('/my/content/notes')
        self.assertEqual(response.status_code, 200)

    def test_content_paper(self):
        response = self.client.get('/my/content/paper')
        self.assertEqual(response.status_code, 200)

    def test_content_userpaper(self):
        response = self.client.get('/my/content/user-paper')
        self.assertEqual(response.status_code, 200)

    def test_content_userpaper_print(self):
        response = self.client.get('/my/content/user-paper/print')
        self.assertEqual(response.status_code, 200)
