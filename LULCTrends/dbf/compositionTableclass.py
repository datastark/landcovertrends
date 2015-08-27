# compositionTableclass.py
# composition dbf table builder class structure
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

class compdBASEtable( dBASEtable ):

    def __init__( self, gp, numRows, numCols, resolution ):
        try:
            dBASEtable.__init__( self, gp, numRows, numCols, resolution )
            #Get data from source table into memory
            where_clause = "Resolution = \'" + self.resolution + "\'" + \
                           " and (Statistic = \'EstChange\' or Statistic = \'StdError\')"
            self.localTable = "localComp"
            self.extractDBStatistics( gp, "TrendsCompStats", self.localTable, where_clause )
            
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
            
    #fill in for composition tables
    def getTableValues( self, gp, numRows, numCols ):
        try:
            gp.OverwriteOutput = True

            for eco in range(1, TrendsNames.numEcoregions+1 ):
                stats = numpy.zeros((numRows, numCols), float)
                gp.AddMessage('eco = ' + str(eco))
                for year in TrendsNames.TrendsYears:
                    ptr = TrendsNames.TrendsYears.index( year )
                    ctrOffset = 0
                    #Get the estimated change values from the comp table and store in array
                    where_clause = "EcoLevel3ID = " + str( eco ) + " and CompYear = \'" + year + "\'" + \
                                   " and Statistic = \'EstChange\'"
                    self.extractStatistics( gp, self.localTable, where_clause, stats, ptr, ctrOffset )

                    #Now get the standard error values from the comp table
                    where_clause = "EcoLevel3ID = " + str( eco ) + " and CompYear = \'" + year + "\'" + \
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

    def writeToTable(self, gp, folderForTables ):
        try:
            for ttype in dBASEtable.tableType:
                dbfTableName = "TRENDS_COMPOSITION_" + self.resolution + "_" + ttype + "_" + dBASEtable.justdate + ".DBF"

                StandardErrorOmitted = False
                if ttype == "PERCENTOFCLASS":
                    StandardErrorOmitted = True
                    continue  #not used with composition
                #Create the new dbf table
                tableLoc, dbffields, dbfoffset = self.createDBASEtable( gp, dbfTableName, folderForTables,
                                                                   TrendsStatCodes.compositionCodes, StandardErrorOmitted )

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


            
