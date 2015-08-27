# File CreateSampleBlocksTable.py
#
#   Creates the SampleBlocks table and populates it
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

def makeSampleBlockTable():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        numEcoregions = 84

        #Custom Change Data table  
        tableName = "SampleBlocks"
        gp.CreateTable( TrendsNames.dbTemplate[:-1], tableName )
        tableLoc = os.path.join( TrendsNames.dbTemplate, tableName)

        gp.AddField( tableLoc, "Ecoregion", "long")
        gp.AddField( tableLoc, "SampleBlock", "long")

        #Just pick one interval and resolution in order to get a list of sample blocks
        changeTab = TrendsNames.dbLocation + "ChangeImage"
        interval = '1973to1980'
        res = '60m'
        blocks = {}
        for eco in range(numEcoregions):
            where_clause = "EcoLevel3ID = " + str(eco+1) + \
                    " and ChangePeriod = \'" + interval + "\'" + \
                    " and Resolution = \'" + res + "\'"
        
            blocks[eco+1] = []
            #Get the block numbers from the table and count the number of samples
            rows = gp.SearchCursor( changeTab, where_clause )
            row = rows.Next()
            while row:
                blocks[eco+1].append( row.BlkLabel )
                row = rows.Next()
            del row, rows

        #Add the ecoregions and sample block numbers to the new table
        rows = gp.InsertCursor( tableLoc )
        for eco in blocks:
            for entry in blocks[eco]:
                row = rows.NewRow()
                row.Ecoregion = eco
                row.SampleBlock = entry
                rows.InsertRow( row)
        del row, rows

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
    makeSampleBlockTable()
    print "Complete"
