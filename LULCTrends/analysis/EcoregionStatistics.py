# File EcoRegionStatistics.py
#
# Contains the functions that generate statistics for a given ecoregion and
#  interval and then stores both the raw data and the results in tables in the database.
#
# Written:         August 2010
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import arcgisscripting, numpy
import os, sys, traceback, time
from ..trendutil import TrendsNames, TrendsUtilities
from ..database import databaseWriteClass
from . import basicStatistics

#Calculate the statistics for the given ecoregion and interval.  Get the raw data from the data
# array and store the results in the statistics array.

def findTotalEstimatedPixels( eco, dataArray ):
    #Calculate the total estimated change in pixels for this data array (and interval).  This value
    # is used in statistics calculations to determine values as % of ecoregion.
    # It will be recalculated for special case years such as cumulative gross change, and then
    # set back to its original value
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        eco.totalEstPixels = numpy.sum( dataArray ) * (float(eco.totalBlks) / float( eco.sampleBlks))
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
        

def calculateEcoStatistics( eco, interval ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("start statistics on ecoregion " + str(eco.ecoNum) + " interval " \
                      + interval + "   " + time.asctime())

        #Check for N or n values out of range, since they are used
        # in the calculations.  They should be > 0 to avoid division by 0
        if eco.totalBlks <= 0 or eco.sampleBlks <= 0:
            raise TrendsUtilities.TrendsErrors("Invalid values, statistics aborted for ecoregion " + \
                                        str(eco.ecoNum)+" N= "+str(eco.totalBlks)+" n= "+str(eco.sampleBlks))

        basicStatistics.dataStats( eco, eco.numCon, eco.ecoData[ interval ][0], eco.ecoData[ interval ][1] )
    
    except TrendsUtilities.TrendsErrors, Terr:
        #Get errors specific to Trends execution
        trlog.trwrite( Terr.message )
        raise
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

#Store the raw data and results for this ecoregion and interval into 2 tables in the database.
# The runName is the analysis name for this processing run.
# Eco points to the ecoregion object, and interval is the change interval

def storeEcoStatistics( eco, interval, analysisNum ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        #Set up a log object
        trlog = TrendsUtilities.trLogger()        
        
        #  Get database table name
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsChangeData"
        else:
            tableName = TrendsNames.dbLocation + "CustomChangeData"
            
        dbWriter = databaseWriteClass.changeWrite( gp, tableName)
        dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution,
                                eco.ecoData[interval][0], "data", "" )
        
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsChangeStats"
        else:
            tableName = TrendsNames.dbLocation + "CustomChangeStats"
            
            
        dbWriter = databaseWriteClass.changeWrite( gp, tableName)
        dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution,
                                eco.ecoData[interval][1], "stats",
                                TrendsNames.statisticsNames )

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
