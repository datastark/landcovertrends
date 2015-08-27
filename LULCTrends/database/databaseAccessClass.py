#Trends database access class
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
from ..trendutil import TrendsNames, TrendsUtilities

class TrendsDBaccess:

    def __init__(self, gp, localTable ):
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            #Get a list of the new field names so they can be iterated through
            self.localTable = localTable
            desc = gp.Describe( localTable )
            self.fields = desc.Fields
            self.isNotSummary = True in [ field.Name == "EcoLevel3ID" for field in self.fields ]
            
            for ptr, field in enumerate(self.fields):
                if field.Name == "BlkLabel" or field.Name == "Statistic":
                    self.offset = ptr + 1
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
            raise

    def setTrendsQueryValues( self ):
        #This is defined to work for change/conversion data and stats, should be
        #  overwritten in subclasses for other table types
        try:
            if self.isNotSummary:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and EcoLevel3ID = " + str(self.eco.ecoNum) + \
                        " and ChangePeriod = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'"
            else:
                where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                        " and ChangePeriod = \'" + self.interval + "\'" + \
                        " and Resolution = \'" + self.resolution + "\'"
            sortFields = ""
            return where_clause, sortFields
        except Exception:
            raise

    def getTheRows( self, gp, where_clause, sortFields ):
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            rows = gp.SearchCursor( self.localTable, where_clause, "", "", sortFields )
            row = rows.Next()
            if row is not None:
                dataFound = True
                while row:
                    if self.content == 'data':
                        ctr = self.eco.column[ row.BlkLabel ]
                    else:
                        ctr = self.statNames.index( row.Statistic )
                    for (ptr, field) in enumerate( self.fields[self.offset:]):
                        self.data[ ptr, ctr ] = row.GetValue( field.Name )
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

    def databaseRead( self, gp, analysisNum, eco, interval, resolution, data, content, statNames):
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
            where_clause, sortFields = self.setTrendsQueryValues()
            return self.getTheRows( gp, where_clause, sortFields )
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            trlog.trwrite(pymsg)
            raise

    def databaseWrite( self, gp, analysisNum, eco, interval, resolution, data, content, statNames ):
        #defined for change/conversion table.  Overwritten for other tables.
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            row = None
            if analysisNum == TrendsNames.TrendsNum:
                #Check for existing rows in table
                where_clause = "AnalysisNum = " + str(analysisNum) + \
                        " and EcoLevel3ID = " + str(eco.ecoNum) + \
                        " and ChangePeriod = \'" + interval + "\'" + \
                        " and Resolution = \'" + resolution + "\'"
                if content == "data":
                    sortFields = "BlkLabel A"
                else:
                    sortFields = ""

                rows = gp.UpdateCursor( self.localTable, where_clause, "", "", sortFields )
                row = rows.Next()  #Get the first row
                
            if row is not None:  #found rows so update existing rows
                while row:
                    if content == 'data':
                        ctr = eco.column[ row.BlkLabel ]
                    else:
                        ctr = statNames.index( row.Statistic )
                    
                    for (ptr, field) in enumerate( self.fields[self.offset:]):
                        row.SetValue( field.Name, data[ ptr, ctr ] )
                    rows.UpdateRow( row )
                    row = rows.Next()
            else:
                #Insert new rows in Trends - always insert for custom and summary table
                #This writes to trends, custom, and summary tables, but the summary table doesn't
                #  have ecoregion field.  The var isNotSummary gets around this.
                rows = gp.InsertCursor( self.localTable )
                if content == 'data':
                    numVals = eco.sampleBlks
                else:
                    numVals = len( statNames)
                for ctr in range( numVals ):
                    row = rows.NewRow()
                    row.AnalysisNum = analysisNum
                    row.Resolution = resolution
                    if self.isNotSummary:
                        row.EcoLevel3ID = eco.ecoNum
                    row.ChangePeriod = interval
                    if content == "data":
                        row.BlkLabel = eco.stratBlocks[ ctr ]
                    else:
                        row.Statistic = statNames[ ctr ]
                    for (ptr, field) in enumerate( self.fields[self.offset:]):
                        row.SetValue( field.Name, data[ ptr, ctr ] )
                    rows.InsertRow( row )
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
            raise
        finally:
            try:
                del row, rows
            except Exception:
                pass
