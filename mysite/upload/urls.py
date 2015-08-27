from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('sendfile.views',
    (r'^complete/$', 'complete'),
    (r'^getfile/$', 'getfile'),
)
