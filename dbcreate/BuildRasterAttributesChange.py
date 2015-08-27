# File buildRasterAttributes.py
#
# Creates a raster attribute table for each .img file so
#  ArcGIS can read it in.
#
# Written:         Jan 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import arcgisscripting, os
import sys, traceback

#Set the topmost workspace folder
folderPath = "REMOVED/Change_Images/2000to2005/"

#Create the geoprocessor object
gp = arcgisscripting.create(9.3)

try:
    #folderList = os.listdir( folderPath )
    folderList = ['Eco07']
    allFiles = {}

    for folder in folderList:
        path = folderPath + folder + "/"
        gp.workspace = path
        print "Getting rasters in folder " + path
        rasters = gp.ListRasters("", "IMG")
        allFiles[ folder ] = rasters

    for folder in folderList:
        path = folderPath + folder + "/"
        gp.workspace = path
        print "Working in " + path
        for raster in allFiles[ folder ]:
            gp.BuildRasterAttributeTable_management(raster, "Overwrite")
    
except arcgisscripting.ExecuteError:
    # Get the geoprocessing error messages
    msgs = gp.GetMessage(0)
    msgs += gp.GetMessages(2)
    print msgs    
except Exception:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
    print pymsg
