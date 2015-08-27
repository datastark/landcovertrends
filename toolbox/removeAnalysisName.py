# File removeAnalysisNames.py
#
# This module is run as a separate tool to delete
#  the analysis names in the database.
#
# Written:         Dec 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import traceback
import arcgisscripting
from LULCTrends.trendutil.deleteAnalysisName import deleteAnalysisName

def removeStatName( name ):
    try:
        gp = arcgisscripting.create(9.3)
        deleteAnalysisName(name)
    except Exception:
        gp.AddMessage(traceback.format_exc())

if __name__ == "__main__":
    try:
        gp = arcgisscripting.create(9.3)
        name = gp.GetParameterAsText(0)
        removeStatName( name )
    except Exception:
        gp.AddMessage(traceback.format_exc())
