# File buildRasterAttributes.py
#
# Updates the raster attribute table for each .img file
#  in the input file so
#  ArcGIS can read it in.
#  Right now this is doing 60m resolution
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
folderPath = "REMOVED/Data/Change_Images/"
datafile = "sampleBlocksforUpdate.txt"

#Create the geoprocessor object
gp = arcgisscripting.create(9.3)
gp.OverwriteOutput = True

try:
    scriptLocation = os.path.dirname(sys.argv[0])
    filename = os.path.join(scriptLocation, datafile)
    print("Reading contents of sample block file: " + filename)
    contents = []
    for line in open( filename ):
        contents.append( line.rstrip())
        print contents[-1]

    folderList = os.listdir( folderPath )
    folderList.remove('1973to2000')
    allFiles = {}
    for folder in folderList:
        allFiles[ folder ] = []
    
    for folder in folderList:
        path = folderPath + folder + "/"
        gp.workspace = path
        for line in contents:
            block = line.split("-")
            allFiles[folder].append("samp" + block[0] + "_" + block[1] + "_" + folder + "_change_60m.img")
            print "Building raster name " + allFiles[folder][-1]

    for folder in folderList:
        rasterpath = folderPath + folder + "/"
        gp.workspace = rasterpath
        print "Working in folder " + rasterpath
        for raster in allFiles[ folder ]:
            print "Creating attribute table for " + raster
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
