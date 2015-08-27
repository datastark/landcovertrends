#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('trendstats.views',
    (r'^$','index'),
    (r'^custom/$', 'custom'),
    (r'^summary/$', 'summary'),
    (r'^complete/$', 'complete'),
    (r'^stats/$','stats'),
    (r'^boundary/$','boundary'),
    (r'^spreadsheet/$','spreadsheet'),
)
