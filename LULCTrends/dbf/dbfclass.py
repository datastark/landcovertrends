# dbf table builder class structure
#
# Written:         Jan 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting, numpy
import os, sys, traceback, time
from ..trendutil import TrendsNames
from . import TrendsStatCodes

class dBASEtable:
    tableType = ["PIXEL","SQKM","PERCENTOFECO","PERCENTOFCLASS" ]
    ecoList = []
    justdate = ""

    def __init__(self, gp, numRows, numCols, resolution  ):
        try:
            #create the arrays to hold data for this table
            self.statSquared = numpy.zeros((TrendsNames.numEcoregions, numRows*numCols), float)
            self.resolution = resolution

            if resolution == "60m":
                self.sqkmFactor = 0.0036
            else:  # 30m resolution
                self.sqkmFactor = 0.0009
            
            #Get the ecoregion info and timestamp if necessary
            if not dBASEtable.ecoList:
                dBASEtable.ecoList = dBASEtable.getEcoregionInfo( self )
            if not dBASEtable.justdate:
                tmstp = time.localtime()
                dBASEtable.justdate = str(tmstp.tm_mon).rjust(2).replace(" ","0") + \
                            str(tmstp.tm_mday).rjust(2).replace(" ","0") + str(tmstp.tm_year)
                
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def getEcoregionInfo(self):
        try:
            gp = arcgisscripting.create(9.3)
            gp.OverwriteOutput = True

            #read in the general values from the Ecoregion table
            ecotable = TrendsNames.dbLocation + "Ecoregions"
            ecoList = []
            rows = gp.SearchCursor( ecotable )
            row = rows.Next()
            while row:
                ecoList.append( [row.Ecoregion, row.Total_Blocks, row.num_samples, row.TotalPixels,
                            row.num_samples-1, row.StudentT_85, row.StudentT_90, row.StudentT_95,
                            row.StudentT_99] )
                row = rows.Next()
            return ecoList
            
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
        finally:
            try:
                del row, rows
            except Exception:
                pass

    def createDBASEtable(self, gp, tableName, folder, codes, noSE = False ):
        try:
            #Create the dBASE table in the given folder
            tableLoc = os.path.join( folder, tableName)

            gp.AddMessage("Creating table " + tableLoc + "   " + time.asctime())
            if gp.Exists( tableLoc ):
                gp.Delete( tableLoc )
            gp.CreateTable( folder, tableName )

            #Add the ecoregion general data columns
            gp.AddField( tableLoc,"ECNM", "double" )
            gp.AddField( tableLoc,"ECTB", "long" )
            gp.AddField( tableLoc,"ECSB", "long" )
            gp.AddField( tableLoc,"ECTP", "double" )
            gp.AddField( tableLoc,"ECDF", "long" )
            gp.AddField( tableLoc,"ECST85", "double" )
            gp.AddField( tableLoc,"ECST90", "double" )
            gp.AddField( tableLoc,"ECST95", "double" )
            gp.AddField( tableLoc,"ECST99", "double" )
            
            #Add the columns for this particular table
            for code in codes:
                if noSE and code.count("SE"):  #some tables don't get SE values
                    break
                gp.AddField( tableLoc, code, "double" )

            #Delete esri's default field
            gp.DeleteField( tableLoc, "FIELD1" )

            #Get a list of the new field names so they can be iterated through
            desc = gp.Describe( tableLoc )
            dbffields = desc.Fields
            for ptr, field in enumerate(dbffields):
                if field.Name == "ECST99":
                    dbfoffset = ptr
                    
            return tableLoc, dbffields, dbfoffset
        
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

    def extractStatistics(self, gp, sourceTable, where_clause, stats, ptr, ctrOffset ):
        try:
            desc = gp.Describe( sourceTable )
            sourcefields = desc.Fields
            for counter, field in enumerate(sourcefields):
                if field.Name == "Statistic":
                    sourceoffset = counter + 1
                                       
            rows = gp.SearchCursor( sourceTable, where_clause )
            row = rows.Next()
            while row:
                for (ctr, field) in enumerate( sourcefields[sourceoffset:]):
                    stats[ ctr + ctrOffset, ptr ] = row.GetValue( field.Name )
                row = rows.Next()
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
        finally:
            try:
                del row, rows
            except Exception:
                pass

    def extractDBStatistics(self, gp, sourceName, localName, where_clause ):
        #create a table view of the data for quicker extraction
        try:
            sourceTable = TrendsNames.dbLocation + sourceName
            gp.AddMessage("Retrieving data from " + sourceTable)
            gp.Overwriteoutput = True
            gp.MakeQueryTable_management( sourceTable, localName,"USE_KEY_FIELDS","","",where_clause )

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

    def writeToDBASEtable(self, gp, tableLoc, dbffields, dbfoffset ):
        try:
            rows = gp.InsertCursor( tableLoc )
            for eco in range(1, TrendsNames.numEcoregions+1 ):
                row = rows.NewRow()
                for (ctr, field) in enumerate( dbffields[1:]):
                    if ctr < dbfoffset:  #put in general ecoregion info
                        row.SetValue( field.Name, dBASEtable.ecoList[eco-1][ctr])
                    else:
                        row.SetValue( field.Name, self.statSquared[eco-1, ctr-dbfoffset] )
                rows.InsertRow( row )
        
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
        finally:
            try:
                del row, rows
            except Exception:
                pass

    def getTableValues ( self, gp, numRows, numCols ):   #each table type fills this one in
        gp.AddMessage("method getTableValues is not defined in a subclass")

    def writeToTable(self, gp, folderForTables ):        #and this one
        gp.AddMessage("method writeToTable is not defined in a subclass")


