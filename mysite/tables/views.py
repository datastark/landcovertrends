#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

from django.shortcuts import render_to_response, get_object_or_404
from tables.models import trendsid, tstamp
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from QueryAnalysisNames import get_the_names
from dbTimeTest import get_the_times

def index(request):
    table_list = trendsid.objects.all().order_by('name')
    if len(table_list) > 10:
        fraction = len(table_list) / 3
        remainder = len(table_list)%3
        if (remainder):
            fraction += 1
        x = table_list[2*fraction:]
        if (remainder):
            x.append("")
        table_pieces = zip(table_list[0:fraction],table_list[fraction:2*fraction],x)
        return render_to_response('tables/index.html', {'table_pieces': table_pieces},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('tables/index.html', {'table_list': table_list},
                              context_instance=RequestContext(request))

def display(request):
    trendsid.objects.all().delete()
    namelist = get_the_names()
    for entry in namelist:
        n = trendsid( name=entry )
        n.save()
    table_list = trendsid.objects.all().order_by('name')
    if len(table_list) > 10:
        fraction = len(table_list) / 3
        remainder = len(table_list)%3
        if (remainder):
            fraction += 1
        x = table_list[2*fraction:]
        if (remainder):
            x.append("")
        table_pieces = zip(table_list[0:fraction],table_list[fraction:2*fraction],x)
        return render_to_response('tables/display.html', {'table_pieces': table_pieces},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('tables/display.html', {'table_list': table_list},
                              context_instance=RequestContext(request))

def timetest(request):
    tstamp.objects.all().delete()
    timelist = get_the_times()
    for entry in timelist:
        n = tstamp( name=entry )
        n.save()
    table_list = tstamp.objects.all()
    return render_to_response('tables/timetest.html', {'table_list': table_list},
                              context_instance=RequestContext(request))
