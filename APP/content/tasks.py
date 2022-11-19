from celery import shared_task
@shared_task()
def _checkvideohealth(video):
    videos = Video.objects.all()
    for video in videos:
        video_url = video.v_link
        print(video_url)
        if 'embed' in video_url or 'watch?v=' in video_url:
            video_url = video_url.replace('embed/', 'watch?v=')
            r = requests.get(video_url)
            if "Video unavailable" in r.text:
                video.v_health = False
            else:
                video.v_health = True
        else:
            video.v_health = False
        video.save()

