# File startBoundaryShapefiles.py
#
# In:   folder with shapefiles for custom boundaries
#       sample file in folder for field names
#       name or prefix to append to filename
#       field containing name for boundary
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
import arcgisscripting, os, sys, traceback, glob
from LULCTrends.trendutil import AnalysisNames, TrendsUtilities, deleteAnalysisName
from LULCTrends.analysis import CustomDataAccess, testStudyAreaStats
from LULCTrends.xcel.CustomWorkbookClass import CustomWorkbook
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

def startBoundaries( infolder, prefix, resolution, outFolder, deleteResults ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.overwriteOutput = True

        os.chdir( infolder )
        fileList = glob.glob( "*.shp" )
            
        for boundary in fileList:
            temp = boundary.split(".")
            newname = prefix + "_" + temp[0]
            if AnalysisNames.isInAnalysisNames( gp, newname):
                deleteAnalysisName.deleteAnalysisName( newname)
                
            AnalysisNames.updateAnalysisNames( gp, newname )
            analysisNum = AnalysisNames.getAnalysisNum( gp, newname )
            gp.AddMessage("startStratified: boundary = " + boundary + " and analysis name = " + newname)

            subFolder = os.path.join(outFolder, newname)
            if not os.path.isdir( subFolder ):
                os.mkdir( subFolder )

            newEcos, strats, splits = CustomDataAccess.accessCustomData( boundary, resolution, newname, subFolder )

            if len(newEcos) > 0:
                testStudyAreaStats.buildStudyAreaStats( newname, analysisNum, newEcos, strats, splits )

                for eco in newEcos:
                    newExcel = CustomWorkbook( gp, newname, analysisNum, resolution, subFolder, eco )
                    newExcel.build_workbook( gp )

                newExcel = SummaryWorkbook( gp, newname, analysisNum, resolution, subFolder )
                newExcel.build_workbook( gp )
                del newExcel
            else:
                gp.AddError("No sample blocks are within the custom boundary " + boundary + ". No Trends processing done.")
                deleteResults = 'Yes'

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
        infolder = gp.GetParameterAsText(0)
        prefix = gp.GetParameterAsText(1)
        resolution = gp.GetParameterAsText(2)
        outFolder = gp.GetParameterAsText(3)
        deleteResults = gp.GetParameterAsText(4)
        startBoundaries( infolder, prefix, resolution, outFolder, deleteResults )
    except Exception:
        gp.AddMessage(traceback.format_exc())
