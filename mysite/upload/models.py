from django.db import models
    
class inbox(models.Model):
    folder = models.CharField(max_length=50)
    foldersize = models.IntegerField()
    emailaddr = models.EmailField(max_length=100)
    req_date = models.DateTimeField('date of request')
    returnmsg = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.folder
