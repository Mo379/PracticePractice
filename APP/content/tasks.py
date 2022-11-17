from celery import shared_task
from content.util.ContentSync import (
        QuestionSync,
        PointSync,
        VideoSync,
        SpecificationSync
    )


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

@shared_task()
def _syncspecquestions(request):
    specs = Specification.objects.all()
    for spec in specs:
        for m_name, moduel in spec.spec_content.items():
            for c_name, chapter in moduel['content'].items():
                questions = chapter['questions']
                keys = questions.keys()
                for i in range(5):
                    i = i+1
                    if i not in keys:
                        questions[i] = []
                    n_questions = len(questions[i])
                    if n_questions < 5:
                        n_diff = 5 - n_questions
                        new_questions = Question.objects.filter(
                                q_level=spec.spec_level,
                                q_subject=spec.spec_subject,
                                q_moduel=m_name,
                                q_chapter=c_name,
                                q_difficulty=i
                            ).exclude(
                                    q_unique_id__in=questions[i]
                                )[:n_diff]
                        for new_q in new_questions:
                            questions[i].append(new_q.q_unique_id)
                    else:
                        questions[i] = questions[i][0:5]
                chapter['questions'] = questions
        spec.save()

    messages.add_message(
            request,
            messages.INFO,
            'Successfully synced specification questions',
            extra_tags='alert-success syncspecquestions_form'
        )
    return redirect('dashboard:superuser_contentmanagement')



