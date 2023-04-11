from celery import shared_task
from content.models import Course
from django.core.mail import send_mail
import time


@shared_task()
def _generate_course_introductions(course_id):
    course = Course.objects.get(pk=course_id)
    content = course.specification
    course.save()

