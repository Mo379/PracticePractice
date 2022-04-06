import os
import sys
import glob
import json
from decouple import config as decouple_config
from ..models import Question,Point

#left to figure out how to insert the extracted information into the models with smart features
class QuestionSync():
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
    def sync(self, subdir=''):
        """
        Synchronises all of the questions in the files data into the database
        """
        #getting all the question files
        structure= {}
        for root, dirs, files in os.walk(self.content_dir+subdir, topdown=False):
            for file in files:
                if('type_question' in file):
                    files = [s for s in files if "type_question" in s]
                    structure[root] = files
                    continue
        #getting all the question information
        for ddir,question in structure.items():
            #getting source information from name
            q_subject = ddir.split('/A_')[1].split('/')[0]
            q_moduel= ddir.split('/B_')[1].split('/')[0]
            q_chapter= ddir.split('/C_')[1].split('/')[0]
            try:
                q_topic= ddir.split('/D_')[1].split('/')[0] 
            except: 
                q_topic = ''
            q_dir= ddir
            q_files_dir = ddir+'/files'
            q_unique_id = ddir.split('/')[-1]
            #getting json file data
            q_link = ddir +'/'+question[0]
            with open(q_link, 'r') as file:
                content= file.read()
            data = json.loads(content)
            #extracting info from json file data
            q_content = data
            q_difficulty = data['details']['head']['0']['q_difficulty']
            q_level = data['details']['head']['0']['q_level']
            q_board = data['details']['head']['0']['q_board']
            q_board_moduel = data['details']['head']['0']['q_moduel']
            q_exam_month = data['details']['head']['0']['q_month']
            q_exam_year = data['details']['head']['0']['q_year']
            q_exam_number = data['details']['head']['0']['q_number']
            q_type = data['details']['head']['0']['q_type']
            #Load question information to model
            if Question.objects.filter(q_unique_id=q_unique_id):
                my_question = Question.objects.get(q_unique_id=q_unique_id)
            else:
                my_question = Question()
            my_question.q_level = q_level
            my_question.q_board = q_board
            my_question.q_board_moduel= q_board_moduel
            my_question.q_exam_month= q_exam_month if q_exam_month != '' else 0
            my_question.q_exam_year= q_exam_year if q_exam_year != '' else 0 
            my_question.q_is_exam= bool(q_exam_number)
            my_question.q_exam_num= q_exam_number if q_exam_number != '' else 0
            my_question.q_subject = q_subject
            my_question.q_moduel = q_moduel
            my_question.q_chapter= q_chapter
            my_question.q_topic= q_topic
            my_question.q_type= q_type
            my_question.q_difficulty= q_difficulty
            my_question.q_total_marks= 0
            my_question.q_content= q_content
            my_question.q_dir= q_dir
            my_question.q_link= q_link
            my_question.q_unique_id= q_unique_id
            my_question.save()
        return 'full sync'

left to figure out how to read the points information form the files into the database
class PointSync():
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
    def sync(slef):
        """
        Synchronises all of the points in the files data into the database
        """
        return 'full sync'
