from django.conf.urls import url

from . import views


app_name = 'maxed'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<dataset_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<dataset_id>[0-9]+)/addobj/$', views.addobj, name='addobj'),
    url(r'^(?P<datasetobj_id>[0-9]+)/fields/$', views.fields, name='fields'),
    url(
        r'^(?P<datasetobj_id>[0-9]+)/addFilter/$',
        views.addFilter, name='addFilter'),
]
