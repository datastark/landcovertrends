# TrendsUtilities.py
#
# module containing functions to be used by
#  other modules
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import os, sys, traceback
import arcgisscripting
from . import TrendsNames

TrendsLogFile = "TrendsStatisticsLogFile.txt"

#This function extracts the desired value from the first position
#  of the R return vector
def makeAtomic( anRobject ):
    return anRobject[0]

#Define Trends errors
class TrendsErrors( Exception ):
    def __init__( self, message ):
        self.message = "Trends error: " + message

class JustExit( Exception ): pass

#This function is used to centralize a logging function, so it can be
#  more easily switched between logging and printing.
class trLogger:
    trLogfile = None
    gp = arcgisscripting.create(9.3)
    try:
        def __init__(self, folder=""):
            if folder:
                trLogfilename = os.path.join( folder, TrendsLogFile)
                trLogger.trLogfile = open(trLogfilename,'w')
     
        def trwrite (self, msg):
            if trLogger.trLogfile:
                trLogger.trLogfile.write( msg + "\n" )
            else:
                trLogger.gp.AddMessage( msg )
            
        def trclose (self):
            trLogger.trLogfile.close()

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        if self.trLogfile:
            self.trLogfile.trwrite( pymsg )
            self.trLogfile.trclose()

def getYearsFromIntervals( gp, folderList ):
    try:
        years = []
        for folder in folderList:
            temp = folder.split('to')
            years.append( temp[0] )
            years.append( temp[1] )
        years.sort()
        for date in years:
            while years.count( date ) > 1:
                years.remove( date )
        return years
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)
        raise

def getIntervalList(gp, tableLoc, where_clause, field):
    try:
        intervals = []
        rows = gp.SearchCursor( tableLoc, where_clause, "", field )
        row = rows.Next()
        while row:
            if not (row.ChangePeriod in intervals):
                intervals.append( row.ChangePeriod.encode('utf-8' ))
            row = rows.Next()
        years = getYearsFromIntervals( gp, intervals )
        return intervals, years
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)
        raise
    finally:
        try:
            del row, rows
        except Exception:
            pass

def FindTimesChanged(gp, multiInterval, changeIntervals):
    try:
        changes = 0
        temp = multiInterval.split('to')
        Mstart = int(temp[0])
        Mend = int(temp[1])

        for interval in changeIntervals:
            temp = interval.split('to')
            Cstart = int(temp[0])
            Cend = int(temp[1])
            if Cstart >= Mstart and Cend <= Mend:
                changes += 1

        return changes
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)

def parseNumberList( gp, invalues ):
    
    #expects a string of numerical entries (1,2,4-6) and returns
    # an integer list of the individual numbers
    # an empty list is returned if unable to parse or input is empty
    try:
        entries = str(invalues)
        numlist = []
        if entries:
            temp = entries.split(",")            
            for each in temp:
                entry = each.strip()
                if entry.isdigit():
                    numlist.append( int(entry))
                else:
                    try:
                        values = entry.split("-")
                        for x in range(int(values[0]), int(values[1])+1):
                            numlist.append( x )
                    except Exception:
                        gp.AddMessage("Unable to parse input list")
                        numlist = []
                        break
        return numlist
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)

def getFirstInterval( eco ):
    intervals = eco.ecoData.keys()
    intervals.sort()
    return intervals[0]
