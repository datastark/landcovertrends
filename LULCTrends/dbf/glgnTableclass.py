# glgnTableclass.py
# glgn dbf table builder class structure
#
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting, numpy
import os, sys, traceback, time, copy
from ..trendutil import TrendsNames
from . import TrendsStatCodes

from dbfclass import dBASEtable

class glgndBASEtable( dBASEtable ):

    def __init__( self, gp, glgn, numRows, numCols, resolution ):
        try:
            dBASEtable.__init__( self, gp, numRows, numCols, resolution )
            #Get data from source table into memory
            where_clause = "Glgn = \'" + glgn + "\'" + " and Resolution = \'" + self.resolution + "\'" + \
                           " and (Statistic = \'EstChange\' or Statistic = \'StdError\')"
            self.localTable = "local" + glgn
            self.extractDBStatistics( gp, "TrendsGlgnStats", self.localTable, where_clause )
            
        except arcgisscripting.ExecuteError:
            msgs = gp.GetMessage(0)
            msgs += gp.GetMessages(2)
            gp.AddMessage(msgs)
            raise
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
            
    def getTableValues( self, gp, numRows, numCols ):
        try:
            gp.OverwriteOutput = True

            for eco in range(1, TrendsNames.numEcoregions+1 ):
                stats = numpy.zeros((numRows, numCols), float)
                for interval in TrendsNames.TrendsIntervals:
                    ptr = TrendsNames.TrendsIntervals.index( interval )
                    ctrOffset = 0
                    #Get the estimated change values from the glgn table and store in array
                    where_clause = "EcoLevel3ID = " + str( eco ) + " and ChangePeriod = \'" + interval + "\'" + \
                                   " and Statistic = \'EstChange\'"
                    self.extractStatistics( gp, self.localTable, where_clause, stats, ptr, ctrOffset )

                    #Now get the standard error values from the glgn table
                    where_clause = "EcoLevel3ID = " + str( eco ) + " and ChangePeriod = \'" + interval + "\'" + \
                                   " and Statistic = \'StdError\'"
                    ctrOffset = TrendsNames.numLCtypes
                    self.extractStatistics( gp, self.localTable, where_clause, stats, ptr, ctrOffset )

                statReshaped = numpy.reshape( stats, [ numRows * numCols ])
                self.statSquared[eco-1,:] = statReshaped[:]

        except arcgisscripting.ExecuteError:
            msgs = gp.GetMessage(0)
            msgs += gp.GetMessages(2)
            gp.AddMessage(msgs)
            raise
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

class gaindBASEtable( glgndBASEtable ):
    def writeToTable(self, gp, folderForTables ):
        try:
            for ttype in dBASEtable.tableType:
                dbfTableName = "TRENDS_GAINS_" + self.resolution + "_" + ttype + "_" + dBASEtable.justdate + ".DBF"

                StandardErrorOmitted = False
                if ttype == "PERCENTOFCLASS":
                    StandardErrorOmitted = True
                #Create the new dbf table
                tableLoc, dbffields, dbfoffset = self.createDBASEtable( gp, dbfTableName, folderForTables,
                                                                   TrendsStatCodes.gainChangeCodes, StandardErrorOmitted )

                if ttype == "PIXEL":
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )

                if ttype == "SQKM":
                    holdTable = copy.deepcopy( self.statSquared)
                    self.statSquared = self.statSquared * self.sqkmFactor
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

                if ttype == "PERCENTOFECO":  #ECTP - total pixels in ecoregion
                    holdTable = copy.deepcopy( self.statSquared)
                    for eco in range( TrendsNames.numEcoregions ):
                        self.statSquared[eco, :] = self.statSquared[eco, :] / float(dBASEtable.ecoList[eco][3])
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

                if ttype == "PERCENTOFCLASS":
                    holdTable = copy.deepcopy( self.statSquared)
                    #Build the percentofclass table without any standard error
                    for statcol in range(TrendsNames.numLCtypes * len(TrendsNames.TrendsIntervals)):
                        intervalTotal = numpy.sum( self.statSquared[:, statcol] )
                        self.statSquared[:,statcol] = self.statSquared[:,statcol] / float(intervalTotal)
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

class lossdBASEtable( glgndBASEtable ):
    def writeToTable(self, gp, folderForTables ):
        try:
            for ttype in dBASEtable.tableType:
                dbfTableName = "TRENDS_LOSSES_" + self.resolution + "_" + ttype + "_" + dBASEtable.justdate + ".DBF"

                StandardErrorOmitted = False
                if ttype == "PERCENTOFCLASS":
                    StandardErrorOmitted = True
                #Create the new dbf table
                tableLoc, dbffields, dbfoffset = self.createDBASEtable( gp, dbfTableName, folderForTables,
                                                                   TrendsStatCodes.lossChangeCodes, StandardErrorOmitted )

                if ttype == "PIXEL":
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )

                if ttype == "SQKM":
                    holdTable = copy.deepcopy( self.statSquared)
                    self.statSquared = self.statSquared * self.sqkmFactor
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

                if ttype == "PERCENTOFECO":  #ECTP - total pixels in ecoregion
                    holdTable = copy.deepcopy( self.statSquared)
                    for eco in range( TrendsNames.numEcoregions ):
                        self.statSquared[eco, :] = self.statSquared[eco, :] / float(dBASEtable.ecoList[eco][3])
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

                if ttype == "PERCENTOFCLASS":
                    holdTable = copy.deepcopy( self.statSquared)
                    #Build the percentofclass table without any standard error
                    for statcol in range(TrendsNames.numLCtypes * len(TrendsNames.TrendsIntervals)):
                        intervalTotal = numpy.sum( self.statSquared[:, statcol] )
                        self.statSquared[:,statcol] = self.statSquared[:,statcol] / float(intervalTotal)
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

class grossdBASEtable( glgndBASEtable ):
    #define this just for gross since it adds an 'overall' class, which is the sum of all LC classes for
    #  the interval
    def getTableValues( self, gp, numRows, numCols ):
        try:
            gp.OverwriteOutput = True

            for eco in range(1, TrendsNames.numEcoregions+1 ):
                stats = numpy.zeros((numRows, numCols), float)  #make stats 2 rows longer for 'overall'
                gp.AddMessage('eco = ' + str(eco))
                for interval in TrendsNames.TrendsIntervals:
                    ptr = TrendsNames.TrendsIntervals.index( interval )
                    ctrOffset =  1  #leave room for the overall total at the front of the array
                    #Get the estimated change values from the glgn table and store in array
                    where_clause = "EcoLevel3ID = " + str( eco ) + " and ChangePeriod = \'" + interval + "\'" + \
                                   " and Statistic = \'EstChange\'"
                    self.extractStatistics( gp, self.localTable, where_clause, stats, ptr, ctrOffset )

                    #Add overall gross change to front of array
                    stats[0, ptr] = numpy.sum(stats[1:TrendsNames.numLCtypes ,ptr])

                    #Now get the standard error values from the glgn table
                    where_clause = "EcoLevel3ID = " + str( eco ) + " and ChangePeriod = \'" + interval + "\'" + \
                                   " and Statistic = \'StdError\'"
                    ctrOffset = TrendsNames.numLCtypes+2
                    self.extractStatistics( gp, self.localTable, where_clause, stats, ptr, ctrOffset )

                    #Add overall gross std error to front of error values
                    stats[TrendsNames.numLCtypes+1, ptr] = numpy.sum(stats[TrendsNames.numLCtypes+2: ,ptr])

                statReshaped = numpy.reshape( stats, [ numRows * numCols ])
                self.statSquared[eco-1,:] = statReshaped[:]

        except arcgisscripting.ExecuteError:
            msgs = gp.GetMessage(0)
            msgs += gp.GetMessages(2)
            gp.AddMessage(msgs)
            raise
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def writeToTable(self, gp, folderForTables ):
        try:
            for ttype in dBASEtable.tableType:
                dbfTableName = "TRENDS_GROSS_" + self.resolution + "_" + ttype + "_" + dBASEtable.justdate + ".DBF"

                StandardErrorOmitted = False
                if ttype == "PERCENTOFCLASS":
                    StandardErrorOmitted = True
                    continue
                #Create the new dbf table
                tableLoc, dbffields, dbfoffset = self.createDBASEtable( gp, dbfTableName, folderForTables,
                                                                   TrendsStatCodes.grossChangeCodes, StandardErrorOmitted )

                if ttype == "PIXEL":
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )

                if ttype == "SQKM":
                    holdTable = copy.deepcopy( self.statSquared)
                    self.statSquared = self.statSquared * self.sqkmFactor
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

                if ttype == "PERCENTOFECO":  #ECTP - total pixels in ecoregion
                    holdTable = copy.deepcopy( self.statSquared)
                    for eco in range( TrendsNames.numEcoregions ):
                        self.statSquared[eco, :] = self.statSquared[eco, :] / float(dBASEtable.ecoList[eco][3])
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

class netdBASEtable( glgndBASEtable ):
    def writeToTable(self, gp, folderForTables ):
        try:
            for ttype in dBASEtable.tableType:
                dbfTableName = "TRENDS_NET_" + self.resolution + "_" + ttype + "_" + dBASEtable.justdate + ".DBF"

                StandardErrorOmitted = False
                if ttype == "PERCENTOFCLASS":
                    StandardErrorOmitted = True
                    continue
                #Create the new dbf table
                tableLoc, dbffields, dbfoffset = self.createDBASEtable( gp, dbfTableName, folderForTables,
                                                                   TrendsStatCodes.netChangeCodes, StandardErrorOmitted )

                if ttype == "PIXEL":
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )

                if ttype == "SQKM":
                    holdTable = copy.deepcopy( self.statSquared)
                    self.statSquared = self.statSquared * self.sqkmFactor
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

                if ttype == "PERCENTOFECO":  #ECTP - total pixels in ecoregion
                    holdTable = copy.deepcopy( self.statSquared)
                    for eco in range( TrendsNames.numEcoregions ):
                        self.statSquared[eco, :] = self.statSquared[eco, :] / float(dBASEtable.ecoList[eco][3])
                    dBASEtable.writeToDBASEtable( self, gp, tableLoc, dbffields, dbfoffset )
                    self.statSquared = copy.deepcopy( holdTable)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

            
