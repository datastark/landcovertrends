#dbfBuilder.py
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting
import os, sys, traceback
from ..trendutil import TrendsNames
from . import TrendsStatCodes
from .dbfclass import dBASEtable
from .glgnTableclass import glgndBASEtable, gaindBASEtable, lossdBASEtable, grossdBASEtable, netdBASEtable
from .compositionTableclass import compdBASEtable
from .multichangeTableclass import multidBASEtable
from .conversionTableclass import changedBASEtable, errordBASEtable

def createDBFtables( tableList, resolution, folderForTables ):
    try:
        gp = arcgisscripting.create(9.3)
        
        if "ConversionChange" in tableList:
            changeTable = changedBASEtable( gp,
                                        TrendsNames.numConversions,
                                        len(TrendsNames.TrendsIntervals),
                                        resolution )
            changeTable.getTableValues( gp, TrendsNames.numConversions,len(TrendsNames.TrendsIntervals))
            changeTable.writeToTable( gp, folderForTables )
            del changeTable
        if "ConversionError" in tableList:
            errorTable = errordBASEtable( gp,
                                        TrendsNames.numConversions,
                                        len(TrendsNames.TrendsIntervals),
                                        resolution )
            errorTable.getTableValues( gp, TrendsNames.numConversions,len(TrendsNames.TrendsIntervals))
            errorTable.writeToTable( gp, folderForTables )
            del errorTable
        if "Composition" in tableList:
            compTable = compdBASEtable( gp,
                                        TrendsNames.numLCtypes * 2,
                                        len(TrendsNames.TrendsYears),
                                        resolution )
            compTable.getTableValues( gp, TrendsNames.numLCtypes * 2,len(TrendsNames.TrendsYears))
            compTable.writeToTable( gp, folderForTables )
            del compTable
        if "Gains" in tableList:
            gainTable = gaindBASEtable( gp, 'gain',
                                        TrendsNames.numLCtypes * 2,
                                        len(TrendsNames.TrendsIntervals),
                                        resolution )
            gainTable.getTableValues( gp, TrendsNames.numLCtypes * 2,len(TrendsNames.TrendsIntervals))
            gainTable.writeToTable( gp, folderForTables )
            del gainTable
        if "Losses" in tableList:
            lossTable = lossdBASEtable( gp, 'loss',
                                        TrendsNames.numLCtypes * 2,
                                        len(TrendsNames.TrendsIntervals),
                                        resolution )
            lossTable.getTableValues( gp, TrendsNames.numLCtypes * 2,len(TrendsNames.TrendsIntervals))
            lossTable.writeToTable( gp, folderForTables )
            del lossTable
        if "Gross" in tableList:
            grossTable = grossdBASEtable( gp, 'gross',
                                        (TrendsNames.numLCtypes+1) * 2, #make longer for 'overall' class
                                        len(TrendsNames.TrendsIntervals),
                                        resolution )
            grossTable.getTableValues( gp, (TrendsNames.numLCtypes+1) * 2,len(TrendsNames.TrendsIntervals))
            grossTable.writeToTable( gp, folderForTables )
            del grossTable
        if "Net" in tableList:
            netTable = netdBASEtable( gp, 'net',
                                        TrendsNames.numLCtypes * 2,
                                        len(TrendsNames.TrendsIntervals),
                                        resolution )
            netTable.getTableValues( gp, TrendsNames.numLCtypes * 2,len(TrendsNames.TrendsIntervals))
            netTable.writeToTable( gp, folderForTables )
            del netTable
        if "Multichange" in tableList:
            multiTable = multidBASEtable( gp,
                                        TrendsNames.numMulti * 2,
                                        1,  #currently only 1973-2000 used in tables
                                        resolution )
            multiTable.getTableValues( gp, TrendsNames.numMulti * 2,1)
            multiTable.writeToTable( gp, folderForTables )
            del multiTable
        gp.AddMessage( "Complete" )
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)
