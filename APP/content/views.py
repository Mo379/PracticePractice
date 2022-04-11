from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .util.ContentSync import QuestionSync,PointSync,VideoSync,SpecificationSync
from .util.ContentCRUD import QuestionCRUD,PointCRUD,SpecificationCRUD


from .models import *
# Create your views here.


class IndexView(generic.ListView):
    template_name = 'content/index.html'
    context_object_name = 'context'
    def get_queryset(self):
        """Return the last three published questions."""
        latest_q= Question.objects.all().order_by('id')[0]
        latest_p= Point.objects.all()[0] 
        latest_v= Video.objects.all()[0] 
        context = {
            'latest_q': latest_q.q_content,
            'latest_p': latest_p.p_content,
            'latest_v': latest_v.v_title,
        }
        return context

class HubView(generic.ListView):
    template_name = 'content/hub.html'
    context_object_name = 'context'
    def get_queryset(self):
        """Return all of the required hub information"""
        crud = QuestionCRUD()

        #q_full_syn= crud.Create('Z_test/A_test/B_test/C_test/questions', 'content')
        #q_full_syn= crud.Create('Z_test/A_test/B_test/C_test/D_test', 'content')
        q_full_syn= crud.Delete('38ff4a1d90')
        context = {
            'Q_crud': q_full_syn,
        }

        return context














