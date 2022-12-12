from content.models import Question
qs = Question.objects.all()
for q in qs:
    content = q.q_content
    questions = content['details']['questions']
    total = 0
    for part in questions:
        try:
            marks = int(questions[part]['q_part_mark'])
        except Exception:
            marks = 0
        total += marks
    q.q_total_marks = total
    q.save()
