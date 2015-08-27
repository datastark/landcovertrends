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
from sendfile.models import inbox
from sendfile.forms import InboxForm
from sendtoserver import sendfile_for_boundary
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, Context
import datetime

def getfile(request):
    if request.method == 'POST': # If the form has been submitted...
        form = InboxForm(request.POST, request.FILES)
        if form.is_valid(): # All validation rules pass
            eaddr = str(form.cleaned_data['recipient'])
            msg = sendfile_for_boundary(eaddr,request.FILES['zipfolder'])
            req = inbox( emailaddr=eaddr,
                            folder=request.FILES['zipfolder'].name,
                            foldersize=request.FILES['zipfolder'].size,
                            req_date=datetime.datetime.now(),
                            returnmsg=msg)
            req.save()
            #return render_to_response('sendfile/complete.html', {'msg': msg})
            return HttpResponseRedirect('/sendfile/complete/')
    else:
        form = InboxForm() # An unbound form

    return render_to_response('sendfile/getfile.html',
                              {'form': form},
                            context_instance=RequestContext(request))

def complete(request):
    return render_to_response('sendfile/complete.html', {'msg': 'Trends'})
