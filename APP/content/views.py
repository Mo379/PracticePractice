from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic


from .models import *
# Create your views here.


class IndexView(generic.ListView):
    template_name = 'content/index.html'
    context_object_name = 'context'
    def get_queryset(self):
        """Return the last three published questions."""
        latest_q= Question.objects.all().order_by('id')[0:2]
        latest_p= Point.objects.all()[0:2] 
        latest_v= Video.objects.all()[0:2] 
        context = {
            'latest_q': latest_q,
            'latest_p': latest_p,
            'latest_v': latest_v,
        }
        return context
