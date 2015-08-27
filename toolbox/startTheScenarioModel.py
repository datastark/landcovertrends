# File startTheScenarioModel.py
#
# starts analysis for each summary selected in the input list
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

def startScenarios( tempList, resolution, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        tableList = [ table.strip("\'") for table in tempList ]
        for table in tableList:
            gp.AddMessage(table)
            
        Hier1 = TrendsNames.dbLocation + "EcoregionHierarchy"
        Eco1 = TrendsNames.dbLocation + "Level1Ecoregions"
        Eco2 = TrendsNames.dbLocation + "Level2Ecoregions"

        for sumname in tableList:
            summary = "sm_" + sumname
            #Delete old summary data from tables before creating new data
            if AnalysisNames.isInAnalysisNames( gp, summary ):
                deleteAnalysisName.deleteAnalysisName( summary )

            ecoList = []
            #Get the ecoregion numbers for each summary name in the list
            if sumname in ["WESTERNMOUNTAINSFORESTS","EASTERNUS","GREATPLAINS","WESTERNARID"]:
                where_clause = "AnalysisName = \'" + sumname + "\'"
                rows = gp.SearchCursor( Eco1, where_clause )
                row = rows.Next()
                eco1 = row.EcoLevel1ID
                gp.AddMessage("EcoLevel1ID = " + str(eco1))
                #now get the level 3s for this level 1
                where_clause = "EcoLevel1ID = " + str(eco1)
                rows = gp.SearchCursor( Hier1, where_clause )
                row = rows.Next()
                while row:
                    ecoList.append( int(row.Ecolevel3ID) )
                    gp.AddMessage("adding eco " + str( ecoList[-1]) + " to ecoList")
                    row = rows.Next()
            else:
                where_clause = "AnalysisName = \'" + sumname + "\'"
                rows = gp.SearchCursor( Eco2, where_clause )
                row = rows.Next()
                eco2 = row.EcoLevel2ID
                gp.AddMessage("EcoLevel2ID = " + str(eco2))
                #now get the level 3s for this level 2
                where_clause = "EcoLevel2ID = " + str(eco2)
                rows = gp.SearchCursor( Hier1, where_clause )
                row = rows.Next()
                while row:
                    ecoList.append( int(row.Ecolevel3ID) )
                    gp.AddMessage("adding eco " + str( ecoList[-1]) + " to ecoList")
                    row = rows.Next()

            AnalysisNames.updateAnalysisNames( gp, summary )
            analysisNum = AnalysisNames.getAnalysisNum( gp, summary )
            gp.AddMessage("startStratified: summary = " + summary + "  analysisNum = " + str(analysisNum))

            #Get the intermediate tables ready for the new summary
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
        startScenarios( tempList, resolution, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
