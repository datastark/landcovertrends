# File gainsLosses.py
#
# In:   eco - ecoregion object
#       interval - change interval for calculations
#       analysisName - prefix for tables in database
#
# This set of functions creates the gains, losses, gross, and net values and their statistics for
#  this interval and ecoregion and stores in the database.
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting, numpy
import os, sys, traceback, time
from ..database import databaseWriteClass
from . import basicStatistics
from ..trendutil import TrendsNames, TrendsUtilities

def createToFromList( toFromList ):
    #Create an abridged copy of the ClassTransition db table in memory for repeated searching.
    #List contains tuples of the form: (TransitionID, FromClassNum, ToClassNum)
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3) 
        gp.OverwriteOutput = True
        localTable = TrendsNames.dbLocation + "ClassTransition"

        #read in the class transition table for use in making
        # gain, loss, gross, and net tables.        
        #Step through all the rows and build a tuple
        #  of (conversion id, toClassNum, fromClassNum) and store in the to-from list
        rows = gp.SearchCursor( localTable )
        row = rows.Next()
        while row:
            if row.TransitionID > 0 and row.TransitionID < 122:
                toFromList.append( (row.TransitionID, row.FromClassNum, row.ToClassNum) )
            row = rows.Next()

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        trlog.trwrite(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
    finally:
        try:
            del row, rows
        except Exception:
            pass

        
def getToFromNumbers( toFromList, LCin, toOrFrom, compOrGlgn ):
    #
    # In:   toFromList- list made from database ClassTransition table. The list contains the
    #           contents of the TransitionID, FromClassNum, and ToClassNum columns, stored
    #           as tuples (TransitionID, FromClassNum, ToClassNum)
    #       LCin- the land cover type of interest (range 1-11)
    #       toOrFrom- string representing 'to', to get values from the ToClassNum column, or
    #           'from' to get values from the FromClassNum column
    #       compOrGlgn - flag for composition or glgn list, composition wants all 11 transition
    #           ids, while glgn wants all but the 'no change' option (values: 'comp' or 'glgn')
    # Out:  convList- list containing the 10 or 11 transition ids to be used when adding gains or
    #           losses or calculating composition from the conversion array
    #
    # Goes through the classtransition table and extracts the transition ids of interest.  There
    #   will be 10 or 11 values found, ranging between 1 and 121.  These are the transitions to be used
    #   when calculating gains or losses or composition for a particular land cover type.
    #   If stmt looks for either gain AND LC type match OR loss AND LC type match.
    #    The next if stmt screens for the 'no change' transition and eliminates that from the list if
    #   the compOrGlgn flag is set to 'glgn'
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        
        convList = []
        for lc in range( len(toFromList)):
            if ((toOrFrom == 'to') and (toFromList[lc][2] == LCin))or((toOrFrom == 'from') and (toFromList[lc][1] == LCin)):
                if toFromList[lc][1] != toFromList[lc][2]:
                    convList.append( lc+1 )
                elif (toFromList[lc][1] == toFromList[lc][2]) and (compOrGlgn == 'comp'):
                    convList.append( lc+1 )
        return convList
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def calcGainsLosses( ecoarray, glgnarray ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Starting gain/loss/gross/net calculations   " + time.asctime())

        toFromList = []
        createToFromList( toFromList )

        #Fill in each array according to its calculation.  Gain for each LC is the sum of pixels for
        # all conversion ids where this LC is the 'to LC' type.  Loss for each LC is the sum
        # of all pixels for conversion ids where this LC is the 'from LC' type.  Gross = gain + loss.
        # Net = gain - loss.  The [0] in ecoGlgn[interval]['gain'][0][lc-1,:] points to the data array
        # for this glgn table, and the next [lc-1,:] selects a whole column from its numpy array, item by item.

        for lc in sorted( TrendsNames.LCtype ):
            #Calculate gains for this landcover
            gainList = getToFromNumbers( toFromList, lc, 'to', 'glgn' )
            for gainIndex in gainList:
                glgnarray[ 'gain' ][0][lc-1,:] += ecoarray[0][ gainIndex-1,:]
            #Calculate losses
            fromList = getToFromNumbers( toFromList, lc, 'from', 'glgn' )
            for fromIndex in fromList:
                glgnarray[ 'loss' ][0][lc-1,:] += ecoarray[0][ fromIndex-1,:]
            #Calculate gross change
            glgnarray[ 'gross' ][0][lc-1,:] = glgnarray[ 'gain' ][0][lc-1,:] + glgnarray[ 'loss' ][0][lc-1,:]
            #Calculate net change
            glgnarray[ 'net' ][0][lc-1,:] = glgnarray[ 'gain' ][0][lc-1,:] - glgnarray[ 'loss' ][0][lc-1,:]
            
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def calcGlgnStats( eco, glgnarray ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Starting gain/loss/gross/net statistics   " + time.asctime())

        for tabType in TrendsNames.glgnTabTypes:
            basicStatistics.dataStats( eco, TrendsNames.LCTypecntr,
                                       glgnarray[ tabType ][0],
                                       glgnarray[ tabType ][1] )

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def storeGainsLosses( eco, interval, analysisNum ):
    try:
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        #Write data and stats for gains/losses to db
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsGlgnData"
        else:
            tableName = TrendsNames.dbLocation + "CustomGlgnData"
            
        dbWriter = databaseWriteClass.glgnWrite( gp, tableName)
        dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution,
                                eco.ecoGlgn[interval], "data", "" )

        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsGlgnStats"
        else:
            tableName = TrendsNames.dbLocation + "CustomGlgnStats"
            
        dbWriter = databaseWriteClass.glgnWrite( gp, tableName)
        dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution,
                                eco.ecoGlgn[interval], "stats",
                                TrendsNames.statisticsNames )
                        
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
