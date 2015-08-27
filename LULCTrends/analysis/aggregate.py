# File aggregate.py
##
# This set of functions creates the aggregate values and their statistics for
#  this ecoregion and stores in the database.
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
import os, sys, traceback, time
from ..database import databaseWriteClass
from . import basicStatistics
from .EcoregionStatistics import findTotalEstimatedPixels
from ..trendutil import TrendsNames, TrendsUtilities

def findAggregateYears( eco, interval ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        years = eco.ecoComp.keys()
        years.sort()
        splitInfo = interval.split('to')
        start = splitInfo[0]
        end = splitInfo[1]
        intermediateIntervals = []
        #Build a list of intervals to add together that span the start
        # and end years of the given interval
        for ptr in range( years.index(start), years.index(end) ):
            intermediateIntervals.append( years[ptr] + "to" + years[ptr+1])
        return intermediateIntervals
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def calcAddGross( eco ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Starting aggregate gross calculations   " + time.asctime())

        source = 'gross'
        add_keys = eco.aggregate_gross_keys
        for interval in add_keys:
            sumyears = findAggregateYears( eco, interval )

            if sumyears:
                for years in sumyears:
                    #add each conversion interval together to get the sum over all intervals
                    eco.aggregate[ interval ][source][0][:,:] += eco.ecoData[ years ][0][:,:]

                #change pixel count for aggregate
                findTotalEstimatedPixels( eco, eco.aggregate[interval][source][0] )

                #Do the statistics
                basicStatistics.dataStats( eco, TrendsNames.numConversions,
                                           eco.aggregate[ interval ][source][0],
                                           eco.aggregate[ interval ][source][1] )
            else:
                del eco.aggregate_gross_keys[interval]
                
        #reset pixel count
        firstInterval = TrendsUtilities.getFirstInterval( eco )
        findTotalEstimatedPixels( eco, eco.ecoData[firstInterval][0] )
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit


def storeAddGross( eco, analysisNum ):
    try:
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        source = 'gross'
        add_keys = eco.aggregate_gross_keys
        
        #Write data and stats for aggregate to db
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsAggregateData"
        else:
            tableName = TrendsNames.dbLocation + "CustomAggregateData"
        dbWriter = databaseWriteClass.aggregateWrite( gp, tableName)
            
        for interval in add_keys:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                    eco.aggregate[interval][source][0], "data", "" )

        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsAggregateStats"
        else:
            tableName = TrendsNames.dbLocation + "CustomAggregateStats"
        dbWriter = databaseWriteClass.aggregateWrite( gp, tableName)
            
        for interval in add_keys:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                    eco.aggregate[interval][source][1], "stats",
                                    TrendsNames.statisticsNames )

        #Write data and stats for gains/losses to db
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsAggGlgnData"
        else:
            tableName = TrendsNames.dbLocation + "CustomAggGlgnData"
            
        dbWriter = databaseWriteClass.aggGlgnWrite( gp, tableName)
        for interval in add_keys:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.aggGlgn[interval][source], "data", "" )

        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsAggGlgnStats"
        else:
            tableName = TrendsNames.dbLocation + "CustomAggGlgnStats"
            
        dbWriter = databaseWriteClass.aggGlgnWrite( gp, tableName)
        for interval in add_keys:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.aggGlgn[interval][source], "stats",
                                TrendsNames.statisticsNames )
                        
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
