#Trends database write classes
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

class changeWrite ( TrendsDBaccess ):
    pass  #use TrendsDBaccess class as is
    
class compositionWrite ( TrendsDBaccess ):

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
                        " and CompYear = \'" + interval + "\'" + \
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
                    row.CompYear = interval
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

class glgnWrite ( TrendsDBaccess ):

    def databaseWrite( self, gp, analysisNum, eco, interval, resolution, data, content, statNames ):
        #defined for change/conversion table.  Overwritten for other tables.
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            for tabType in TrendsNames.glgnTabTypes:
                row = None
                if analysisNum == TrendsNames.TrendsNum:
                    #Check for existing rows in table
                    where_clause = "AnalysisNum = " + str(analysisNum) + \
                            " and EcoLevel3ID = " + str(eco.ecoNum) + \
                            " and ChangePeriod = \'" + interval + "\'" + \
                            " and Resolution = \'" + resolution + "\'" + \
                            " and Glgn = \'" + tabType + "\'"
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
                            dataTable = data[tabType][0]
                        else:
                            ctr = statNames.index( row.Statistic )
                            dataTable = data[tabType][1]
                        
                        for (ptr, field) in enumerate( self.fields[self.offset:]):
                            row.SetValue( field.Name, dataTable[ ptr, ctr ] )
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
                        row.Glgn = tabType
                        row.Resolution = resolution
                        if self.isNotSummary:
                            row.EcoLevel3ID = eco.ecoNum
                        row.ChangePeriod = interval
                        if content == "data":
                            row.BlkLabel = eco.stratBlocks[ ctr ]
                            dataTable = data[tabType][0]
                        else:
                            row.Statistic = statNames[ ctr ]
                            dataTable = data[tabType][1]
                        for (ptr, field) in enumerate( self.fields[self.offset:]):
                            row.SetValue( field.Name, dataTable[ ptr, ctr ] )
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

class multichangeWrite ( TrendsDBaccess ):
    pass  #use TrendsDBaccess class as is

class aggregateWrite ( TrendsDBaccess ):

    def databaseWrite( self, gp, analysisNum, eco, interval, resolution, source,
                       data, content, statNames ):
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            row = None
            if analysisNum == TrendsNames.TrendsNum:
                #Check for existing rows in table
                where_clause = "AnalysisNum = " + str(analysisNum) + \
                        " and EcoLevel3ID = " + str(eco.ecoNum) + \
                        " and ChangePeriod = \'" + interval + "\'" + \
                        " and Resolution = \'" + resolution + "\'" + \
                        " and Source = \'" + source + "\'"
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
                #  have ecoregion and resolution fields.  The var isNotSummary gets around this.
                rows = gp.InsertCursor( self.localTable )
                if content == 'data':
                    numVals = eco.sampleBlks
                else:
                    numVals = len( statNames)
                for ctr in range( numVals ):
                    row = rows.NewRow()
                    row.AnalysisNum = analysisNum
                    row.Resolution = resolution
                    row.Source = source
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

class allChangeWrite ( TrendsDBaccess ):

    def databaseWrite( self, gp, analysisNum, eco, interval, resolution, source,
                       data, content, statNames ):
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            row = None
            if analysisNum == TrendsNames.TrendsNum:
                #Check for existing rows in table
                where_clause = "AnalysisNum = " + str(analysisNum) + \
                        " and EcoLevel3ID = " + str(eco.ecoNum) + \
                        " and ChangePeriod = \'" + interval + "\'" + \
                        " and Resolution = \'" + resolution + "\'" + \
                        " and Source = \'" + source + "\'"
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
                #  have ecoregion and resolution fields.  The var isNotSummary gets around this.
                rows = gp.InsertCursor( self.localTable )
                if content == 'data':
                    numVals = eco.sampleBlks
                else:
                    numVals = len( statNames)
                for ctr in range( numVals ):
                    row = rows.NewRow()
                    row.AnalysisNum = analysisNum
                    row.Resolution = resolution
                    row.Source = source
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

class aggGlgnWrite ( TrendsDBaccess ):

    def databaseWrite( self, gp, analysisNum, eco, interval, resolution, source,
                       data, content, statNames ):
        #defined for change/conversion table.  Overwritten for other tables.
        try:
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            for tabType in TrendsNames.glgnTabTypes:
                row = None
                if analysisNum == TrendsNames.TrendsNum:
                    #Check for existing rows in table
                    where_clause = "AnalysisNum = " + str(analysisNum) + \
                            " and EcoLevel3ID = " + str(eco.ecoNum) + \
                            " and ChangePeriod = \'" + interval + "\'" + \
                            " and Resolution = \'" + resolution + "\'" + \
                            " and Source = \'" + source + "\'" + \
                            " and Glgn = \'" + tabType + "\'"
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
                            dataTable = data[tabType][0]
                        else:
                            ctr = statNames.index( row.Statistic )
                            dataTable = data[tabType][1]
                        
                        for (ptr, field) in enumerate( self.fields[self.offset:]):
                            row.SetValue( field.Name, dataTable[ ptr, ctr ] )
                        rows.UpdateRow( row )
                        row = rows.Next()
                else:
                    #Insert new rows in Trends - always insert for custom and summary table
                    #This writes to trends, custom, and summary tables, but the summary table doesn't
                    #  have ecoregion and resolution fields.  The var isNotSummary gets around this.
                    rows = gp.InsertCursor( self.localTable )
                    if content == 'data':
                        numVals = eco.sampleBlks
                    else:
                        numVals = len( statNames)
                    for ctr in range( numVals ):
                        row = rows.NewRow()
                        row.AnalysisNum = analysisNum
                        row.Glgn = tabType
                        row.Resolution = resolution
                        row.Source = source
                        if self.isNotSummary:
                            row.EcoLevel3ID = eco.ecoNum
                        row.ChangePeriod = interval
                        if content == "data":
                            row.BlkLabel = eco.stratBlocks[ ctr ]
                            dataTable = data[tabType][0]
                        else:
                            row.Statistic = statNames[ ctr ]
                            dataTable = data[tabType][1]
                        for (ptr, field) in enumerate( self.fields[self.offset:]):
                            row.SetValue( field.Name, dataTable[ ptr, ctr ] )
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
