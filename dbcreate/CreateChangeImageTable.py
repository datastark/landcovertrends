# CreateChangeImageTable.py
#
# Creates the  table for indexing the change images.
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

def createChangeImageTable():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #Create table names for ecoregion table and stratified block table
        tableName = "ChangeImage"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        #Add the fields for the ecoregion table
        gp.AddField( tableLoc, "EcoLevel3ID", "long" )
        gp.AddField( tableLoc, "BlkLabel", "long" )
        gp.AddField( tableLoc, "SampleBlkID", "text", "20" )
        gp.AddField( tableLoc, "ChangePeriod", "text", "15" )
        gp.AddField( tableLoc, "Resolution", "text", "10")
        gp.AddField( tableLoc, "ImageLocation", "text", "255")

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise     #push the error up to exit

if __name__ == '__main__':
    try:
        createChangeImageTable()
        print "Complete"
    except Exception:
        pass
