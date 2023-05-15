import os
from content.models import Question, Point, Video, Image
from django.conf import settings
import base64


#points = Point.objects.all()
#print(points)
#for point in points:
#    content = point.p_content['details']['description']
#    point.p_content = content
#    point.save()
#    print(content)







#res = sorted([int(i) for i in content.keys()])
#for key in res:
#    line = content[str(key)]
#    if 'img' in line:
#        img_info = line['img']['img_info']
#        img_name = line['img']['img_name']
#        if img_name:
#            image_path = os.path.join(point.p_files_directory, img_name)
#            name = img_name.split('.')[0]
#            extension = img_name.split('.')[-1]
#            new_name = f'point_{point.id}_{name}.{extension}'
#            copy_source = {
#                    'Bucket': 'practicepractice',
#                    'Key': image_path
#                }
#            try:
#                settings.AWS_S3_C.copy(copy_source, 'practicepractice', f'universal/{new_name}')
#                img_obj, _ = Image.objects.get_or_create(
#                        user=point.user,
#                        description=img_info,
#                        url=f'universal/{new_name}'
#                    )
#                point.p_images.add(img_obj)
#                point.save()
#                print(point.p_images.all())
#            except Exception as e:
#                print(str(e) + str(image_path))

#for item in hidden_content:
#    video = hidden_content[item]['vid']
#    video_link = video['vid_link']
#    video_title = video['vid_title']
#    if 'youtube' in str(video_link):
#        print(video_link, video_title)
#        vid_obj, _ = Video.objects.get_or_create(
#                user=point.user,
#                title=video_title,
#                url=video_link,
#            )
#        point.p_videos.add(vid_obj)
#        point.save()
#        print(point.p_videos.all())
