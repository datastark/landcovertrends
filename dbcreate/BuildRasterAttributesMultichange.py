# File buildRasterAttributesMultichange.py
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
folderPath = "REMOVED/Multichange_Images/1973to2000/"

#Create the geoprocessor object
gp = arcgisscripting.create(9.3)

try:
    folderlist = os.listdir( folderPath )
    for folder in folderlist:
        path = folderPath + folder
        gp.workspace = path
        print "Getting rasters in " + path
        rasters = gp.ListRasters("", "IMG")

        print "Building attribute tables"
        for raster in rasters:
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
