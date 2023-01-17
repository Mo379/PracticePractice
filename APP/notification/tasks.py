from celery import shared_task
from django.core.mail import send_mail


@shared_task()
def _send_email(mail_subject, message, mail_sender, to_email):
    #
    send_mail(
        mail_subject,
        message,
        mail_sender,
        [to_email],
        fail_silently=False,
    )
