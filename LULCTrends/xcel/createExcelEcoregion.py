# createExcelEcoregion.py
#
# Creates an ecoregion container for excel file builder
# Methods include initialization to create an ecoregion
# object and loading of ecoregion data from db.
#
# Written:         July 2011
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
import os, sys, traceback
from ..trendutil import TrendsUtilities, TrendsNames
from ..analysis.restoreEcoFromDB import loadEcoregion
from ..analysis import createRegionStats

STATS = createRegionStats.EcoStats

class EcoExcel( createRegionStats.EcoStats ):

    def __init__(self, gp, ecoNum, N, n, res, intervals, years, multiIntervals, analysisNum ):
        try:
            self.ecoNum = ecoNum
            self.analysisNum = analysisNum
            self.totalBlks = N
            self.sampleBlks = n
            self.resolution = res
            self.ecoData = {}
            self.ecoGlgn = {}
            self.ecoComp = {}
            self.allChange = {}
            self.aggregate = {}
            self.aggGlgn = {}
            self.ecoMulti = {}
            self.aggregate_gross_keys = TrendsNames.aggregate_gross_interval
            self.column = self.getBlockNumbers( gp, ecoNum, analysisNum, years )

            for folder in intervals:
                self.ecoData[ folder ] = ( numpy.zeros(( STATS.numCon, self.sampleBlks ), int),
                                        numpy.zeros(( STATS.numCon, STATS.numStats ), float))

            for date in years:
                self.ecoComp[ date ] = ( numpy.zeros(( TrendsNames.LCTypecntr, self.sampleBlks ), int),
                                        numpy.zeros(( TrendsNames.LCTypecntr, self.numStats ), float))

            for interval in multiIntervals:
                self.ecoMulti[ interval ] = ( numpy.zeros(( TrendsNames.numMulti, self.sampleBlks ), int),
                                            numpy.zeros(( TrendsNames.numMulti, STATS.numStats ), float))

        except arcgisscripting.ExecuteError:
            raise            
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def getBlockNumbers( self, gp, ecoNum, analysisNum, years ):
        try:
            #Make a dictionary that maps the sample block numbers to the
            #  array column numbers.  If sample block list = [16, 18, 21]
            #  then
            #  self.column = {16:0, 18:1, 21:2}
            if analysisNum == TrendsNames.TrendsNum:
                tableName = TrendsNames.dbLocation + "TrendsCompData"
            else:
                tableName = TrendsNames.dbLocation + "CustomCompData"
            where_clause = "AnalysisNum = " + str(analysisNum) + \
                           " and EcoLevel3ID = " + str(self.ecoNum) + \
                           " and CompYear = '" + str(years[0]) + "'" + \
                           " and Resolution = '" + str(self.resolution) + "'"
            field = "BlkLabel"
            sortFields = "BlkLabel A"
            samples = []
            rows = gp.SearchCursor( tableName, where_clause, "", field, sortFields )
            row = rows.Next()
            while row:
                samples.append( row.BlkLabel )
                row = rows.Next()
            del row, rows
            return dict( zip( samples, [x for x in range( len(samples))]))
        except arcgisscripting.ExecuteError:
            raise            
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise            

    def loadDataAndStatisticsTables( self, gp ):
        try:            
            #Set up a log object
            dataFound = loadEcoregion( self )
            return dataFound
        except arcgisscripting.ExecuteError:
            raise            
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def buildHeaders( self, gp ):
        try:            
            sheader = TrendsNames.statprintNames
            samples = self.column.keys()
            samples.sort()
            dheader = [ str(self.ecoNum) + "-" + str(block) for block in samples ]
            return dheader,sheader
        except arcgisscripting.ExecuteError:
            raise            
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
