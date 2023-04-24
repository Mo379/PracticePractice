import os
from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from content.models import Course, CourseVersion

class NotesSitemap(Sitemap):
    def items(self):
        courses = Course.objects.all()
        course_chapter = []
        for course in courses:
            version = CourseVersion.objects.filter(course=course).order_by('-version_number')[0]
            version_content = version.version_content
            modules = version_content.keys()
            #
            for module in modules:
                module_content = version_content[module]
                chapters = module_content['content'].keys()
                for chapter in chapters:
                    course_chapter.append({
                        "course_id": course.id,
                        'module': module,
                        'chapter': chapter,
                        })
            #
        return course_chapter

    def location(self, item):
        course_id = item['course_id']
        moduel = item['module']
        chapter = item['chapter']
        return reverse(
                'content:notearticle',
                kwargs={
                    'course_id': course_id,
                    'module': moduel,
                    'chapter': chapter
                }
            )

