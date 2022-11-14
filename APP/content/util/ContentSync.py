import os
import json
from decouple import config as decouple_config
from content.models import Question, Point, Video, Specification
from django.conf import settings
from collections import defaultdict
from io import BytesIO






# models with smart features
class QuestionSync():
    # init
    def __init__(self, content_dir=decouple_config('CND_content_dir')):
        self.content_dir = content_dir

    # sync
    def sync(self, subdir=''):
        """
        Synchronises all of the questions in the files data into the database
        """
        # getting all the question files
        structure = defaultdict(list)
        response = settings.AWS_S3_C.list_objects_v2(
            Bucket=settings.AWS_BUCKET_NAME,
            Prefix=self.content_dir,
        )
        while True:
            if "NextContinuationToken" in response:
                token = response["NextContinuationToken"]
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if 'type_question' in file and '/bin/' not in directory:
                        structure[directory].append(file)
                    else:
                        pass
                response = settings.AWS_S3_C.list_objects_v2(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Prefix=self.content_dir,
                    ContinuationToken=token
                )
            else:
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if 'type_question' in file and '/bin/' not in directory:
                        structure[directory].append(file)
                    else:
                        pass
                break
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
            f = BytesIO()
            settings.AWS_S3_C.download_fileobj(settings.AWS_BUCKET_NAME, q_link, f)
            content = f.getvalue()
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


class PointSync():
    # Init
    def __init__(self, content_dir=decouple_config('CND_content_dir')):
        self.content_dir = content_dir

    # sync
    def sync(self, subdir=''):
        """
        Synchronises all of the points in the files data into the database
        """
        # getting all the question files
        structure = defaultdict(list)
        response = settings.AWS_S3_C.list_objects_v2(
            Bucket=settings.AWS_BUCKET_NAME,
            Prefix=self.content_dir,
        )
        while True:
            if "NextContinuationToken" in response:
                token = response["NextContinuationToken"]
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if 'type_point' in file and '/bin/' not in directory:
                        structure[directory].append(file)
                    else:
                        pass
                response = settings.AWS_S3_C.list_objects_v2(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Prefix=self.content_dir,
                    ContinuationToken=token
                )
            else:
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if 'type_point' in file and '/bin/' not in directory:
                        structure[directory].append(file)
                    else:
                        pass
                break
        # getting all the question information
        for ddir, point in structure.items():
            # getting source information from name
            p_level = ddir.split('/Z_')[1].split('/')[0]
            p_subject = ddir.split('/A_')[1].split('/')[0]
            p_moduel = ddir.split('/B_')[1].split('/')[0]
            p_chapter = ddir.split('/C_')[1].split('/')[0]
            p_topic = ddir.split('/D_')[1].split('/')[0]
            p_number = int(ddir.split('/N_')[1].split('/')[0])
            #
            p_dir = ddir
            p_files_dir = ddir+'/files'
            p_unique_id = point[0].split('tag_')[1].split('.')[0]
            # getting json file data
            p_link = ddir + '/' + point[0]
            f = BytesIO()
            settings.AWS_S3_C.download_fileobj(
                    settings.AWS_BUCKET_NAME, p_link, f
                )
            content = f.getvalue()
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
            my_point.p_number = p_number
            my_point.p_content = p_content
            my_point.p_directory = p_dir
            my_point.p_link = p_link
            my_point.p_unique_id = p_unique_id
            my_point.save()
        return 1


# Video Sync
class VideoSync():
    # init
    def __init__(self, content_dir=decouple_config('CND_content_dir')):
        self.content_dir = content_dir

    # sync
    def sync(self, subdir=''):
        """
        Synchronises all of the videos in the files (points) data
        into the database
        """
        # getting all the points files
        structure = defaultdict(list)
        response = settings.AWS_S3_C.list_objects_v2(
            Bucket=settings.AWS_BUCKET_NAME,
            Prefix=self.content_dir,
        )
        while True:
            if "NextContinuationToken" in response:
                token = response["NextContinuationToken"]
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if 'type_point' in file and '/bin/' not in directory:
                        structure[directory].append(file)
                    else:
                        pass
                response = settings.AWS_S3_C.list_objects_v2(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Prefix=self.content_dir,
                    ContinuationToken=token
                )
            else:
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if 'type_point' in file and '/bin/' not in directory:
                        structure[directory].append(file)
                    else:
                        pass
                break
        # getting all the points information
        for ddir, point in structure.items():
            p_unique_id = point[0].split('tag_')[1].split('.')[0]
            p_link = ddir + '/' + point[0]
            f = BytesIO()
            settings.AWS_S3_C.download_fileobj(settings.AWS_BUCKET_NAME, p_link, f)
            content = f.getvalue()
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
    def __init__(self, content_dir=decouple_config('CND_specifications_dir')):
        self.content_dir = content_dir

    # Sync
    def sync(self, subdir=''):
        """
        Synchronises all of the specs in the files data into the database
        """
        # getting all the question files
        structure = defaultdict(list)
        response = settings.AWS_S3_C.list_objects_v2(
            Bucket=settings.AWS_BUCKET_NAME,
            Prefix=self.content_dir,
        )
        while True:
            if "NextContinuationToken" in response:
                token = response["NextContinuationToken"]
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if('.json' in file):
                        structure[directory].append(file)
                    else:
                        pass
                response = settings.AWS_S3_C.list_objects_v2(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Prefix=self.content_dir,
                    ContinuationToken=token
                )
            else:
                for item in response['Contents']:
                    parts = item['Key'].split('/')
                    directory = ('/').join(parts[:-1])
                    file = parts[-1]
                    if('.json' in file):
                        structure[directory].append(file)
                    else:
                        pass
                break
        # getting all the question information
        for ddir, specs in structure.items():
            for spec in specs:
                # getting source information from name
                spec_level = ddir.split('/Z_')[1].split('/')[0]
                spec_subject = ddir.split('/A_')[1].split('/')[0]
                if '/B_' in ddir:
                    spec_board = ddir.split('/B_')[1].split('/')[0]
                else:
                    spec_board = 'Universal'
                #
                spec_dir = ddir
                spec_name = spec.split('.')[0]
                # getting json file data
                spec_link = ddir + '/' + spec
                f = BytesIO()
                settings.AWS_S3_C.download_fileobj(settings.AWS_BUCKET_NAME, spec_link, f)
                content = f.getvalue()
                try:
                    data = json.loads(content)
                except Exception:
                    data = {}
                # extracting info from json file data
                spec_content = data
                # Load question information to model
                if Specification.objects.filter(
                        spec_level=spec_level,
                        spec_subject=spec_subject,
                        spec_board=spec_board,
                        spec_name=spec_name
                    ):
                    my_spec = Specification.objects.get(
                        spec_level=spec_level,
                        spec_subject=spec_subject,
                        spec_board=spec_board,
                        spec_name=spec_name
                        )
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
