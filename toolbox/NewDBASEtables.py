#GenerateDBASEtables.py
#
# In:   list of tables to be generated
#       resolution
#       folder for results
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

import arcgisscripting
import os, sys, traceback
from LULCTrends.dbf import dbfBuilder

def makeDBASEtables( tempList, resolution, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        
        tableList = [ table.strip("\'") for table in tempList ]
        for table in tableList:
            gp.AddMessage(table)

        dbfBuilder.createDBFtables( tableList, resolution, outFolder )

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
    except Exception:
        gp.AddMessage(traceback.format_exc())

if __name__ == "__main__":
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverWriteOutput = True
        tempList = gp.GetParameterAsText(0).split(';')
        resolution = gp.GetParameterAsText(1)
        outFolder = gp.GetParameterAsText(2)
        makeDBASEtables( tempList, resolution, outFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
