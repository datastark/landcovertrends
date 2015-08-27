# File getChangeData.py
#
# In:   the ecoregion object to load data into
#       the change interval to get the data for
# Out:  true or false, depending on if any data was loaded for this interval
#
# For a given ecoregion (or partial region) and change interval
#  and resolution, extract the names of the
#  change image files needed for this analysis from the ChangeImage
#  table of the database and load the pixel counts for
#  each conversion into the conversion array for this ecoregion.
#  Pixel counts are loaded by opening the attribute table for each
#  selected change image and reading the conversion numbers and
#  corresponding pixel counts.
#
#  There could be two lists of sample blocks as input parameters to
#  this function.  listOfSamples is the list containing the sample
#  block numbers for full sample blocks.  This is the initial mode of
#  analysis, which uses a stratified sample block approximation to the
#  study region.  Eventually, sample blocks that fall along study region
#  boundaries may be clipped and the pixel counts recalculated for the
#  block portion within the region.  The list of these block numbers is
#  in listOfSplits, and for these blocks, the conversion number and pixel
#  count will be retrieved from a temporary table that contains
#  the split counts.
#  Sliver blocks are contained within the change image of the corresponding
#  sample block, so the pixel counts in the sample block change image already
#  include the counts from any associated sliver blocks.
#
# Written:         July 2010
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import arcgisscripting, os, sys, traceback
from ..trendutil import TrendsNames, TrendsUtilities

def loadChangeImageData( eco, interval ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        trlog.trwrite("Loading data for ecoregion " + str(eco.ecoNum) + " and interval " + interval)

        #Make a query table from the database
        #The table is the changeImage table, and
        # only rows with the given ecoregion number, resolution, 
        # and change interval are selected from ChangeImage for this table view
        tableName = TrendsNames.dbLocation + "ChangeImage"
        where_clause = "EcoLevel3ID = " + str(eco.ecoNum) + \
                " and ChangePeriod = \'" + interval + "\'" + \
                " and Resolution = \'" + eco.resolution + "\'"
        sort_fields = "BlkLabel A"

        #Step through all the rows and find the block numbers
        # that are in the list of sample blocks
        #For those blocks, get the filename and store in a dictionary
        #  with the filename. format = {block:filename, block:filename, ...}
        changeFiles = {}
        rows = gp.SearchCursor( tableName, where_clause, "", "", sort_fields )
        row = rows.Next()
        while row:
            if row.BlkLabel in eco.stratBlocks:
                changeFiles[ row.BlkLabel ] = row.ImageLocation
            row = rows.Next()

        if len( changeFiles ) > eco.sampleBlks:
            trlog.trwrite("Found " + str(len(changeFiles)) + " change files but expected only " + str(eco.sampleBlks))
            raise TrendsUtilities.TrendsErrors("More block images found than expected - unable to process ecoregion")

        trlog.trwrite( "N= "+str(eco.totalBlks)+" n= "+str(eco.sampleBlks))
        if (len( changeFiles ) < eco.sampleBlks) and (eco.runType == "Full stratified"):
            trlog.trwrite("WARNING: found only " + str(len(changeFiles)) + " images in the change image table")
            
        #For each filename in the list, open its attribute table and read in the
        # conversion number and count columns. Add this to the array
        for block in changeFiles :
            rows = gp.SearchCursor( changeFiles[ block ] )
            row = rows.Next()
            while row:
                if row.Count > 0 and row.Value > 0 and row.Value <= eco.numCon:
                    eco.ecoData[interval][0][ row.Value - 1, eco.column[ block ]] = int( row.Count )
                row = rows.Next()
        #For each block in the list of split blocks,
        #  read the conversion numbers for each block from the table for this ecoregion and interval
        #The split blocks have already been screened for interval and resolution
        #  If there are blocks in the split list, then they are ready to load (TBD)

        #Send an acknowledgment back that there was data found for
        #  this interval at this resolution
        # If changeFiles or eco.splitBlocks contain block numbers,
        #  the value returned will be TRUE.  If they are both empty, FALSE is returned
        return (changeFiles or eco.splitBlocks)
    
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        trlog.trwrite(msgs)
        raise
    except TrendsUtilities.TrendsErrors, Terr:
        trlog.trwrite( Terr.message )
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise
    finally:
        try:
            del row, rows
        except Exception:
            pass


def loadMultiChangeData( eco, multiInterval ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Loading multichange data for ecoregion " + str(eco.ecoNum) + \
                      " and interval " + multiInterval)
        
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #Make a query from the database
        #The table is the MultiChangeImage table, and
        # only rows with the given ecoregion number and resolution 
        # are selected from ChangeImage for this table view
        tableName = TrendsNames.dbLocation + "MultiChangeImage"
        where_clause = "EcoLevel3ID = " + str(eco.ecoNum) + \
                " and ChangePeriod = \'" + multiInterval + "\'" + \
                " and Resolution = \'" + eco.resolution + "\'"
        sort_fields = "BlkLabel A"

        #Step through all the rows and find the block numbers
        # that are in the list of sample blocks
        #For those blocks, get the filename and store in a dictionary
        #  with the filename. format = {block:filename, block:filename, ...}
        changeFiles = {}
        rows = gp.SearchCursor( tableName, where_clause, "", "", sort_fields )
        row = rows.Next()
        while row:
            if row.BlkLabel in eco.stratBlocks:
                changeFiles[ row.BlkLabel ] = row.ImageLocation
            row = rows.Next()

        #Find the number of change intervals for this interval
        changes = TrendsNames.MultiMap[ multiInterval ]

        #For each filename in the list, open its attribute table and read in the
        # multichange number and count columns. Add this to the array
        for block in changeFiles :
            rows = gp.SearchCursor( changeFiles[ block ] )
            row = rows.Next()
            while row:
                if row.Count > 0 and row.Value >= 0 and row.Value <= changes:
                    eco.ecoMulti[multiInterval][0][ row.Value, eco.column[ block ]] = int( row.Count )
                row = rows.Next()
        #For each block in the list of split blocks,
        #  read the conversion numbers for each block from the table for this ecoregion and interval
        #The split blocks have already been screened for interval and resolution
        #  If there are blocks in the split list, then they are ready to load (TBD)

        #Send an acknowledgment back that there was data found at this resolution
        # If changeFiles or eco.splitBlocks contain block numbers,
        #  the value returned will be TRUE.  If they are both empty, FALSE is returned
        return (changeFiles or eco.splitBlocks)

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        trlog.trwrite(msgs)
        raise
    except TrendsUtilities.TrendsErrors, Terr:
        trlog.trwrite( Terr.message )
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise
    finally:
        try:
            del row, rows
        except Exception:
            pass
