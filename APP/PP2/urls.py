"""PP2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from main.views import NotFoundView, ErrorView, robots_txt
from main.sitemaps import StaticViewSitemap
from django.views.generic.base import TemplateView
from content.sitemaps import NotesSitemap, QuestionsSitemap, PapersSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'notes': NotesSitemap,
    'questions': QuestionsSitemap,
    'papers': PapersSitemap,
}


urlpatterns = [
    path('', include('main.urls')),
    path('study/', include('content.urls')),
    path('user/', include('user.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('admin/', admin.site.urls),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path("robots.txt", robots_txt),

]

handler404 = NotFoundView.as_view()
handler500 = ErrorView.as_view()



if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



