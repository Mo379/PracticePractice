import os
import json
from decouple import config as decouple_config
from ..models import Question, Point, Video, Specification


# left to figure out how to insert the extracted information into the 
# models with smart features
class QuestionSync():
    # init
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir

    # sync
    def sync(self, subdir=''):
        """
        Synchronises all of the questions in the files data into the database
        """
        # getting all the question files
        structure = {}
        for root, dirs, files in \
                os.walk(os.path.join(self.content_dir, subdir), topdown=False):
            for file in files:
                if('type_question' in file):
                    files = [s for s in files if "type_question" in s]
                    structure[root] = files
                    continue
        # getting all the question information
        for ddir, question in structure.items():
            # getting source information from name
            q_level = ddir.split('/Z_')[1].split('/')[0]
            q_subject = ddir.split('/A_')[1].split('/')[0]
            q_moduel = ddir.split('/B_')[1].split('/')[0]
            q_chapter = ddir.split('/C_')[1].split('/')[0]
            try:
                q_topic = ddir.split('/D_')[1].split('/')[0] 
            except Exception:
                q_topic = ''
            q_dir = ddir
            q_files_dir = ddir+'/files'
            q_unique_id = ddir.split('/')[-1]
            # getting json file data
            q_link = ddir + '/' + question[0]
            with open(q_link, 'r') as file:
                content = file.read()
            data = json.loads(content)
            # extracting info from json file data
            q_content = data
            q_difficulty = data['details']['head']['0']['q_difficulty']
            q_board = data['details']['head']['0']['q_board']
            q_board_moduel = data['details']['head']['0']['q_moduel']
            q_exam_month = data['details']['head']['0']['q_month']
            q_exam_year = data['details']['head']['0']['q_year']
            q_exam_number = data['details']['head']['0']['q_number']
            q_type = data['details']['head']['0']['q_type']
            # Load question information to model
            if Question.objects.filter(q_unique_id=q_unique_id):
                my_question = Question.objects.get(q_unique_id=q_unique_id)
            else:
                my_question = Question()
            my_question.q_level = q_level
            my_question.q_board = q_board
            my_question.q_board_moduel = q_board_moduel
            my_question.q_exam_month = \
                q_exam_month if q_exam_month != '' else 0
            my_question.q_exam_year = q_exam_year if q_exam_year != '' else 0 
            my_question.q_is_exam = bool(q_exam_number)
            my_question.q_exam_num = \
                q_exam_number if q_exam_number != '' else 0
            my_question.q_subject = q_subject
            my_question.q_moduel = q_moduel
            my_question.q_chapter = q_chapter
            my_question.q_topic = q_topic
            my_question.q_type = q_type
            my_question.q_difficulty = q_difficulty
            my_question.q_total_marks = 0
            my_question.q_content = q_content
            my_question.q_dir = q_dir
            my_question.q_link = q_link
            my_question.q_unique_id = q_unique_id
            my_question.save()
        return 1


# Point sync
class PointSync():
    # Init
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir

    # sync
    def sync(self, subdir=''):
        """
        Synchronises all of the points in the files data into the database
        """
        # getting all the question files
        structure = {}
        for root, dirs, files in \
                os.walk(os.path.join(self.content_dir, subdir), topdown=False):
            for file in files:
                if('type_point' in file):
                    files = [s for s in files if "type_point" in s]
                    structure[root] = files
                    continue
        # getting all the question information
        for ddir, point in structure.items():
            # getting source information from name
            p_level = ddir.split('/Z_')[1].split('/')[0]
            p_subject = ddir.split('/A_')[1].split('/')[0]
            p_moduel = ddir.split('/B_')[1].split('/')[0]
            p_chapter = ddir.split('/C_')[1].split('/')[0]
            p_topic = ddir.split('/D_')[1].split('/')[0] 
            #
            p_dir = ddir
            p_files_dir = ddir+'/files'
            p_unique_id = point[0].split('tag_')[1].split('.')[0]
            # getting json file data
            p_link = ddir + '/' + point[0]
            with open(p_link, 'r') as file:
                content = file.read()
            data = json.loads(content)
            # extracting info from json file data
            p_content = data
            # Load question information to model
            if Point.objects.filter(p_unique_id=p_unique_id):
                my_point = Point.objects.get(p_unique_id=p_unique_id)
            else:
                my_point = Point()
            my_point.p_level = p_level
            my_point.p_subject = p_subject
            my_point.p_moduel = p_moduel
            my_point.p_chapter = p_chapter
            my_point.p_topic = p_topic
            my_point.p_content = p_content
            my_point.p_directory = p_dir
            my_point.p_link = p_link
            my_point.p_unique_id = p_unique_id
            my_point.save()
        return 1


# Video Sync
class VideoSync():
    # init
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir

    # sync
    def sync(self, subdir=''):
        """
        Synchronises all of the points in the files data into the database
        """
        # getting all the question files
        structure = {}
        for root, dirs, files in \
            os.walk(os.path.join(self.content_dir, subdir), topdown=False):
            for file in files:
                if('type_point' in file):
                    files = [s for s in files if "type_point" in s]
                    structure[root] = files
                    continue
        # getting all the question information
        for ddir, point in structure.items():
            p_unique_id = point[0].split('tag_')[1].split('.')[0]
            p_link = ddir + '/' + point[0]
            with open(p_link, 'r') as file:
                content = file.read()
            data = json.loads(content)
            point_content = data['details']['hidden']['0']['content']
            for pos, item in point_content.items():
                pos = int(pos)
                if item['vid']:
                    video = item['vid']
                    v_pos = pos
                    v_title = video['vid_title']
                    v_link = video['vid_link']
                    if v_link:
                        if Video.objects.filter(
                                p_unique_id=p_unique_id, v_pos=v_pos
                            ):
                            my_vid = Video.objects.get(
                                    p_unique_id=p_unique_id, v_pos=v_pos
                                )
                        else:
                            my_vid = Video()
                        my_vid.p_unique_id = p_unique_id
                        my_vid.v_title = v_title
                        my_vid.v_link = v_link
                        my_vid.v_pos = v_pos
                        my_vid.save()
        return 1


# Specification
class SpecificationSync():
    # init
    def __init__(self, content_dir=decouple_config('specifications_dir')):
        self.content_dir = content_dir

    # Sync
    def sync(self, subdir=''):
        """
        Synchronises all of the specs in the files data into the database
        """
        # getting all the question files
        structure = {}
        for root, dirs, files in \
                os.walk(os.path.join(self.content_dir, subdir), topdown=False):
            for file in files:
                if('.json' in file):
                    files = [s for s in files if ".json" in s]
                    structure[root] = files
        # getting all the question information
        for ddir, specs in structure.items():
            for spec in specs:
                # getting source information from name
                spec_level = ddir.split('/Z_')[1].split('/')[0]
                spec_subject = ddir.split('/A_')[1].split('/')[0]
                spec_board = ddir.split('/B_')[1].split('/')[0]
                #
                spec_dir = ddir
                spec_name = spec.split('.')[0]
                # getting json file data
                spec_link = ddir + '/' + spec
                with open(spec_link, 'r') as file:
                    content = file.read()
                try:
                    data = json.loads(content)
                except Exception:
                    data = {}
                # extracting info from json file data
                spec_content = data
                # Load question information to model
                if Specification.objects.filter(spec_name=spec_name):
                    my_spec = Specification.objects.get(spec_name=spec_name)
                else:
                    my_spec = Specification()
                my_spec.spec_level = spec_level
                my_spec.spec_subject = spec_subject
                my_spec.spec_board = spec_board
                my_spec.spec_name = spec_name
                my_spec.spec_content = spec_content
                my_spec.spec_dir = spec_dir
                my_spec.spec_link = spec_link
                my_spec.save()
        return 1
