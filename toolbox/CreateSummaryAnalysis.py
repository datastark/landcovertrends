# File CreateSummaryAnalysis.py
#
# Quick tool for generating a single summary analysis and report
#
# In:   eco list
#       analysis name
#       resolution
#       folder for excel files
#
# Written:         Oct 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting, os, sys, traceback
from LULCTrends.trendutil import TrendsNames, AnalysisNames, TrendsUtilities, deleteAnalysisName
from LULCTrends.analysis import TrendsDataAccess, testStudyAreaStats
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

def startOneSummary(ecoString, newname, resolution, outFolder):
    try:
        gp = arcgisscripting.create(9.3)
        gp.overwriteOutput = True

        #create a file to log failures for tool return
        statusfile = False
        try:
            statusfile = open( os.path.join( outFolder, "analysis_log.txt"), 'w')
        except Exception:
            pass

        ecoList = TrendsUtilities.parseNumberList( gp, ecoString )
        ecoList.sort()

        #check for invalid entries in ecolist
        if ecoList:
            if ecoList[0] < 1 or ecoList[-1] > 84:
                msg = "Invalid ecoregion number.  Numbers must be between 1 and 84."
                if statusfile:
                    statusfile.write( msg + "\n" )
                gp.AddError(msg)
                raise TrendsUtilities.JustExit()
        if len(ecoList) < 2:
            msg = "Ecoregion list for " +newname+ " does not contain at least 2 ecoregions. No summary can be done."
            if statusfile:
                statusfile.write( msg + "\n" )
            gp.AddError(msg)
            raise TrendsUtilities.JustExit()
                
        if AnalysisNames.isInAnalysisNames( gp, newname):
            msg = "The name \'" + newname + "\' is already in use in the database.  Please choose another."
            if statusfile:
                statusfile.write( msg + "\n" )
            gp.AddError(msg)
            raise TrendsUtilities.JustExit
                
        AnalysisNames.updateAnalysisNames( gp, newname )
        analysisNum = AnalysisNames.getAnalysisNum( gp, newname )

        newEcos, strats, splits = TrendsDataAccess.accessTrendsData( ecoList, analysisNum, resolution )

        testStudyAreaStats.buildStudyAreaStats( newname, analysisNum, newEcos, strats, splits )
        newExcel = SummaryWorkbook( gp, newname, analysisNum, resolution, outFolder )
        newExcel.build_workbook( gp )
        del newExcel

        #clean out name from database
        deleteAnalysisName.deleteAnalysisName( newname )
        statusfile.write("Create Summary Analysis tool execution is complete.\n")

    except arcgisscripting.ExecuteError:
        # Get the geoprocessing error messages
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
        ecoString = gp.GetParameterAsText(0)
        newname = gp.GetParameterAsText(1)
        resolution = gp.GetParameterAsText(2)
        outFolder = gp.GetParameterAsText(3)
        startOneSummary(ecoString, newname, resolution, outFolder)
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)
