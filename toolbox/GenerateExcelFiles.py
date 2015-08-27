#GenerateExcelFiles.py
#
# Starts the creation of excel files from the Trends database
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting
import os, sys, traceback
from LULCTrends.trendutil import AnalysisNames, TrendsNames, TrendsUtilities
from LULCTrends.xcel.TrendsWorkbookClass import TrendsWorkbook
from LULCTrends.xcel.CustomWorkbookClass import CustomWorkbook
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

def makeExcelFiles( runType, ecoString, runName, resolution, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #if any eco numbers entered in ecoString, clean up and
        # break into a list
        ecoList = TrendsUtilities.parseNumberList( gp, ecoString )
        ecoList.sort()
        
        #Check for valid analysis name
        if not AnalysisNames.isInAnalysisNames( gp, runName ):
            gp.AddWarning("No database information stored for that analysis name")
            raise TrendsUtilities.JustExit()
        
        #check for valid combination of analysis name, type and ecolist
        if runType == 'Trends':
            runNum = TrendsNames.TrendsNum
            if not len(ecoList):
                gp.AddWarning("No ecoregions were selected for Trends file generation.")
                raise TrendsUtilities.JustExit()
        elif runType == 'Custom':
            if not len(ecoList):
                gp.AddWarning("No ecoregions were selected for custom file generation.")
                raise TrendsUtilities.JustExit()
            runNum = AnalysisNames.getAnalysisNum( gp, runName )        
        else:  #summary
            if len(ecoList):
                gp.AddWarning("Ecoregion numbers are ignored for summary file generation.")
            del ecoList
            ecoList = [0]
            runNum = AnalysisNames.getAnalysisNum( gp, runName )

        #Generate the appropriate excel file(s)
        for eco in ecoList:
            if runType == 'Trends':
                newExcel = TrendsWorkbook( gp, runName, runNum, resolution, outFolder, eco )
            elif runType == 'Custom':
                newExcel = CustomWorkbook( gp, runName, runNum, resolution, outFolder, eco )
            else:  #summary
                newExcel = SummaryWorkbook( gp, runName, runNum, resolution, outFolder )
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
        gp.OverWriteOutput = True
        runType = gp.GetParameterAsText(0)
        ecoString = gp.GetParameterAsText(1)
        runName = gp.GetParameterAsText(2).upper()
        resolution = gp.GetParameterAsText(3)
        outFolder = gp.GetParameterAsText(4)
        makeExcelFiles( runType, ecoString, runName, resolution, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
