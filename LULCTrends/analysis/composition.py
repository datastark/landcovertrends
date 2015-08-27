# File composition.py
#
# In:   eco - ecoregion object
#       interval - change interval for calculations
#       analysisNum - analysis number for summary or custom run
#
# This set of functions creates the composition tables and their statistics for
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
from .gainsLosses import createToFromList, getToFromNumbers


def calcComposition( eco, interval ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Starting composition calculations   " + time.asctime())

        toFromList = []
        createToFromList( toFromList )
        years = eco.ecoComp.keys()
        years.sort()

        dates = interval.split('to')
        if (years.index(dates[1]) - years.index(dates[0])) != 1:  #skip multiple change years - already counted
            raise TrendsUtilities.JustExit()
        thisYear = dates[0]
        fromTo = 'from'

        #Fill in the data array according to its calculation.  Composition for each LC is the sum of pixels for
        # all conversion ids where this LC is the 'from LC' type, unless the last or most recent year in the
        # composition set is reached.  For this year, the composition is the sum of pixels for the 'to LC' type.
        # The [0] in ecoComp[thisYear][0][lc-1,:] points to the data array
        # and the next [lc-1,:] selects a whole column from its numpy array, item by item.

        for lc in sorted( TrendsNames.LCtype):
            gainLossList = getToFromNumbers( toFromList, lc, fromTo, 'comp' )
            for glIndex in gainLossList:
                eco.ecoComp[ thisYear ][0][lc-1,:] = eco.ecoComp[ thisYear ][0][lc-1,:] + \
                                                     eco.ecoData[ interval ][0][ glIndex-1,:]

        #If on the most recent interval, also calculate the 'to LC' values for the most recent year
        if dates[1] == years[-1]:
            thisYear = dates[1]
            fromTo = 'to'
            for lc in sorted( TrendsNames.LCtype):
                gainLossList = getToFromNumbers( toFromList, lc, fromTo, 'comp' )
                for glIndex in gainLossList:
                    eco.ecoComp[ thisYear ][0][lc-1,:] = eco.ecoComp[ thisYear ][0][lc-1,:] + \
                                                         eco.ecoData[ interval ][0][ glIndex-1,:]
            
    except TrendsUtilities.JustExit:
        pass
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def calcCompStats( eco, year ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Starting composition statistics   " + time.asctime())

        basicStatistics.dataStats( eco, TrendsNames.LCTypecntr,
                                    eco.ecoComp[ year ][0],
                                    eco.ecoComp[ year ][1] )

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit


def storeComposition( eco, year, analysisNum ):
    try:
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsCompData"
        else:
            tableName = TrendsNames.dbLocation + "CustomCompData"
            
        dbWriter = databaseWriteClass.compositionWrite( gp, tableName)
        dbWriter.databaseWrite( gp, analysisNum, eco, year, eco.resolution,
                                eco.ecoComp[year][0], "data", "" )

        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsCompStats"
        else:
            tableName = TrendsNames.dbLocation + "CustomCompStats"
            
        dbWriter = databaseWriteClass.compositionWrite( gp, tableName)
        dbWriter.databaseWrite( gp, analysisNum, eco, year, eco.resolution,
                                eco.ecoComp[year][1], "stats",
                                TrendsNames.statisticsNames )
                        
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
