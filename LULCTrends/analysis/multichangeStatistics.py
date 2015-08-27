# File multichangeStatistics.py
#
# Contains the functions that generate statistics for a given ecoregion and
#  then stores both the raw data and the results in tables in the database.
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
import arcgisscripting
import os, sys, traceback, time
from ..database import databaseWriteClass
from . import basicStatistics
from ..trendutil import TrendsNames, TrendsUtilities

#Calculate the statistics for the given ecoregion.  Get the raw data from the data
# array and store the results in the statistics array.

def calcMultichangeStats( eco, interval ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("start multichange statistics on ecoregion " + str(eco.ecoNum) + \
                      " and interval " + interval + "   " + time.asctime())

        for interval in eco.ecoMulti:
            basicStatistics.dataStats( eco, TrendsNames.numMulti, eco.ecoMulti[interval][0],
                                       eco.ecoMulti[interval][1] )

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit


#Store the raw data and results for this ecoregion into tables in the database.
# Eco points to the ecoregion object, and analysisNum is the number assigned to the analysis run name

def storeMultichange( eco, interval, analysisNum ):
    try:
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        
        #  Get database table name
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsMultichangeData"
        else:
            tableName = TrendsNames.dbLocation + "CustomMultichangeData"

        dbWriter = databaseWriteClass.multichangeWrite( gp, tableName )
        dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution,
                                eco.ecoMulti[interval][0], "data", "" )
        
        #  Get database table name
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsMultichangeStats"
        else:
            tableName = TrendsNames.dbLocation + "CustomMultichangeStats"
        
        dbWriter = databaseWriteClass.multichangeWrite( gp, tableName )
        dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution,
                                eco.ecoMulti[interval][1], "stats", TrendsNames.statisticsNames )
        
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
