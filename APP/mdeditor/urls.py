# -*- coding:utf-8 -*-
from django.urls import path
from content import views

from .views import UploadView

app_name = 'mdeditor'
urlpatterns = [
    path(
        'uploads/',
        UploadView.as_view(),
        name='uploads'
    ),
]
