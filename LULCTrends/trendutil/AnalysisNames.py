# File AnalysisNames.py
#
# holds functions to manage the Trends AnalysisNames table
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
from . import TrendsNames, TrendsUtilities

def updateAnalysisNames( gp, name ):
    try:
        gp.OverWriteOutput = True

        sourceTable = TrendsNames.dbLocation + "AnalysisNames"

        #Find out which analysis numbers are currently in use
        #Get a new, unique number by sorting list and adding 1 to the last list value
        #Table is initialized with Trends number = 1
        if name == TrendsNames.name:
            raise TrendsUtilities.JustExit()
        inUse = []
        rows = gp.SearchCursor( sourceTable )
        row = rows.Next()
        while row:
            inUse.append( row.AnalysisNum )
            row = rows.Next()

        inUse.sort()
        validNum = inUse[-1] + 1
        del row, rows

        tableLoc = TrendsNames.dbLocation + "AnalysisNames"
        where_clause = "AnalysisName = \'" + name.upper() + "\'"
        rows = gp.SearchCursor( tableLoc, where_clause )
        row = rows.Next()
        if row is None:
            rows = gp.InsertCursor( tableLoc )
            row = rows.NewRow()
            row.AnalysisName = name.upper()
            row.AnalysisNum = validNum
            rows.InsertRow( row )
            gp.AddMessage("Analysis name: " + name + " added to AnalysisNames table in database")

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddError(msgs)
        raise
    except TrendsUtilities.JustExit:
        pass
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddError(pymsg)
        raise
    finally:
        try:
            del row, rows
        except Exception:
            pass

def getAnalysisNum( gp, name ):
    try:
        gp.OverWriteOutput = True

        tableLoc = TrendsNames.dbLocation + "AnalysisNames"
        where_clause = "AnalysisName = \'" + name.upper() + "\'"

        rows = gp.SearchCursor( tableLoc, where_clause )
        row = rows.Next()
        if row is None:
            analysisNum = None
        else:            
            analysisNum = row.AnalysisNum
        return analysisNum

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddError(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddError(pymsg)
        raise
    finally:
        try:
            del row, rows
        except Exception:
            pass

def isInAnalysisNames( gp, name ):
    try:
        gp.OverWriteOutput = True

        tableLoc = TrendsNames.dbLocation + "AnalysisNames"
        where_clause = "AnalysisName = \'" + name.upper() + "\'"
        rows = gp.SearchCursor( tableLoc, where_clause )
        row = rows.Next()
        if row is None:
            result = False
        else:
            result = True
        return result

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddError(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddError(pymsg)
        raise
    finally:
        try:
            del row, rows
        except Exception:
            pass
    

