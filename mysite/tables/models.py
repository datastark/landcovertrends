from django.db import models

class trendsid(models.Model):
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

class tstamp(models.Model):
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

