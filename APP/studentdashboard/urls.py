from django.urls import path, include
from . import views


# Create your views here.
app_name = 'studentdashboard'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('buttons', views.ButtonsView.as_view(), name='buttons'),
    path('cards', views.CardsView.as_view(), name='cards'),
    path('util-color', views.UtilColorView.as_view(), name='util-color'),
    path('util-border', views.UtilBorderView.as_view(), name='util-border'),
    path('util-animation', views.UtilAnimationView.as_view(), name='util-animation'),
    path('util-other', views.UtilOtherView.as_view(), name='util-other'),
    path('charts', views.ChartsView.as_view(), name='charts'),
    path('tables', views.TablesView.as_view(), name='tables'),
    path('blank', views.BlankView.as_view(), name='blank'),
    path('404', views.NotFoundView.as_view(), name='404'),
]
