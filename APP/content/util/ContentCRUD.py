import os
import shutil
import glob
import json
from decouple import config as decouple_config
from django.shortcuts import get_object_or_404
from ..models import Question, Point, Specification
from .GeneralUtil import TagGenerator


# Crut question
class QuestionCRUD():

    # init
    def __init__(self):
        self.data_dir = decouple_config('data_dir')
        self.content_dir = decouple_config('content_dir')

    # check link pattern
    def _check_short_link(self, short_link):
        # the short link should match a specific pattern !!
        pattern = ['Z_', 'A_', 'B_', 'C_', 'D_', 'questions']
        parts = short_link.split('/')
        for i in range(len(parts)-1):
            part_pattern = parts[i][0:2]
            if pattern[i] == part_pattern:
                pass
            else:
                return 0
        if parts[len(parts)-1] == pattern[len(pattern)-1]:
            return 1
        else:
            return 0

    # Create new question
    def Create(self, short_link):
        """
        Create a new question in the files
        """
        link_check = self._check_short_link(short_link)
        if link_check == 1:
            pass
        else:
            return 0
        # generate a unique tag for this new instance
        while True:
            tag = TagGenerator()
            result = Question.objects.filter(q_unique_id=tag).exists()
            if result == False:
                break
        # Create question directory in the short link using the tag
        fname = 'type_question.tag_'+tag+'.json'
        new_dir = os.path.join(self.content_dir, short_link, tag)
        files_dir = os.path.join(new_dir, 'files')
        file_name = os.path.join(new_dir, fname)
        # setting up the dummy data
        with open(
                    os.path.join(self.data_dir, 'templates/question.json'), "r"
                ) as jsonFile:
            file = jsonFile.read()
        template_data = json.loads(file)
        template_data['link'] = file_name
        template_data['object_unique_id'] = {'object_unique_id': tag}
        # Creating and writing to object
        try:
            os.makedirs(new_dir)
            os.makedirs(files_dir)
            with open(file_name, 'a') as f:
                json.dump(template_data, f)
                f.close()
        except Exception:
            return 0
        else:
            return 1

    # Read
    def Read(self, q_unique_id):
        """
        Read question in the files, uses q_unique id to locate questions
        """
        q_object = get_object_or_404(Question, q_unique_id=q_unique_id)
        try:
            f = open(q_object.q_link, "r")
            content = f.read()
            f.close()
        except Exception:
            return 0
        else:
            return content

    # Update Question
    def Update(self, q_unique_id, content):
        """
        Update question in the files
        """
        q_object = get_object_or_404(Question, q_unique_id=q_unique_id)
        try:
            with open(q_object.q_link, 'w') as f:
                f.write(content)
        except Exception:
            return 0
        else:
            return 1

    # Delete question
    def Delete(self, q_unique_id):
        """
        Delete question in the files
        """
        q_object = get_object_or_404(Question, q_unique_id=q_unique_id)
        q_dir = q_object.q_dir
        try:
            shutil.rmtree(q_dir, ignore_errors=False)
        except Exception:
            return 0
        else:
            q_object.delete()
            return 1


# Point crud
class PointCRUD():
    # init
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
        self.data_dir = decouple_config('data_dir')

    # link validation
    def _check_short_link(self, short_link):
        # the short link should match a specific pattern !!
        pattern = ['Z_', 'A_', 'B_', 'C_', 'D_']
        parts = short_link.split('/')
        if len(pattern) != len(parts):
            return 0
        for i in range(len(pattern)):
            part_pattern = parts[i][0:2]
            if pattern[i] == part_pattern:
                pass
            else:
                return 0
        return 1

    # create
    def Create(self, short_link):
        """
        Create a new point in the files
        """
        link_check = self._check_short_link(short_link)
        if link_check == 1:
            pass
        else:
            return 0
        # generate a unique tag for this new instance
        while True:
            tag = TagGenerator()
            result = Question.objects.filter(q_unique_id=tag).exists()
            if result == False:
                break
        # open directory and count the number of existing points
        # Create question directory in the short link using the tag
        fname = 'type_point.tag_'+tag+'.json'
        total_points = (
                glob.glob(
                    os.path.join(self.content_dir, short_link, 'N_*'),
                    recursive=True
                )
            )
        points_names = [p.split('/')[-1]for p in total_points]
        points_nums = [int(p.split('_')[-1]) for p in points_names]
        points_nums.append(0)
        nth_point = str(max(points_nums)+1)
        new_dir = os.path.join(self.content_dir, short_link, f'N_{nth_point}')
        files_dir = os.path.join(new_dir, 'files')
        file_name = os.path.join(new_dir, fname)
        #
        with open(
                    os.path.join(self.data_dir, 'templates/point.json'),
                    "r"
                ) as jsonFile:
            file = jsonFile.read()
        template_data = json.loads(file)
        template_data['link'] = file_name
        template_data['object_unique_id'] = {'object_unique_id': tag}
        try:
            os.makedirs(new_dir)
            os.makedirs(files_dir)
            with open(file_name, 'a') as f:
                json.dump(template_data, f)
                f.close()
        except Exception:
            return 0
        else:
            return 1

    # read
    def Read(self, p_unique_id):
        """
        Read point in the files
        """
        p_object = get_object_or_404(Point, p_unique_id=p_unique_id)
        try:
            f = open(p_object.p_link, "r")
            content = f.read()
            f.close()
        except Exception:
            return 0
        else:
            return content

    # update
    def Update(self, p_unique_id, content):
        """
        Update point in the files
        """
        p_object = get_object_or_404(Point, p_unique_id=p_unique_id)
        try:
            with open(p_object.p_link, 'w') as f:
                f.write(content)
        except Exception:
            return 0
        else:
            return 1

    # delete
    def Delete(self, p_unique_id):
        """
        Delete point in the files
        """
        p_object = get_object_or_404(Point, p_unique_id=p_unique_id)
        p_loc = p_object.p_directory
        try:
            shutil.rmtree(p_loc, ignore_errors=False)
        except Exception:
            return 0
        else:
            p_object.delete()
            return 1


# Specification crud
class SpecificationCRUD():
    # Init
    def __init__(self, content_dir=decouple_config('specifications_dir')):
        self.content_dir = content_dir

    # link validation
    def _check_short_link(self, short_link):
        # the short link should match a specific pattern !!
        pattern = ['Z_', 'A_', 'B_']
        parts = short_link.split('/')
        if len(pattern) != len(parts):
            return 0
        for i in range(len(pattern)):
            part_pattern = parts[i][0:2]
            if pattern[i] == part_pattern:
                pass
            else:
                return 0
        return 1

    # Create
    def Create(self, short_link, name):
        """
        Create a new point in the files
        """
        link_check = self._check_short_link(short_link)
        if link_check == 1:
            if name.isalnum() == True:
                pass
            else:
                return 0
        else:
            return 0
        # open directory and count the number of existing points
        # Create question directory in the short link using the tag
        fname = name + '.json'
        new_dir = os.path.join(self.content_dir, short_link)
        file_name = os.path.join(new_dir, fname)
        try:
            os.makedirs(new_dir, exist_ok=True)
            open(file_name, 'a').close()
        except Exception:
            return 0
        else:
            return 1

    # Read
    def Read(self, spec_board, spec_name):
        """
        Read spec in the files
        """
        spec_object = get_object_or_404(
                Specification,
                spec_board=spec_board,
                spec_name=spec_name
            )
        try:
            f = open(spec_object.spec_link, "r")
            content = f.read()
            f.close()
        except Exception:
            return 0
        else:
            return content

    # update
    def Update(self, spec_board, spec_name, content):
        """
        Update spec in the files
        """
        spec_object = get_object_or_404(
                Specification,
                spec_board=spec_board,
                spec_name=spec_name
            )
        try:
            with open(spec_object.spec_link, 'w') as f:
                f.write(content)
        except Exception:
            return 0
        else:
            return 1

    # Delete
    def Delete(self, spec_board, spec_name):
        """
        Delete spec in the files
        """
        spec_object = get_object_or_404(
                Specification,
                spec_board=spec_board,
                spec_name=spec_name
            )
        spec_link = spec_object.spec_link
        try:
            os.remove(spec_link)
        except Exception:
            return 0
        else:
            spec_object.delete()
            return 1

