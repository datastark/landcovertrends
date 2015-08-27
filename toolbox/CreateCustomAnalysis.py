# File CreateCustomAnalysis.py
#
# In:   shapefile with custom boundary
#       new analysis name
#       resolution
#       output folder
#
# Out:  excel reports to subfolder in results folder
#       shapefiles of total blocks and sample blocks to subfolder
#
#       Performs an analysis for one custom boundary, creating spreadsheets
#       of the statistics results and shapefiles of the total and sample blocks
#       in a subfolder within the results folder.  When complete, the data
#       and stats for the custom boundary are deleted from the database.
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
import arcgisscripting, os, sys, traceback, shutil
from LULCTrends.trendutil import AnalysisNames, TrendsUtilities, deleteAnalysisName
from LULCTrends.analysis import CustomDataAccess, testStudyAreaStats
from LULCTrends.xcel.CustomWorkbookClass import CustomWorkbook
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

def startOneCustom(Input_Features, newname, resolution, outFolder):
    try:
        gp = arcgisscripting.create(9.3)
        gp.overwriteOutput = True
        #create a file to log failures for tool return
        statusfile = False
        try:
            statusfile = open( os.path.join( outFolder, "analysis_log.txt"), 'w')
        except Exception:
            pass
            
        if AnalysisNames.isInAnalysisNames( gp, newname):
            msg = "The name \'" + newname + "\' is already in use.  Please choose another."
            if statusfile:
                statusfile.write( msg + "\n" )
            gp.AddError(msg)
            raise TrendsUtilities.JustExit
                
        AnalysisNames.updateAnalysisNames( gp, newname )
        analysisNum = AnalysisNames.getAnalysisNum( gp, newname )

        #create a folder for the results
        subFolder = os.path.join(outFolder, newname)
        if not os.path.isdir( subFolder ):
            os.mkdir( subFolder )

        newEcos, strats, splits = CustomDataAccess.accessCustomData( Input_Features, resolution, newname, subFolder )

        if len(newEcos) > 0:
            testStudyAreaStats.buildStudyAreaStats( newname, analysisNum, newEcos, strats, splits )

            for eco in newEcos:
                newExcel = CustomWorkbook( gp, newname, analysisNum, resolution, subFolder, eco )
                newExcel.build_workbook( gp )

            newExcel = SummaryWorkbook( gp, newname, analysisNum, resolution, subFolder )
            newExcel.build_workbook( gp )
            del newExcel
        else:
            msg = "No sample blocks are within the custom boundary. No Trends processing done."
            if statusfile:
                statusfile.write( msg + "\n" )
            gp.AddError(msg)

        #clean out name from database
        deleteAnalysisName.deleteAnalysisName( newname )
        statusfile.write("Create Custom Analysis tool execution is complete.\n")

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
        errmsg = "The summary analysis tool failed with the following ArcGIS error:\n"
        if statusfile:
            statusfile.write(errmsg + msgs + "\n")
    except TrendsUtilities.JustExit:
        pass
    except Exception:
        pymsg = traceback.format_exc()
        gp.AddMessage(pymsg)
        errmsg = "The summary analysis tool failed with the following Python error:\n"
        if statusfile:
            statusfile.write(errmsg + pymsg + "\n")
    finally:
        try:
            if statusfile:
                statusfile.close()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverWriteOutput = True
        In_Features = gp.GetParameterAsText(0)
        nename = gp.GetParameterAsText(1)
        res = gp.GetParameterAsText(2)
        oFolder = gp.GetParameterAsText(3)
        startOneCustom(In_Features, nename, res, oFolder)
    except Exception:
        gp.AddMessage(traceback.format_exc())
