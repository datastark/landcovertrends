from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('tables.views',
    (r'^$', 'index'),
    (r'^display/$', 'display'),
    (r'^timetest/$', 'timetest'),
)
