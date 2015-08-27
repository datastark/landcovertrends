# File startTheStatusTrends.py
#
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

import arcgisscripting, os, sys, traceback
from LULCTrends.trendutil import TrendsNames, AnalysisNames, TrendsUtilities
from LULCTrends.analysis import TrendsDataAccess, testStudyAreaStats
from LULCTrends.trendutil import deleteAnalysisName
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

def startStatusTrends( tempList, resolution, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        tableList = [ table.strip("\'") for table in tempList ]
        for table in tableList:
            gp.AddMessage(table)
            
        for sumname in tableList:
            summary = "st_" + sumname
            #Delete old summary data from tables before creating new data
            if AnalysisNames.isInAnalysisNames( gp, summary ):
                deleteAnalysisName.deleteAnalysisName( summary )

            ecoList = []
            #Get the ecoregion numbers for each summary name in the list
            if sumname == "AllUS":
                ecoList = [x for x in range(1,85)]  #want list of ecos 1-84
            elif sumname == "Western":
                ecoList = [x for x in range(1,25)] + [41,77,78,79,80,81]
            elif sumname == "GreatPlains":
                ecoList = [x for x in range(25,35)] + [40,42,43,44,46,47,48]
            elif sumname == "MidwestSouthCentral":
                ecoList = [35,36,37,38,39] + [x for x in range(49,58)] + [61,72,73]
            elif sumname == "Eastern":
                ecoList = [45,58,59,60] + [x for x in range(62,72)] + [74,75,76,82,83,84]
            elif sumname == "NorthGreatPlains":
                ecoList = [42,43,46,48]
            else:
                gp.AddError("Unknown summary name")

            AnalysisNames.updateAnalysisNames( gp, summary )
            analysisNum = AnalysisNames.getAnalysisNum( gp, summary )
            gp.AddMessage("startStratified: summary = " + summary + "  analysisNum = " + str(analysisNum))

            #Get the ecoregions and samples for the new summary
            newEcos, strats, splits = TrendsDataAccess.accessTrendsData( ecoList, analysisNum, resolution )

            #Start the Trends processing
            path = os.path.dirname(sys.argv[0])
            testStudyAreaStats.buildStudyAreaStats( summary, analysisNum, newEcos, strats, splits )

            newExcel = SummaryWorkbook( gp, summary, analysisNum, resolution, outFolder )
            newExcel.build_workbook( gp )
            del newExcel

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddError(msgs)
    except TrendsUtilities.JustExit:
        pass
    except Exception:
        gp.AddMessage(traceback.format_exc())

if __name__ == "__main__":
    try:
        gp = arcgisscripting.create(9.3)
        tempList = gp.GetParameterAsText(0).split(';')
        resolution = gp.GetParameterAsText(1)
        outFolder = gp.GetParameterAsText(2)
        startStatusTrends( tempList, resolution, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
