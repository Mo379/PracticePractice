import os
import sys
import glob
import json
from decouple import config as decouple_config
from ..models import Question,Point
from .GeneralUtil import TagGenerator





class QuestionCRUD():
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
    def Create(self):
        """
        Create a new question in the files
        """
        pass
    def Read(self):
        """
        Read question in the files
        """
        pass
    def Update(self):
        """
        Update question in the files
        """
        pass
    def Delete(self):
        """
        Delete question in the files
        """
        pass






class PointCRUD():
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
    def Create(self):
        """
        Create a new point in the files
        """
        pass
    def Read(self):
        """
        Read point in the files
        """
        pass
    def Update(self):
        """
        Update point in the files
        """
        pass
    def Delete(self):
        """
        Delete point in the files
        """
        pass




class SpecificationCRUD():
    def __init__(self, content_dir=decouple_config('content_dir')):
        self.content_dir = content_dir
    def Create(self):
        """
        Create a new spec in the files
        """
        pass
    def Read(self):
        """
        Read spec in the files
        """
        pass
    def Update(self):
        """
        Update spec in the files
        """
        pass
    def Delete(self):
        """
        Delete spec in the files
        """
        pass

