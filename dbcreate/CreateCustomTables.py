# File CreateCustomTables.py
#
#   Creates the 6 database tables to hold custom analysis data and stats
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

#Import modules
import os, sys, traceback
import arcgisscripting
from LULCTrends.trendutil import TrendsNames

def makeCustomTables():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #Custom Change Data table  
        tableName = "CustomChangeData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "BlkLabel","long")
        
        for trans in range( TrendsNames.numConversions ):
            gp.AddField( tableLoc, "CT_" + str(trans+1), "long")

        #Custom Change Stats table
        tableName = "CustomChangeStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Statistic", "text","20")

        for trans in range( TrendsNames.numConversions ):
            gp.AddField( tableLoc, "CT_" + str(trans+1), "double")

        #Custom Glgn Data table
        tableName = "CustomGlgnData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Glgn", "text", "10")
        gp.AddField( tableLoc, "BlkLabel","long")
        
        for trans in range( TrendsNames.numLCtypes ):
            gp.AddField( tableLoc, "LC_" + str(trans+1), "long")

        #Custom Glgn Stats table
        tableName = "CustomGlgnStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Glgn", "text", "10")
        gp.AddField( tableLoc, "Statistic", "text","20")

        for trans in range( TrendsNames.numLCtypes ):
            gp.AddField( tableLoc, "LC_" + str(trans+1), "double")

        #Custom Composition Data table
        tableName = "CustomCompData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "CompYear", "text","10")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "BlkLabel","long")
        
        for trans in range( TrendsNames.numLCtypes ):
            gp.AddField( tableLoc, "LC_" + str(trans+1), "long")

        #Custom Composition Stats table
        tableName = "CustomCompStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "CompYear", "text","10")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Statistic", "text","20")

        for trans in range( TrendsNames.numLCtypes ):
            gp.AddField( tableLoc, "LC_" + str(trans+1), "double")

        #Custom Multichange Data table  
        tableName = "CustomMultichangeData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "BlkLabel","long")
        
        for trans in range( TrendsNames.numMulti ) :
            gp.AddField( tableLoc, "Xchg_" + str(trans), "long")

        #Custom Multichange Stats table
        tableName = "CustomMultichangeStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Statistic", "text","20")

        for trans in range( TrendsNames.numMulti ) :
            gp.AddField( tableLoc, "Xchg_" + str(trans), "double")

    except arcgisscripting.ExecuteError:
        # Get the geoprocessing error messages
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise     #push the error up to exit

if __name__ == '__main__':
    makeCustomTables()
    print "Complete"
