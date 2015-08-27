# File CreateAllChangeTables.py
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

def makeAllChangeTables():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #Trends All Change Data table  
        tableName = "TrendsAllChangeData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "BlkLabel","long")
        gp.AddField( tableLoc, "Total", "long")

        #Trends All Change Stats table
        tableName = "TrendsAllChangeStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "Statistic", "text","20")
        gp.AddField( tableLoc, "Total", "double")

        #Custom AllChange Data table  
        tableName = "CustomAllChangeData"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "BlkLabel","long")
        gp.AddField( tableLoc, "Total", "long")

        #Custom AllChange Stats table
        tableName = "CustomAllChangeStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)
        
        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "EcoLevel3ID", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "Statistic", "text","20")
        gp.AddField( tableLoc, "Total", "double")

        #Summary All Change Stats table  
        tableName = "SummaryAllChangeStats"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        gp.AddField( tableLoc, "AnalysisNum", "long")
        gp.AddField( tableLoc, "ChangePeriod", "text","15")
        gp.AddField( tableLoc, "Resolution", "text","10")
        gp.AddField( tableLoc, "Source", "text", "20")
        gp.AddField( tableLoc, "Statistic", "text","20")
        gp.AddField( tableLoc, "Total", "double")

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
    makeAllChangeTables()
    print "Complete"
