# restoreSummaryFromDB.py
#
# reads in statistics for the given summary
# and stores in the summary object.  The
# empty arrays have already been created
#
# Written:         Aug 2011
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
from .setUpCalcStructures import setUpShortEcoArrays

def loadSummary( sa ):
    try:
        gp = arcgisscripting.create(9.3)    
        gp.OverwriteOutput = True
        trlog = TrendsUtilities.trLogger()
        where_clause = "AnalysisNum = " + str(sa.analysisNum) + \
                       " and Resolution = '" + str(sa.resolution) + "'"

        sourceName = "SummaryChangeStats"
        dbReader = databaseReadClass.changeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in sa.intervals:
            dbReader.databaseRead( gp, sa.analysisNum, 0, interval,
                                    sa.resolution, sa.summary[interval][1],
                                    "stats", TrendsNames.sumStatsNames)
                
        sourceName = "SummaryCompStats"
        dbReader = databaseReadClass.compositionRead( gp, TrendsNames.dbLocation + sourceName)
        for year in sa.years:
            dbReader.databaseRead( gp, sa.analysisNum, 0, year, sa.resolution,
                                    sa.sumcomp[year][1], "stats", TrendsNames.sumStatsNames)

        sourceName = "SummaryMultichangeStats"
        dbReader = databaseReadClass.multichangeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in sa.multiIntervals:
            datafound = dbReader.databaseRead( gp, sa.analysisNum, 0, interval, sa.resolution,
                                   sa.summulti[interval][1],"stats", TrendsNames.sumStatsNames)

        sourceName = "SummaryGlgnStats"
        dbReader = databaseReadClass.glgnRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in sa.intervals:
            dbReader.databaseRead( gp, sa.analysisNum, 0, interval, sa.resolution,
                                    sa.sumglgn[interval],
                                    "stats", TrendsNames.sumStatsNames)

        source = 'gross'                    
        sourceName = "SummaryAggregateStats"
        dbReader = databaseReadClass.aggregateRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in sa.aggIntervals:
            dbReader.databaseRead( gp, sa.analysisNum, 0, interval, sa.resolution, source,
                                    sa.sumaggregate[interval][source][1],
                                    "stats", TrendsNames.sumStatsNames)

        sourceName = "SummaryAggGlgnStats"
        dbReader = databaseReadClass.aggGlgnRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in sa.aggIntervals:
            dbReader.databaseRead( gp, sa.analysisNum, 0, interval, sa.resolution, source,
                                    sa.sumaggglgn[interval][source],
                                    "stats", TrendsNames.sumStatsNames)

        sourceC = 'conversion'
        sourceA = 'addgross'
        sourceM = 'multichange'
        sourceName = "SummaryAllChangeStats"
        dbReader = databaseReadClass.allChangeRead( gp, TrendsNames.dbLocation + sourceName)
        for interval in sa.intervals:
            dbReader.databaseRead( gp, sa.analysisNum, 0, interval, sa.resolution,
                                    sourceC, sa.sumallchange[interval][sourceC][1],
                                    "stats", TrendsNames.sumStatsNames)
        for interval in sa.aggIntervals:
            dbReader.databaseRead( gp, sa.analysisNum, 0, interval, sa.resolution,
                                       sourceA, sa.sumallchange[interval][sourceA][1],
                                       "stats", TrendsNames.sumStatsNames)

        for interval in sa.multiIntervals:
            dbReader.databaseRead( gp, sa.analysisNum, 0, interval, sa.resolution,
                                    sourceM, sa.sumallchange[interval][sourceM][1],
                                   "stats", TrendsNames.sumStatsNames)
            
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

def loadEcosForSummary( sa, ecoData ):
    try:
        gp = arcgisscripting.create(9.3)    
        gp.OverwriteOutput = True
        trlog = TrendsUtilities.trLogger()
        statList = ('EstChange','EstVar')

        def getoffset( source ):
            try:
                desc = gp.Describe( source )
                newfields = desc.Fields
                for ptr, field in enumerate(newfields):
                    if field.Name == "Statistic":
                        newoffset = ptr + 1
                return newfields, newoffset
            except Exception:
                raise
        def getrows( tabname, clause, fields, offset, data ):
            try:
                rows = gp.SearchCursor( tabname, clause )
                row = rows.Next()
                while row:
                    ctr = statList.index( row.Statistic )
                    for (ptr, field) in enumerate( fields[offset:]):
                        data[ ptr, ctr ] = row.GetValue( field.Name )
                    row = rows.Next()
            except Exception:
                raise

        customAnalysis = "Partial stratified" in [ecodat[9] for ecodat in ecoData]
        if customAnalysis:
            tableType = "Custom"
            analysisNum = sa.analysisNum
        else:
            tableType = "Trends"
            analysisNum = TrendsNames.TrendsNum
        ecoList = [x[0] for x in ecoData]        
        for ecoNum in ecoList:
            setUpShortEcoArrays( sa, ecoNum )
            where_clause = "AnalysisNum = " + str(analysisNum) + \
                        " and EcoLevel3ID = " + str(ecoNum) + \
                       " and Resolution = '" + str(sa.resolution) + "'" + \
                       " and (Statistic = 'EstChange' or Statistic = 'EstVar')"

            if tableType == "Trends":
                sourceName = TrendsNames.dbLocation + "TrendsChangeStats"
            else:
                sourceName = TrendsNames.dbLocation + "CustomChangeStats"
            fields, offset = getoffset( sourceName )
            for interval in sa.intervals:
                clause = where_clause + " and ChangePeriod = '" + interval + "'"
                getrows( sourceName, clause, fields, offset, sa.study[ecoNum].conv[interval] )

            if tableType == "Trends":
                sourceName = TrendsNames.dbLocation + "TrendsCompStats"
            else:
                sourceName = TrendsNames.dbLocation + "CustomCompStats"
            fields, offset = getoffset( sourceName )
            for year in sa.years:
                clause = where_clause + " and CompYear = '" + year + "'"
                getrows( sourceName, clause, fields, offset, sa.study[ecoNum].comp[year] )

            if tableType == "Trends":
                sourceName = TrendsNames.dbLocation + "TrendsMultichangeStats"
            else:
                sourceName = TrendsNames.dbLocation + "CustomMultichangeStats"
            fields, offset = getoffset( sourceName )
            for interval in sa.multiIntervals:
                getrows( sourceName, where_clause, fields, offset, sa.study[ecoNum].multi[interval] )

            if tableType == "Trends":
                sourceName = TrendsNames.dbLocation + "TrendsGlgnStats"
            else:
                sourceName = TrendsNames.dbLocation + "CustomGlgnStats"
            fields, offset = getoffset( sourceName )
            for interval in sa.intervals:
                for tab in TrendsNames.glgnTabTypes:
                    clause = where_clause + " and ChangePeriod = '" + interval + "'" + \
                             " and Glgn = \'" + tab + "\'" 
                    getrows( sourceName, clause, fields, offset, sa.study[ecoNum].glgn[interval][tab] )

            source = 'gross'                    
            if tableType == "Trends":
                sourceName = TrendsNames.dbLocation + "TrendsAggregateStats"
            else:
                sourceName = TrendsNames.dbLocation + "CustomAggregateStats"
            fields, offset = getoffset( sourceName )
            for interval in sa.aggIntervals:
                clause = where_clause + " and ChangePeriod = '" + interval + "'" + \
                        " and Source = '" + source + "'"
                getrows( sourceName, clause, fields, offset, sa.study[ecoNum].aggregate[interval][source] )

            if tableType == "Trends":
                sourceName = TrendsNames.dbLocation + "TrendsAggGlgnStats"
            else:
                sourceName = TrendsNames.dbLocation + "CustomAggGlgnStats"
            fields, offset = getoffset( sourceName )
            for interval in sa.aggIntervals:
                for tab in TrendsNames.glgnTabTypes:
                    clause = where_clause + " and ChangePeriod = '" + interval + "'" + \
                             " and Source = '" + source + "'" + " and Glgn = \'" + tab + "\'" 
                    getrows( sourceName, clause, fields, offset, sa.study[ecoNum].aggGlgn[interval][source][tab] )

            sourceC = 'conversion'
            sourceA = 'addgross'
            sourceM = 'multichange'
            if tableType == "Trends":
                sourceName = TrendsNames.dbLocation + "TrendsAllChangeStats"
            else:
                sourceName = TrendsNames.dbLocation + "CustomAllChangeStats"
            fields, offset = getoffset( sourceName )
            for interval in sa.intervals:
                clause = where_clause + " and ChangePeriod = '" + interval + "'" + \
                        " and Source = '" + sourceC + "'"
                getrows( sourceName, clause, fields, offset, sa.study[ecoNum].allchg[interval][sourceC] )

            for interval in sa.aggIntervals:
                clause = where_clause + " and ChangePeriod = '" + interval + "'" + \
                        " and Source = '" + sourceA + "'"
                getrows( sourceName, clause, fields, offset, sa.study[ecoNum].allchg[interval][sourceA] )

            for interval in sa.multiIntervals:
                clause = where_clause + " and ChangePeriod = '" + interval + "'" + \
                        " and Source = '" + sourceM + "'"
                getrows( sourceName, clause, fields, offset, sa.study[ecoNum].allchg[interval][sourceM] )
            
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
