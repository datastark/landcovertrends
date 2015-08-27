# File startAllStates.py
#
# In:   list of states for analysis
#       resolution for this analysis
#       results folder
# Out:  excel files of analysis results to subfolders in results folder
#       shapefiles of total and sample blocks to subfolders in results folder
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
from LULCTrends.analysis import CustomDataAccess, testStudyAreaStats
from LULCTrends.xcel.CustomWorkbookClass import CustomWorkbook
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

def startStates( tempList, resolution, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.overwriteOutput = True

        stateList = [ table.strip("\'") for table in tempList ]
        for state in stateList:
            gp.AddMessage(state)

        infeatures = "//REMOVE/REMOVE/LULCTrends/Vectors/States/states_generalized_Albers.shp"
        test = r'in_memory\teststates'
            
        for state in stateList:
            stateabbrev = 'usa_' + state.replace(" ","",10)
            if AnalysisNames.isInAnalysisNames( gp, stateabbrev):
                deleteAnalysisName.deleteAnalysisName( stateabbrev)
                
            AnalysisNames.updateAnalysisNames( gp, stateabbrev )
            analysisNum = AnalysisNames.getAnalysisNum( gp, stateabbrev )
            gp.AddMessage("startStratified: state = " + state + "  analysisNum = " + str(analysisNum))

            #create a folder for the results
            subFolder = os.path.join(outFolder, state)
            if not os.path.isdir(subFolder):
                os.mkdir( subFolder )

            where_clause = "NAME10 = " + "'" + state + "'"
            gp.Select_analysis( infeatures, test, where_clause )
            newEcos, strats, splits = CustomDataAccess.accessCustomData( test, resolution, stateabbrev, subFolder )

            if len(newEcos) > 0:
                testStudyAreaStats.buildStudyAreaStats( stateabbrev, analysisNum, newEcos, strats, splits )

                for eco in newEcos:
                    newExcel = CustomWorkbook( gp, stateabbrev, analysisNum, resolution, subFolder, eco )
                    newExcel.build_workbook( gp )

                newExcel = SummaryWorkbook( gp, stateabbrev, analysisNum, resolution, subFolder )
                newExcel.build_workbook( gp )
                del newExcel
            else:
                deleteAnalysisName.deleteAnalysisName( stateabbrev )

        if gp.Exists( test ):
            gp.delete_management( test )

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
        tempList = gp.GetParameterAsText(0).split(';')
        resolution = gp.GetParameterAsText(1)
        outFolder = gp.GetParameterAsText(2)
        startStates( tempList, resolution, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())

