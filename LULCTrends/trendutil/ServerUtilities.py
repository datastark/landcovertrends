# File ServerUtilities.py
#
# Tools for use by scripts running under ArcGIS Server
#  to send email and create unique job folders.
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright
#
import arcgisscripting, os, traceback
import time, smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate

#output directory for tool results
server_results_path = r"\\REMOVED\Trendsresults"  #server location removed
gp = arcgisscripting.create(9.3)

def send_mail(send_from, send_to, subject, text, server, smtpUser="", smtpPwd=""):
    try:
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = send_to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach( MIMEText(text) )
            
        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
    except Exception:
        gp.AddMessage(traceback.format_exc())

def send_auto_email(recipient, destpath):
    try:
        text = "The Custom Shapefile processing you requested has completed.\n\n" + \
                "To copy the results to your own computer,\n" + \
                "open a Windows or Internet Explorer window and copy\n\n" + \
                destpath + "\n\ninto the address window.\n" + \
                "You can copy your files from this folder.\n\n" + \
                "Do you plan to link your new Excel file(s) to other Excel files?\n" + \
                "When you open the new Excel file(s) for the first time, do a 'save'\n" + \
                "of the file.  This makes Microsoft Excel happy.  Why?  It's complicated.\n\n" + \
                "Please note that your files will be automatically deleted\n" + \
                "one week from today.\n\nThis message was generated automatically" + \
                " on process completion."

        send_mail("jmjones@usgs.gov",
                  recipient,
                  "Trends processing complete",
                  text,
                  "REMOVED") #mail server name removed
    except Exception:
        gp.AddMessage(traceback.format_exc())        

def create_server_results_folder():
    try:
        #get unique job id from server tool to use as output
        #subfolder name to place results in for each job
        scratchpath = gp.ScratchWorkspace.split("\\")
        idindex = 0
        for idx,p in enumerate(scratchpath):
            if p.count('_gpserver'):
                idindex = idx+1
        if idindex:
            jobid = scratchpath[idindex]
        else:
            jobid = "job_" + str(int(time.time()))

        #create a subfolder in the server results folder
        # with this jobid. Create the subfolder now for use
        # by the processing that will follow.
        subfolder = os.path.join(server_results_path,jobid)
        if not os.path.isdir( subfolder ):
            os.mkdir( subfolder )
        return subfolder
    except Exception:
        gp.AddMessage(traceback.format_exc())        

