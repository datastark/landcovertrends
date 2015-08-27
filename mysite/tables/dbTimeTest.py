# dbTimeTest.py
#
# test how long it takes to execute a simple ArcGIS tool
#
# Written:         Nov 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import os,sys,traceback,time
timestamp = ['starting import of arcpy']
timestamp.append(time.asctime())
import arcpy
timestamp.append('completed import of arcpy')
timestamp.append(time.asctime())

def get_the_times():
    try:
        timestamp.append('importing toolbox')
        timestamp.append(time.asctime())
        arcpy.ImportToolbox("http://REMOVED/arcgis/services;TrendsNames", "TrendsNames")
        timestamp.append('completed importing toolbox')
        timestamp.append(time.asctime())

        # Run the server tool DisplayAnalysisNames with no input parameters
        # This is a synchronous tool so execution waits until the tool completes
        timestamp.append('starting tool execution')
        timestamp.append(time.asctime())
        result = arcpy.displayAnalysisNames_TrendsNames()
        outnames = str(result.getOutput(0))
        timestamp.append('completed tool execution')
        timestamp.append(time.asctime())
        return timestamp
    except arcpy.ExecuteError:
        print arcpy.GetMessages()
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)

if __name__ == '__main__':
    try:
        timestamp = get_the_times()
        print "Complete"
    except Exception:
        pass
