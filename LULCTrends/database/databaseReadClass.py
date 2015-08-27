#Trends database read classes
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
from LULCTrends.database.databaseAccessClass import TrendsDBaccess
from ..trendutil import TrendsNames, TrendsUtilities

class changeRead ( TrendsDBaccess ):
    try:
        pass  #use TrendsDBaccess class as is
    except Exception:
        raise
    
class compositionRead ( TrendsDBaccess ):

    def setTrendsQueryValues( self ):
        try:
            if self.isNotSummary:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and EcoLevel3ID = " + str(self.eco.ecoNum) + \
                        " and CompYear = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'"
            else:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and CompYear = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'"                
            sortFields = ""
            return where_clause, sortFields
        except Exception:
            raise

class glgnRead ( TrendsDBaccess ):

    def getTheRows( self, gp, where_clause, sortFields ):
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            for tabType in TrendsNames.glgnTabTypes:
                temp_clause = where_clause + " and Glgn = \'" + tabType + "\'"
                rows = gp.SearchCursor( self.localTable, temp_clause, "", "", sortFields )
                row = rows.Next()
                if row is not None:
                    dataFound = True
                    while row:
                        if self.content == 'data':
                            ctr = self.eco.column[ row.BlkLabel ]
                            localData = self.data[ tabType ][0]
                        else:
                            ctr = self.statNames.index( row.Statistic )
                            localData = self.data[ tabType ][1]
                        for (ptr, field) in enumerate( self.fields[self.offset:]):
                            localData[ ptr, ctr ] = row.GetValue( field.Name )
                        row = rows.Next()
                else:
                    dataFound = False
            return dataFound
        except arcgisscripting.ExecuteError:
            msgs = gp.GetMessage(0)
            msgs += gp.GetMessages(2)
            trlog.trwrite(msgs)
            raise
        except TrendsUtilities.TrendsErrors, Terr:
            trlog.trwrite( Terr.message )
            raise
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            trlog.trwrite(pymsg)
            raise
        finally:
            try:
                del row, rows
            except Exception:
                pass

class multichangeRead ( TrendsDBaccess ):
    pass  #use TrendsDBaccess class as is

class aggregateRead ( TrendsDBaccess ):  #same as allchange read

    def databaseRead( self, gp, analysisNum, eco, interval, resolution,
                      source, data, content, statNames ):
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            self.analysisNum = analysisNum
            self.resolution = resolution
            self.eco = eco
            self.interval = interval
            self.data = data             #2-dim array for table values
            self.content = content       #indicator of data or stats array
            self.statNames = statNames
            where_clause, sortFields = self.setTrendsQueryValues( source )
            return self.getTheRows( gp, where_clause, sortFields )
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            trlog.trwrite(pymsg)
            raise

    def setTrendsQueryValues( self, source ):
        try:
            if self.isNotSummary:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and EcoLevel3ID = " + str(self.eco.ecoNum) + \
                        " and ChangePeriod = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'" + \
                        " and Source = \'" + source + "\'"
            else:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and ChangePeriod = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'" + \
                        " and Source = \'" + source + "\'"

            sortFields = ""
            return where_clause, sortFields
        except Exception:
            raise

class allChangeRead ( aggregateRead ):
    try:
        pass  #use aggregate class as is
    except Exception:
        raise


class aggGlgnRead ( glgnRead ): #use glgnRead getTheRows and add below methods

    def databaseRead( self, gp, analysisNum, eco, interval, resolution,
                      source, data, content, statNames ):
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            self.analysisNum = analysisNum
            self.resolution = resolution
            self.eco = eco
            self.interval = interval
            self.data = data             #2-dim array for table values
            self.content = content       #indicator of data or stats array
            self.statNames = statNames
            where_clause, sortFields = self.setTrendsQueryValues( source )
            return self.getTheRows( gp, where_clause, sortFields )
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            trlog.trwrite(pymsg)
            raise

    def setTrendsQueryValues( self, source ):
        try:
            if self.isNotSummary:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and EcoLevel3ID = " + str(self.eco.ecoNum) + \
                        " and ChangePeriod = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'" + \
                        " and Source = \'" + source + "\'"
            else:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and ChangePeriod = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'" + \
                        " and Source = \'" + source + "\'"
            sortFields = ""
            return where_clause, sortFields
        except Exception:
            raise
