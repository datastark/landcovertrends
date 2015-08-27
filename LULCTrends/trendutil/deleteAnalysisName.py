# File deleteAnalysisName.py
#
# This module is run as a separate tool to delete
#  an analysis from the database, including both the name
#  and all data in all tables associated with that name.
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
from . import TrendsNames, TrendsUtilities

def deleteAnalysisName( name ):

# If split block intermediate table is ever used it will need to be added to this list
    allTables = [ "SummaryChangeStats",
                  "SummaryGlgnStats",
                  "SummaryCompStats",
                  "SummaryMultichangeStats",
                  "SummaryAllChangeStats",
                  "SummaryAggregateStats",
                  "SummaryAggGlgnStats",
                  "CustomChangeData",
                  "CustomChangeStats",
                  "CustomGlgnData",
                  "CustomGlgnStats",
                  "CustomCompData",
                  "CustomCompStats",
                  "CustomMultichangeData",
                  "CustomMultichangeStats",
                  "CustomAllChangeData",
                  "CustomAllChangeStats",
                  "CustomAggregateData",
                  "CustomAggregateStats",
                  "CustomAggGlgnData",
                  "CustomAggGlgnStats",
                  "SummaryAnalysisParams",
                  "SummaryEcoregions" ]

    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        gp.AddMessage("Deleting name from database: " + TrendsNames.dbLocation)

        tableName = "AnalysisNames"
        tableLoc = TrendsNames.dbLocation + tableName

        if name.upper() == TrendsNames.name:
            gp.AddError("The analysis name \'Trends\' is reserved and cannot be deleted with this tool")
            raise TrendsUtilities.JustExit()

        where_clause = "AnalysisName = \'" + name.upper() + "\'"
        
        #Delete name from AnalysisNames table
        rows = gp.UpdateCursor( tableLoc, where_clause )
        row = rows.Next()
        if row is not None:
            num = row.AnalysisNum
            rows.DeleteRow(row)
            gp.AddMessage("Deleted " + name + " from " + tableName)
        else:
            gp.AddWarning("Name not found in AnalysisNames database")
            raise TrendsUtilities.JustExit()
        del row, rows

        #Look for any data or stats for this name in intermediate, custom, supplemental or summary tables
        for tableName in allTables:
            tableLoc = TrendsNames.dbLocation + tableName
        
            where_clause = "AnalysisNum = " + str(num)
            rows = gp.UpdateCursor( tableLoc, where_clause )
            row = rows.Next()
            if row is not None:
                gp.AddMessage("Deleting " + name + " from " + tableName)
                while row:
                    rows.DeleteRow(row)
                    row = rows.Next()
            del row, rows

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
    except TrendsUtilities.JustExit:
        pass
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
    name = sys.argv[1]
    deleteAnalysisName( name )
    print "Complete"
