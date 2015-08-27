#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

from django.shortcuts import render_to_response, redirect
from trendstats.forms import CustomForm, SummaryForm
from sendcustom import sendfile_for_custom
from sendsummary import send_for_summary
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, Context

def index(request):
    return render_to_response('trendstats/index.html',)

def custom(request):
    if request.method == 'POST': # If the form has been submitted...
        form = CustomForm(request.POST, request.FILES)
        if form.is_valid(): # All validation rules pass
            eaddr = str(form.cleaned_data['recipient'])
            msg = sendfile_for_custom(eaddr,request.FILES['zipfolder'])
            return render_to_response('trendstats/complete.html', {'msg': msg})
    else:
        form = CustomForm() # An unbound form

    return render_to_response('trendstats/custom.html',
                              {'form': form},
                            context_instance=RequestContext(request))

def summary(request):
    if request.method == 'POST':
        form = SummaryForm(request.POST)
        if form.is_valid():
            eaddr = str(form.cleaned_data['recipient'])
            ecolist = str(form.cleaned_data['ecoregions'])
            name = str(form.cleaned_data['analysisname'])
            msg = send_for_summary( ecolist, name, eaddr )
            return render_to_response('trendstats/complete.html', {'msg': msg})
    else:
        form = SummaryForm()

    return render_to_response('trendstats/summary.html',
                              {'form': form},
                            context_instance=RequestContext(request))

def complete(request):
    return render_to_response('trendstats/complete.html',)

def stats(request):
    return render_to_response('trendstats/stats.html',)

def boundary(request):
    return render_to_response('trendstats/boundary.html',)

def spreadsheet(request):
    return render_to_response('trendstats/spreadsheet.html',)
    

