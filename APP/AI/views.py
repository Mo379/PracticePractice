import collections
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from django.views import generic
from content.models import Course
from user.models import (
        User
    )
from AI.models import Lesson
from user.forms import (
        AppearanceChoiceForm,
    )
from content.util.GeneralUtil import (
        order_live_spec_content
    )


# Create your views here.
class AIView(
        LoginRequiredMixin,
        generic.ListView
        ):
    login_url = 'user:login'
    redirect_field_name = False
    template_name = 'AI/AI.html'
    context_object_name = 'context'

    def get_queryset(self):
        """Return all of the required hub information"""
        context = {}
        course_id = self.kwargs['course_id']
        user = User.objects.get(pk=self.request.user.id)
        appearancechoiceform = AppearanceChoiceForm(instance=user)
        # Get course modules and chapters
        course = Course.objects.get(pk=course_id)
        spec = course.specification
        content = order_live_spec_content(spec.spec_content)
        modules = list(content.keys())
        unclaimables = set()
        claimed_lessons = Lesson.objects.filter(
                user=user,
                course=course,
            )
        for claimed_lesson in claimed_lessons:
            idx = modules.index(claimed_lesson.moduel)
            del modules[idx]
        for task in tasks:
            if task.task_chapter != 'Null':
                unclaimables.add(task.task_moduel)
        # 
        context['form_appearancechoice'] = appearancechoiceform
        context['modules'] = modules
        return context


@login_required(login_url='/user/login', redirect_field_name=None)
def _themechange(request):
    if request.method == 'POST':
        form = AppearanceChoiceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(
                    request,
                    messages.INFO,
                    'Your preferred theme was successfully updated ' +
                    '(Try to refresh your browser if no changes show).',
                    extra_tags='alert-success AI_window'
                )
        else:
            messages.add_message(
                    request,
                    messages.INFO,
                    'Something is wrong, please check that all inputs are valid.'+str(form.errors),
                    extra_tags='alert-danger AI_window'
                )
    else:
        messages.add_message(
                request,
                messages.INFO,
                'Invalid Request Method',
                extra_tags='alert-danger AI_window'
            )
    return redirect('AI:index')


