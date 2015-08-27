# QueryAnalysisNames.py
#
# Access server geoprocessing tool to display the analysis names
# currently in use in the database.
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

import os,sys,traceback
import arcpy

def get_the_names():
    try:
        # Add a toolbox from a server. The "mytools" parm is a temporary alias used to
        #  identify the toolbox in the arcpy call below.  A toolbox's alias can also
        #  be set in the toolbox's property window before publishing to the server.
        arcpy.ImportToolbox("http://REMOVED/arcgis/services;DisplayAnalysisNames", "DisplayAnalysisNames")

        # Run the server tool DisplayAnalysisNames with no input parameters
        # This is a synchronous tool so execution waits until the tool completes
        result = arcpy.displayAnalysisNames_DisplayAnalysisNames()
        outnames = str(result.getOutput(0))
        namelist = outnames.split(';')
        return namelist
    except arcpy.ExecuteError:
        print arcpy.GetMessages()
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)

if __name__ == '__main__':
    try:
        namelist = get_the_names()
        print "Complete"
    except Exception:
        pass
