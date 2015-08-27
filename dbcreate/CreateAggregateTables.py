# File CreateAggregateTables.py
#
#   Creates the 6 database tables to hold trends ecosystem data and stats
#
# Written:         Oct 2010
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

def makeAggregateTables():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #Trends Aggregate Data table  
        tableName = "TrendsAggregateData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "BlkLabel","long")
        
        for trans in range( TrendsNames.numConversions ):
            gp.AddField( tableLoc, "CT_" + str(trans+1), "long")

        #Trends Aggregate Stats table
        tableName = "TrendsAggregateStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "Statistic", "text","20")

        for trans in range( TrendsNames.numConversions ):
            gp.AddField( tableLoc, "CT_" + str(trans+1), "double")

        #Custom Aggregate Data table  
        tableName = "CustomAggregateData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "BlkLabel","long")
        
        for trans in range( TrendsNames.numConversions ):
            gp.AddField( tableLoc, "CT_" + str(trans+1), "long")

        #Custom Aggregate Stats table
        tableName = "CustomAggregateStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "Statistic", "text","20")

        for trans in range( TrendsNames.numConversions ):
            gp.AddField( tableLoc, "CT_" + str(trans+1), "double")

        #Summary Aggregate Stats table
        tableName = "SummaryAggregateStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "Statistic", "text","20")

        for trans in range( TrendsNames.numConversions ):
            gp.AddField( tableLoc, "CT_" + str(trans+1), "double")

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
    makeAggregateTables()
    print "Complete"
