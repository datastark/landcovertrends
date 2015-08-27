# sendsummary.py
#
# Send block numbers and email address to ArcServer summary
# geoprocessing tool.
# This geoprocessing tool will send an email on completion.
#
# Written:         Jan 2012
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import os,sys,traceback
import arcpy
        
def send_for_summary(ecolist, name, recipient):
    try:
        msg = []
        arcpy.ImportToolbox("http://REMOVED/arcgis/services;CreateSummaryAnalysis", "CreateSummaryAnalysis")

        # Run the server tool with input parameters set 
        # This is an asynchronous tool so execution exits after tool is called
        result = arcpy.createSummaryAnalysis_CreateSummaryAnalysis(ecolist, name, recipient)
        msg.append("Thank you.")
        msg.append("Processing is in progress.")
        msg.append("You will receive an email when the files are ready.")
    except arcpy.ExecuteError:
        msg.append("We have a problem.")
        msg.append(arcpy.GetMessages())
    except Exception:
        msg.append("We have a problem.")
        msg.append(traceback.format_exc())
        
    return msg

if __name__ == '__main__':
    try:
        arcpy.GetParameterAsText(0, ecoregions)
        arcpy.GetParameterAsText(1, name)
        arcpy.GetParameterAsText(2, recipient)
        send_for_summary(ecoregions, name, recipient)
    except Exception:
        pass
