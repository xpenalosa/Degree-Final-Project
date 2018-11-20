from django.conf.urls import url
from . import views

urlpatterns = [
    # post views
    url(r'^$', views.PostListView.as_view(), name='post_list'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'\
        r'(?P<post>[-\w]+)/$',
        views.post_detail,
        name='post_detail'),
    url(r'^objectius$', views.ObjectiveListView.as_view(), name='objectius'),
    url(r'^objectius/(?P<slug>.*)$',
        views.objective_detail,
        name='objectius_detail'),
]
