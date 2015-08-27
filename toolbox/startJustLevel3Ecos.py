# File startJustLevel3Ecos.py
#
# In:   text string containing the ecoregion numbers for this summary
#       resolution for this analysis
#       results folder
#
# Written:         Sep 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting, os, sys, traceback
from LULCTrends.trendutil import AnalysisNames, TrendsUtilities
from LULCTrends.analysis import TrendsDataAccess, testStudyAreaStats
from LULCTrends.xcel.TrendsWorkbookClass import TrendsWorkbook

def startJust3s( ecoString, resolution, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)

        runName = 'Trends'
        ecoList = TrendsUtilities.parseNumberList( gp, ecoString )
        ecoList.sort()

        #check for invalid entries in ecolist
        if ecoList[0] < 1 or ecoList[-1] > 84:
            gp.AddError("Invalid ecoregion number.  Numbers must be between 1 and 84.")
            raise TrendsUtilities.JustExit()
                
        analysisNum = AnalysisNames.getAnalysisNum( gp, runName )

        #Get block counts for each ecoregion and start processing
        newEcos, strats, splits = TrendsDataAccess.accessTrendsData( ecoList, analysisNum, resolution )
        testStudyAreaStats.buildStudyAreaStats( runName, analysisNum, newEcos, strats, splits )

        for eco in ecoList:
            newExcel = TrendsWorkbook( gp, runName, analysisNum, resolution, outFolder, eco )
            newExcel.build_workbook( gp )
            del newExcel

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
    except TrendsUtilities.JustExit:
        pass
    except Exception:
        gp.AddMessage(traceback.format_exc())

if __name__ == "__main__":
    try:
        gp = arcgisscripting.create(9.3)
        ecoString = gp.GetParameterAsText(0)
        resolution = gp.GetParameterAsText(1)
        outFolder = gp.GetParameterAsText(2)
        startJust3s( ecoString, resolution, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
