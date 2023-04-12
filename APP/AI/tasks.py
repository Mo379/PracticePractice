import collections
from celery import shared_task
from content.models import Course
from django.core.mail import send_mail
from content.util.GeneralUtil import (
        order_full_spec_content,
        order_live_spec_content
    )
import time


@shared_task()
def _generate_course_introductions(course_id):
    course = Course.objects.get(pk=course_id)
    content = course.specification
    content = order_live_spec_content(content.spec_content)
    modules = list(content.keys())
    mod_chap = collections.OrderedDict({})
    for module in modules:
        _chapters = list(content[module]['content'].keys())
        mod_chap[module] = _chapters
    for module in mod_chap.keys():
        chapters = mod_chap[module]
        for chapter in chapters:
            print(module, chapter)
    course.save()

