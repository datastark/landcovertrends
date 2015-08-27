# File TrendsDataAccess.py
#
# In:   text string containing the ecoregion numbers for this summary
#       table name to store the block info in
#       resolution for this analysis
# Out:  lists of ecoregions and sample blocks in analysis
#
#       Gets the sample blocks for each ecoregion in the input list
#       Note: the splits list is not currently used
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright
#
import arcgisscripting, os, sys, traceback
from ..trendutil import TrendsNames

def accessTrendsData( eco_list, runNum, resolution ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverWriteOutput = True
        #  Initialize a dictionary with eco# as the key and a
        #  placeholder for total block count and sample block count
        ecoregions = {}
        strats = {}
        splits = {}
        for eco in eco_list:
            ecoregions[ eco ] = 0
            strats[ eco ] = []

        #For each ecoregion in the ecoregions list, open the ecoregions
        #table and get the number of total blocks.
            
        SamplesTable = TrendsNames.dbLocation + "SampleBlocks"
        EcosTable = TrendsNames.dbLocation + "Ecoregions"
        for eco in ecoregions:
            #Make a query to get this ecoregion's info from ecoregion table
            where_clause = "Ecoregion = " + str( eco )
            rows = gp.SearchCursor( EcosTable, where_clause )
            row = rows.Next()
            #The desired ecoregion should be the only entry in this table
            ecoregions[ eco ] = (row.Total_Blocks, row.num_samples, resolution, "Full stratified" )
            gp.AddMessage("Ecoregion " + str(eco) + ": Total blocks = " + str(ecoregions[eco][0]) + \
                          "  Sample blocks = " + str(ecoregions[eco][1]))

        for eco in ecoregions:
            where_clause = "Ecoregion = " + str( eco )
            srows = gp.SearchCursor( SamplesTable, where_clause )
            srow = srows.Next()
            while srow:
                strats[ eco ].append(srow.SampleBlock)
                srow = srows.Next()

        return ecoregions, strats, splits

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddError(msgs)
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddError(pymsg)
    finally:
        try:
            del row,rows
            del srow, srows
        except Exception:
            pass

