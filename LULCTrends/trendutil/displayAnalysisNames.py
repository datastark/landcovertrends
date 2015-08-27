# File displayAnalysisNames.py
#
# This module is run as a separate tool to display
#  the analysis names in the database.
#
# Written:         Nov 2010
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
from . import TrendsNames

def displayAnalysisNames():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        tableName = "AnalysisNames"
        tableLoc = TrendsNames.dbLocation + tableName
        sortField = "AnalysisName"
        gp.AddMessage("Table in use: " + tableLoc)
        gp.AddMessage("Analysis names currently in use:")

        #get name from AnalysisNames table
        rows = gp.SearchCursor( tableLoc, "","","", sortField)
        row = rows.Next()
        while row:
            num = row.AnalysisNum
            name = row.AnalysisName
            gp.AddMessage("Analysis name: " + name + " and number: " + str(num))
            row = rows.Next()

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)
    finally:
        try:
            del row, rows
        except Exception:
            pass

if __name__ == '__main__':
    try:
        displayAnalysisNames()
        print "Complete"
    except Exception:
        pass
