#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

from django.db import models
    
class shapefile(models.Model):
    folder = models.CharField(max_length=50)
    foldersize = models.IntegerField()
    emailaddr = models.EmailField(max_length=100)
    req_date = models.DateTimeField('date of request')
    returnmsg = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.folder
