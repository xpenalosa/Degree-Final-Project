"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, re_path, include
from django.contrib import admin
from django.views.generic import TemplateView

from project.application.views import test, create_tournament, display_tournament, list_tournaments, update_tournament, delete_tournament, status

urlpatterns = [
    re_path(r'^admin/?', admin.site.urls),
    path(r'blog/', include('project.blog_app.urls')),
    path(r'test', test, name="test"),
    re_path(r'^t/(?P<identifier>[0-9]{1,10})/?$', display_tournament, name="get_tournament"),
    path(r't/<int:identifier>/update', update_tournament, name="update_tournament"), 
    path(r't/<int:identifier>/delete', delete_tournament, name="delete_tournament"),
    path(r'list', list_tournaments, name="list_tournaments"),
    path(r'create', create_tournament, name="create_tournament"),
    path(r'status', status, name="status"),
    path(r'', TemplateView.as_view(template_name='index.html'), name='Home'),
]

