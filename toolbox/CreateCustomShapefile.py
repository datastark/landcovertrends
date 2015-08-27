# File CreateCustomShapefile.py
#
# In:   input features as the new study area
#       analysis name to store statistics under
#       resolution for this analysis
# Out:  database update containing the block numbers for the ecoregions
#       analysis name
#
#       This is a wrapper for the accessCustomData function in the case
#       where it's called as a separate tool to just create the total and
#       sample block shapefiles.
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
import arcgisscripting, os, sys, traceback
from LULCTrends.trendutil import TrendsNames
from LULCTrends.analysis import CustomDataAccess

def createShapefile( custom_boundary, nameForFile, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverWriteOutput = True
        resolution = "60m"
        CustomDataAccess.accessCustomData( custom_boundary, resolution, nameForFile, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
        raise

if __name__ == "__main__":
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverWriteOutput = True
        boundary = gp.GetParameterAsText(0)
        name = gp.GetParameterAsText(1)
        outFolder = gp.GetParameterAsText(2)
        createShapefile( boundary, name, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
