import os
from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from content.models import Question, Point

class NotesSitemap(Sitemap):
    def items(self):
        Notes = Point.objects.values(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                ).distinct().order_by(
                    'p_level',
                    'p_subject',
                    'p_moduel',
                    'p_chapter',
                )
        Notes_objs = [obj for obj in Notes]
        return Notes_objs

    def location(self, item):
        level = item['p_level']
        subject = item['p_subject']
        moduel = item['p_moduel']
        chapter = item['p_chapter']
        return reverse(
                'content:notearticle',
                kwargs={
                    'level': level,
                    'subject': subject,
                    'board': 'Universal',
                    'specification': 'Universal',
                    'module': moduel,
                    'chapter': chapter
                }
            )


class QuestionsSitemap(Sitemap):
    def items(self):
        Notes = Question.objects.values(
                    'q_level',
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                ).distinct().order_by(
                    'q_level',
                    'q_subject',
                    'q_moduel',
                    'q_chapter',
                )
        Notes_objs = [obj for obj in Notes]
        return Notes_objs

    def location(self, item):
        level = item['q_level']
        subject = item['q_subject']
        moduel = item['q_moduel']
        chapter = item['q_chapter']
        return reverse(
                'content:question',
                kwargs={
                    'level': level,
                    'subject': subject,
                    'specification': 'universal',
                    'module': moduel,
                    'chapter': chapter
                }
            )


class PapersSitemap(Sitemap):
    def items(self):
        Notes = Question.objects.values(
                    'q_subject',
                    'q_board',
                    'q_board_moduel',
                    'q_exam_year',
                    'q_exam_month',
                ).distinct().order_by(
                    'q_subject',
                    'q_board',
                    'q_board_moduel',
                    'q_exam_year',
                    'q_exam_month',
                ).filter(q_is_exam=1)
        Notes_objs = [obj for obj in Notes]
        return Notes_objs

    def location(self, item):
        subject = item['q_subject']
        board = item['q_board']
        board_moduel = item['q_board_moduel']
        exam_year = item['q_exam_year']
        exam_month = item['q_exam_month']
        return reverse(
                'content:paper',
                kwargs={
                    'subject': subject,
                    'board': board,
                    'board_moduel': board_moduel,
                    'exam_year': exam_year,
                    'exam_month': exam_month
                }
            )
