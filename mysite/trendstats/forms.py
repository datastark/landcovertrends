#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

from django import forms
import re
from numberchecker import parseNumberList

class CustomForm(forms.Form):
    recipient = forms.EmailField(max_length=100, label='Your email address')
    zipfolder = forms.FileField(label='Zip folder')

class SummaryForm(forms.Form):
    recipient = forms.EmailField(max_length=100, label='Your email address')
    ecoregions = forms.CharField(max_length=250, label='List of ecoregions')
    analysisname = forms.CharField(max_length=100,label='Your analysis name')

    def clean_ecoregions(self):
        ecos = self.cleaned_data['ecoregions']
        errors = parseNumberList(ecos)
        if errors:
            raise forms.ValidationError(errors)
        return ecos

    def clean_analysisname(self):
        name = str(self.cleaned_data['analysisname'])
        reg = re.compile(r'^[a-zA-Z][a-zA-Z0-9._-]*$')
        if not re.match(reg, name):
            raise forms.ValidationError("The name contains invalid file name characters.")
        if name.lower() == 'trends':
            raise forms.ValidationError("Sorry. That name is already in the database. Please pick another.")
        return name
