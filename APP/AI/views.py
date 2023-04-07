from django.shortcuts import render
from braces.views import (
        LoginRequiredMixin,
        GroupRequiredMixin,
        SuperuserRequiredMixin,
    )
from django.views import generic


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
        context['hello'] = 'Hello world'
        # optain the subscribed spec or the unviersal spec
        return context

