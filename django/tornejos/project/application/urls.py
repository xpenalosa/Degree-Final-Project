from django.urls import re_path
from django.views.generic import TemplateView

from project.application.views import test, create_tournament, get_tournament, list_tournaments

urlpatterns = [
    re_path(r'test/?', test, name='test'),
    re_path(r't/<int:identifier>/?', get_tournament, name='get_tournament'),
    re_path(r'.*', TemplateView.as_view(template_name='index.html'), name='Home'),
]

