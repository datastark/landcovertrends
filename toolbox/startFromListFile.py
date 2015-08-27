# File startFromListFile.py
#
# In:   filename containing names and eco lists
#       resolution
#       folder for excel files
#       yes/no if results should be deleted from the database
#
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
from LULCTrends.trendutil import AnalysisNames, TrendsUtilities, deleteAnalysisName
from LULCTrends.analysis import TrendsDataAccess, testStudyAreaStats
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

def startFromFile( filename, resolution, outFolder, deleteResults ): 
    try:
        gp = arcgisscripting.create(9.3)
        gp.overwriteOutput = True
        try:
            summaryfile = open( filename, 'r')
            contents = summaryfile.readlines()
            summaryfile.close()
        except:
            gp.AddError("Unable to access summary list file")
            raise Exception
                
        numlines = len(contents)

        for line in range(0, numlines, 2):
            newname = contents[line].rstrip()
            ecoString = contents[line+1].rstrip()
            ecoList = TrendsUtilities.parseNumberList( gp, ecoString )
            ecoList.sort()
                
            if len(ecoList) < 2:
                gp.AddError( "Ecoregion list for " +newname+ " does not contain at least 2 ecoregions. No summary can be done.")
                continue

            if ecoList[0] < 1 or ecoList[-1] > 84:
                gp.AddError( "Ecoregion list for " +newname+ " contains invalid values.  Accepted range is 1-84.")
                continue

            if AnalysisNames.isInAnalysisNames( gp, newname):
                deleteAnalysisName.deleteAnalysisName( newname)
                
            AnalysisNames.updateAnalysisNames( gp, newname )
            analysisNum = AnalysisNames.getAnalysisNum( gp, newname )
            gp.AddMessage("starting summary: analysis name = " + newname)

            newEcos, strats, splits = TrendsDataAccess.accessTrendsData( ecoList, analysisNum, resolution )

            testStudyAreaStats.buildStudyAreaStats( newname, analysisNum, newEcos, strats, splits )
            newExcel = SummaryWorkbook( gp, newname, analysisNum, resolution, outFolder )
            newExcel.build_workbook( gp )
            del newExcel

            if deleteResults == "Yes":
                #clean out name from database
                deleteAnalysisName.deleteAnalysisName( newname )
            
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
        filename = gp.GetParameterAsText(0)
        resolution = gp.GetParameterAsText(1)
        outFolder = gp.GetParameterAsText(2)
        deleteResults = gp.GetParameterAsText(3)
        startFromFile( filename, resolution, outFolder, deleteResults )
    except Exception:
        gp.AddMessage(traceback.format_exc())
