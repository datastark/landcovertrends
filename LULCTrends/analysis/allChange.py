# File allChange.py
#
# In:   eco - ecoregion object
#       interval - change interval for calculations
#       analysisName - prefix for tables in database
#
# This set of functions creates the All Change values and their statistics for
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

import arcgisscripting
import os, sys, traceback, time, numpy
from ..database import databaseWriteClass
from . import basicStatistics
from .EcoregionStatistics import findTotalEstimatedPixels
from ..trendutil import TrendsNames, TrendsUtilities

def findChangeNumbers():
    #Return a list with the transition numbers for change only
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3) 
        gp.OverwriteOutput = True
        transTable = TrendsNames.dbLocation + "ClassTransition"
        where_clause = "IsNotChanged = 0"
        changeList = []

        #read in the class transition table screened for only change
        #Step through all the rows to read transition number
        rows = gp.SearchCursor( transTable, where_clause )
        row = rows.Next()
        while row:
            changeList.append( row.TransitionID )
            row = rows.Next()

        return changeList
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

def calcAllChange( eco ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Starting all change calculations   " + time.asctime())
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3) 
        gp.OverwriteOutput = True

        toFromList = findChangeNumbers()
        temp = numpy.zeros(( TrendsNames.numConversions, eco.sampleBlks ), int)

        for interval in eco.ecoData:
            #Calculate All Change for conversion arrays
            for index in range( TrendsNames.numConversions ):
                #Copy just change conversions into all change array
                if index+1 in toFromList:
                    temp[index,:] = eco.ecoData[ interval ][0][index,:]

            #Sum all the pixel values for each block and do statistics only on block totals
            eco.allChange[ interval ]['conversion'][0][:] = numpy.sum( temp, axis=0 )
            #Do the statistics
            basicStatistics.dataStats( eco,1,
                                        eco.allChange[ interval ]['conversion'][0],
                                        eco.allChange[ interval ]['conversion'][1] )

        #Now calculate for aggregate change, and change total pixel estimate yet again
        add_keys = eco.aggregate_gross_keys
        if add_keys:  #only calculate if an aggregate interval is defined for this data
            findTotalEstimatedPixels( eco, eco.aggregate[add_keys[0]]['gross'][0] )
            for key in add_keys:
                for index in range( TrendsNames.numConversions ):
                    #Copy just aggregate change into all change array
                    if index+1 in toFromList:
                        temp[index,:] = eco.aggregate[ key ]['gross'][0][index,:]

                #Sum all the pixel values for each block and do statistics only on block totals
                eco.allChange[ key ]['addgross'][0][:] = numpy.sum( temp, axis=0 )
                #Do the statistics
                basicStatistics.dataStats( eco,1,
                                            eco.allChange[ key ]['addgross'][0],
                                            eco.allChange[ key ]['addgross'][1] )                

            #Reset total pixel estimate (this needs to be cleaned up one day...)
            firstInterval = TrendsUtilities.getFirstInterval( eco )
            findTotalEstimatedPixels( eco, eco.ecoData[firstInterval][0] )

        #calculate AllChange for multichange
        for key in eco.ecoMulti:
            changes = TrendsNames.MultiMap[ key ]
            temp = numpy.zeros(( changes-1, eco.sampleBlks ), int)
            for index in range( 1, changes):
                temp[index-1,:] = eco.ecoMulti[key][0][index,:]
            eco.allChange[key]['multichange'][0][:] = numpy.sum( temp, axis=0 )
            basicStatistics.dataStats( eco,1,
                                        eco.allChange[ key ]['multichange'][0],
                                        eco.allChange[ key ]['multichange'][1] )                
        
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit


def storeAllChange( eco, analysisNum ):
    try:
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        #Write data and stats for allChange to db
        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsAllChangeData"
        else:
            tableName = TrendsNames.dbLocation + "CustomAllChangeData"
            
        source = 'conversion'
        dbWriter = databaseWriteClass.allChangeWrite( gp, tableName)
        for interval in eco.ecoData:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.allChange[interval][source][0], "data", "" )
        source = 'addgross'
        add_keys = eco.aggregate_gross_keys
        for interval in add_keys:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.allChange[interval][source][0], "data", "" )
        source = 'multichange'
        for interval in eco.ecoMulti:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.allChange[interval][source][0], "data", "" )

        if analysisNum == TrendsNames.TrendsNum:        
            tableName = TrendsNames.dbLocation + "TrendsAllChangeStats"
        else:
            tableName = TrendsNames.dbLocation + "CustomAllChangeStats"
            
        source = 'conversion'
        dbWriter = databaseWriteClass.allChangeWrite( gp, tableName)
        for interval in eco.ecoData:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.allChange[interval][source][1], "stats",
                                TrendsNames.statisticsNames )
        source = 'addgross'
        add_keys = eco.aggregate_gross_keys
        for interval in add_keys:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.allChange[interval][source][1], "stats",
                                TrendsNames.statisticsNames )
        source = 'multichange'
        for interval in eco.ecoMulti:
            dbWriter.databaseWrite( gp, analysisNum, eco, interval, eco.resolution, source,
                                eco.allChange[interval][source][1], "stats",
                                TrendsNames.statisticsNames )
                        
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
