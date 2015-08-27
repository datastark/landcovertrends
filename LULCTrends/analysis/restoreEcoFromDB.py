# restoreEcoFromDB.py
#
# reads in data and statistics for the given ecoregion
# and stores in the ecoregion object
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

import arcgisscripting
import os, sys, traceback, time
from ..database import databaseReadClass
from ..trendutil import TrendsNames, TrendsUtilities
from .setUpCalcStructures import setUpArrays

def loadEcoregion( eco ):
    try:
        gp = arcgisscripting.create(9.3)    
        gp.OverwriteOutput = True
        trlog = TrendsUtilities.trLogger()
        dataAvailable = True
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsChangeData"
        else:
            sourceName = "CustomChangeData"
        nointervals = []
        dbReader = databaseReadClass.changeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoData:
            dataFound = dbReader.databaseRead( gp, eco.analysisNum, eco, interval,
                                                   eco.resolution, eco.ecoData[interval][0],
                                                   "data", TrendsNames.statisticsNames)
            if not dataFound:
                nointervals.append( interval )
                dataAvailable = False
                trlog.trwrite("No data found for ecoregion " + str(eco.ecoNum) + " and interval " +\
                          str(interval))

        #Now remove intervals where no data was found
        for interval in nointervals:
            trlog.trwrite("Removing interval " + interval + " for ecoregion " + str(eco.ecoNum))
            del eco.ecoData[ interval ]
        #If some but not all intervals removed, reset 'datafound' flag
        if len(eco.ecoData) > 0:
            dataAvailable = True

        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsChangeStats"
        else:
            sourceName = "CustomChangeStats"
        dbReader = databaseReadClass.changeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoData:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval,
                                        eco.resolution, eco.ecoData[interval][1],
                                       "stats", TrendsNames.statisticsNames)
                
        #Now update the arrays for composition based on the intervals found
        folderList = eco.ecoData.keys()            
        currentyears = TrendsUtilities.getYearsFromIntervals( gp, folderList )
        compyears = eco.ecoComp.keys()
        for date in compyears:
            if not (date in currentyears):
                del eco.ecoComp[ date ]

        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsCompData"
        else:
            sourceName = "CustomCompData"
        dbReader = databaseReadClass.compositionRead( gp, TrendsNames.dbLocation + sourceName)
        for year in eco.ecoComp:
            dbReader.databaseRead( gp, eco.analysisNum, eco, year, eco.resolution,
                                             eco.ecoComp[year][0], "data", "")
                
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsCompStats"
        else:
            sourceName = "CustomCompStats"
        dbReader = databaseReadClass.compositionRead( gp, TrendsNames.dbLocation + sourceName)
        for year in eco.ecoComp:
            dbReader.databaseRead( gp, eco.analysisNum, eco, year, eco.resolution,
                                             eco.ecoComp[year][1], "stats", TrendsNames.statisticsNames)

        #Load multichange data where found.
        nointervals = []
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsMultichangeData"
        else:
            sourceName = "CustomMultichangeData"
        dbReader = databaseReadClass.multichangeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoMulti:
            dataFound = dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                       eco.ecoMulti[interval][0],"data", "")
            if not dataFound:
                nointervals.append( interval )
                trlog.trwrite("No multichange data found for ecoregion " + str(eco.ecoNum) + " and interval " +\
                          str(interval))

        #Now remove intervals where no data was found
        for interval in nointervals:
            trlog.trwrite("Removing multichange interval " + interval + " for ecoregion " + str(eco.ecoNum))
            del eco.ecoMulti[ interval ]

        #Remove aggregate intervals if this eco isn't within the data boundaries
        keylist = eco.aggregate_gross_keys
        compyears = eco.ecoComp.keys()
        for interval in keylist:
            ptr = eco.aggregate_gross_keys.index(interval)
            splitInfo = interval.split('to')
            start = splitInfo[0]
            end = splitInfo[1]
            if not (start in compyears) or not (end in compyears):
                del eco.aggregate_gross_keys[ptr]

        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsMultichangeStats"
        else:
            sourceName = "CustomMultichangeStats"
        dbReader = databaseReadClass.multichangeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoMulti:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                   eco.ecoMulti[interval][1],"stats", TrendsNames.statisticsNames)

        #Load the calculated data for glgn, all change and aggregate
        setUpArrays( eco )
                
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsGlgnData"
        else:
            sourceName = "CustomGlgnData"
        dbReader = databaseReadClass.glgnRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoGlgn:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                             eco.ecoGlgn[interval],"data", "")
                
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsGlgnStats"
        else:
            sourceName = "CustomGlgnStats"
        dbReader = databaseReadClass.glgnRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoGlgn:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                             eco.ecoGlgn[interval],
                                       "stats", TrendsNames.statisticsNames)

        source = 'gross'
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsAggregateData"
        else:
            sourceName = "CustomAggregateData"
        dbReader = databaseReadClass.aggregateRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.aggregate_gross_keys:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,source,
                                             eco.aggregate[interval][source][0],"data", "")
                    
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsAggregateStats"
        else:
            sourceName = "CustomAggregateStats"
        dbReader = databaseReadClass.aggregateRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.aggregate_gross_keys:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution, source,
                                             eco.aggregate[interval][source][1],
                                           "stats", TrendsNames.statisticsNames)

        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsAggGlgnData"
        else:
            sourceName = "CustomAggGlgnData"
        dbReader = databaseReadClass.aggGlgnRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.aggregate_gross_keys:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,source,
                                             eco.aggGlgn[interval][source],
                                       "data", "")
                    
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsAggGlgnStats"
        else:
            sourceName = "CustomAggGlgnStats"
        dbReader = databaseReadClass.aggGlgnRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.aggregate_gross_keys:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution, source,
                                             eco.aggGlgn[interval][source],
                                       "stats", TrendsNames.statisticsNames)

        sourceC = 'conversion'
        sourceA = 'addgross'
        sourceM = 'multichange'
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsAllChangeData"
        else:
            sourceName = "CustomAllChangeData"
        dbReader = databaseReadClass.allChangeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoData:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                       sourceC,
                                        eco.allChange[interval][sourceC][0],
                                       "data", "")
        for interval in eco.aggregate_gross_keys:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                       sourceA,
                                        eco.allChange[interval][sourceA][0],
                                       "data", "")
        for interval in eco.ecoMulti:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                   sourceM,
                                    eco.allChange[interval][sourceM][0],
                                   "data", "")
                    
        if eco.analysisNum == TrendsNames.TrendsNum:
            sourceName = "TrendsAllChangeStats"
        else:
            sourceName = "CustomAllChangeStats"
        dbReader = databaseReadClass.allChangeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in eco.ecoData:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                       sourceC, eco.allChange[interval][sourceC][1],
                                       "stats", TrendsNames.statisticsNames)
        for interval in eco.aggregate_gross_keys:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                       sourceA, eco.allChange[interval][sourceA][1],
                                       "stats", TrendsNames.statisticsNames)
        for interval in eco.ecoMulti:
            dbReader.databaseRead( gp, eco.analysisNum, eco, interval, eco.resolution,
                                    sourceM, eco.allChange[interval][sourceM][1],
                                   "stats", TrendsNames.statisticsNames)
        return dataAvailable
    except arcgisscripting.ExecuteError:
        # Get the geoprocessing error messages
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        trlog.trwrite(msgs)
        raise            
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
        raise  #push the error up to exit
