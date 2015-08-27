# File CreateAnalysisName.py
#
#   Creates the database table that maps analysis names to unique identifiers
#
# Written:         Oct 2010
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import os, sys, traceback
import arcgisscripting
from LULCTrends.trendutil import TrendsNames

def makeAnalysisNameTable():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #Analysis name table
        tableName = "AnalysisNames"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName )
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "AnalysisName", "text","50" )

        rows = gp.InsertCursor( tableLoc )
        row = rows.NewRow()
        row.AnalysisNum = 1
        row.AnalysisName = "TRENDS"
        rows.InsertRow( row )
        del rows,row
            
    except arcgisscripting.ExecuteError:
        # Get the geoprocessing error messages
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise     #push the error up to exit

if __name__ == '__main__':
    try:
        makeAnalysisNameTable()
        print "Complete"
    except Exception:
        pass
