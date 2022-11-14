from celery import shared_task
from content.util.ContentSync import (
        QuestionSync,
        PointSync,
        VideoSync,
        SpecificationSync
    )


@shared_task()
def QuestionSyncTask():
    sync_obj = QuestionSync()
    sync_obj.sync()


@shared_task()
def PointSyncTask():
    sync_obj = PointSync()
    sync_obj.sync()


@shared_task()
def VideoSyncTask():
    sync_obj = VideoSync()
    sync_obj.sync()


@shared_task()
def SpecificationSyncTask():
    sync_obj = SpecificationSync()
    sync_obj.sync()
