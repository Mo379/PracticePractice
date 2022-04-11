import os
import sys
import glob
import shutil
import json
from decouple import config as decouple_config
from django.shortcuts import get_object_or_404
from ..models import Question,Point,Specification
from .GeneralUtil import TagGenerator





class QuestionCRUD():
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
    def _check_short_link(self,short_link):
        #the short link should match a specific pattern !!
        pattern = ['Z_','A_','B_','C_','D_', 'questions']
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

    def Create(self, short_link):
        """
        Create a new question in the files
        """
        link_check = self._check_short_link(short_link)
        if link_check == 1:
            pass
        else:
            return 0
        #generate a unique tag for this new instance
        while True:
            tag = TagGenerator()
            result = Question.objects.filter(q_unique_id=tag).exists()
            if result == False:
                break
        #Create question directory in the short link using the tag
        fname = 'type_question.tag_'+tag+'.json'
        new_dir = os.path.join(self.content_dir,short_link,tag)
        files_dir = os.path.join(new_dir,'files')
        file_name = os.path.join(new_dir,fname)
        try:
            os.makedirs(new_dir)
            os.makedirs(files_dir)
            open(file_name, 'a').close()
        except:
            return 0
        else:
            return 1
    def Read(self, q_unique_id):
        """
        Read question in the files, uses q_unique id to locate questions
        """
        q_object = get_object_or_404(Question, q_unique_id=q_unique_id)
        try:
            f = open(q_object.q_link, "r")
            content = f.read()
            f.close()
        except:
            return 0
        else:
            return content

    def Update(self, q_unique_id, content):
        """
        Update question in the files
        """
        q_object = get_object_or_404(Question, q_unique_id=q_unique_id)
        try:
            with open(q_object.q_link, 'w') as f:
                f.write(content)
        except: 
            return 0 
        else:
            return 1
    def Delete(self, q_unique_id):
        """
        Delete question in the files
        """
        q_object = get_object_or_404(Question, q_unique_id=q_unique_id)
        try:
            print('deleting')
        except: 
            return 0 
        else:
            print('erasing')
            return 1















class PointCRUD():
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
    def _check_short_link(self,short_link):
        #the short link should match a specific pattern !!
        pattern = ['Z_','A_','B_','C_','D_']
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

    def Create(self, short_link):
        """
        Create a new point in the files
        """
        link_check = self._check_short_link(short_link)
        if link_check == 1:
            pass
        else:
            return 0
        #generate a unique tag for this new instance
        while True:
            tag = TagGenerator()
            result = Question.objects.filter(q_unique_id=tag).exists()
            if result == False:
                break
        #open directory and count the number of existing points 
        #Create question directory in the short link using the tag
        fname = 'type_point.tag_'+tag+'.json'
        total_points = (glob.glob(os.path.join(self.content_dir,short_link,'*'), 
            recursive = True))
        nth_point = str(len(total_points)+1)
        new_dir = os.path.join(self.content_dir,short_link,nth_point)
        files_dir = os.path.join(new_dir,'files')
        file_name = os.path.join(new_dir,fname)
        try:
            os.makedirs(new_dir)
            os.makedirs(files_dir)
            open(file_name, 'a').close()
        except:
            return 0
        else:
            return 1
    def Read(self, p_unique_id):
        """
        Read point in the files
        """
        p_object = get_object_or_404(Point, p_unique_id=p_unique_id)
        try:
            f = open(p_object.p_link, "r")
            content = f.read()
            f.close()
        except:
            return 0
        else:
            return content
    def Update(self, p_unique_id, content):
        """
        Update point in the files
        """
        p_object = get_object_or_404(Point, p_unique_id=p_unique_id)
        content = str(p_object.p_content)
        try:
            with open(p_object.p_link, 'w') as f:
                f.write(content)
        except: 
            return 0 
        else:
            return 1
    def Delete(self, p_unique_id):
        """
        Delete point in the files
        """
        p_object = get_object_or_404(Point, p_unique_id=p_unique_id)
        try:
            print('deleting')
        except: 
            return 0 
        else:
            print('erasing')
            return 1




class SpecificationCRUD():
    def __init__(self, content_dir=decouple_config('specifications_dir')):
        self.content_dir = content_dir
    def _check_short_link(self,short_link):
        #the short link should match a specific pattern !!
        pattern = ['Z_','A_','B_']
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
        #open directory and count the number of existing points 
        #Create question directory in the short link using the tag
        fname = name + '.json'
        new_dir = os.path.join(self.content_dir,short_link)
        file_name = os.path.join(new_dir,fname)
        try:
            os.makedirs(new_dir,exist_ok = True)
            open(file_name, 'a').close()
        except:
            return 0
        else:
            return 1
    def Read(self, spec_board,spec_name):
        """
        Read spec in the files
        """
        spec_object = get_object_or_404(Specification, 
                spec_board=spec_board, spec_name=spec_name)
        try:
            f = open(spec_object.spec_link, "r")
            content = f.read()
            f.close()
        except:
            return 0
        else:
            return content
    def Update(self, spec_board,spec_name, content):
        """
        Update spec in the files
        """
        spec_object = get_object_or_404(Specification, 
                spec_board=spec_board, spec_name=spec_name)
        content = str(spec_object.spec_content)
        try:
            with open(spec_object.spec_link, 'w') as f:
                f.write(content)
        except: 
            return 0 
        else:
            return 1
    def Delete(self, spec_board,spec_name):
        """
        Delete spec in the files
        """
        spec_object = get_object_or_404(Specification, 
                spec_board=spec_board, spec_name=spec_name)
        try:
            print('deleting')
        except: 
            return 0 
        else:
            print('erasing')
            return 1

