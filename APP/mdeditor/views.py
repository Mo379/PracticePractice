# -*- coding:utf-8 -*-
import os
import datetime

from django.views import generic
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .configs import MDConfig
from io import BytesIO
from content.models import Question, Point

# TODO 此处获取default配置，当用户设置了其他配置时，此处无效，需要进一步完善
MDEDITOR_CONFIGS = MDConfig('default')


class UploadView(generic.View):
    """ upload image file """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)
        object_id = request.POST['my_object_id']
        object_type = request.POST['my_object_type']
        # image none check
        if not upload_image:
            return JsonResponse({
                'success': 0,
                'message': "Failed to find an image.",
                'url': ""
            })
        # image format check
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        file_name = '.'.join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return JsonResponse({
                'success': 0,
                'message': "Invalid format detected, image has got to be：%s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
                'url': ""
            })
        # save image
        try:
            f = BytesIO()
            for chunk in upload_image.chunks():
                f.write(chunk)
            f.seek(0)
            #get object location
            if object_type == 'Point':
                obj = Point.objects.get(pk=object_id)
                file_key = f'{obj.p_files_directory}/{file_name}.{file_extension}'
            elif object_type == 'Question':
                obj = Question.objects.get(pk=object_id)
                file_key = f'{obj.q_files_directory}/{file_name}.{file_extension}'
            settings.AWS_S3_C.upload_fileobj(
                    f,
                    settings.AWS_BUCKET_NAME,
                    file_key,
                    ExtraArgs={'ACL': 'public-read'}
                )
        except Exception as e:
            return JsonResponse({
                'success': 0,
                'message': 'Something went wrong cannot upload image.'+str(e),
                'url': ""
            })
        else:
            # image floder check
            return JsonResponse({'success': 1,
                                 'message': "Success !",
                                 'url': f"{file_name}.{file_extension}"
                                 })
