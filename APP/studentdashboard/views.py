from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
class IndexView(generic.ListView):
    template_name = "studentdashboard/index.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class ButtonsView(generic.ListView):
    template_name = "studentdashboard/buttons.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class CardsView(generic.ListView):
    template_name = "studentdashboard/cards.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class UtilColorView(generic.ListView):
    template_name = "s-dash-utilities/utilities-color.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class UtilBorderView(generic.ListView):
    template_name = "s-dash-utilities/utilities-border.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class UtilAnimationView(generic.ListView):
    template_name = "s-dash-utilities/utilities-animation.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class UtilOtherView(generic.ListView):
    template_name = "s-dash-utilities/utilities-other.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class BlankView(generic.ListView):
    template_name = "studentdashboard/blank.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class ChartsView(generic.ListView):
    template_name = "studentdashboard/charts.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class TablesView(generic.ListView):
    template_name = "studentdashboard/tables.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
class NotFoundView(generic.ListView):
    template_name = "studentdashboard/404.html"
    context_object_name = 'context'
    def get_queryset(self):
        return "user_index"
