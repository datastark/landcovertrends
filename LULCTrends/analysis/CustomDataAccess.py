# File CustomDataAccess.py
#
# In:   custom boundary of study area
#       resolution for this analysis
#       analysis name to store shapefiles under
#       folder for results
# Out:  lists of ecoregions and sample blocks in study area
#       shapefiles in result folder
#
# Note: the splits list was initially meant for blocks that were
#       split by custom boundary, but only stratified analysis is
#       currently used.
#
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

def accessCustomData( custom_boundary, resolution, nameForFile, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverWriteOutput = True
        #Go through the block shapefiles attribute table and pick
        #  up the ecoregion numbers used in this analysis,
        #  Initialize a dictionary with eco# as the key and a
        #  placeholder for total block count and sample block count

        ecoregions = {}
        totalblocks = {}
        sampleblocks = {}
        splits = {}

        #Find out which blocks from the 10k and 20k total block grids are in the study area
        new10kland = outFolder + os.path.sep + nameForFile + "_10k_land.shp"
        new20kland = outFolder + os.path.sep + nameForFile + "_20k_land.shp"
        block10k = outFolder + os.path.sep + nameForFile + "_10k_blocks.shp"
        block20k = outFolder + os.path.sep + nameForFile + "_20k_blocks.shp"
        new10kcoast = outFolder + os.path.sep + nameForFile + "_10k_coast.shp"
        new20kcoast = outFolder + os.path.sep + nameForFile + "_20k_coast.shp"
        sampleset = outFolder + os.path.sep + nameForFile + "_samples.shp"
        lyrfile = 'lyr'
        lyrfile10k = 'lyr10k'
        lyrfile20k = 'lyr20k'

        #Select the total 10k blocks whose centroid falls within the boundary
        All_10k = TrendsNames.dbLocation + "Ecoregion_10k_national"
        gp.MakeFeatureLayer_management( All_10k, lyrfile )
        gp.SelectLayerByLocation_management( lyrfile, 'HAVE_THEIR_CENTER_IN', custom_boundary )
        gp.CopyFeatures_management( lyrfile, new10kland )

        #Extract the numbers of the ecoregions in the study area
        rows = gp.SearchCursor( lyrfile )
        row = rows.Next()
        while row:
            if not (int(row.ECOREG_10K) in totalblocks):
                totalblocks[ int(row.ECOREG_10K) ] = []
            totalblocks[ int(row.ECOREG_10K) ].append( int(row.SAMPLE_10K) )
            row = rows.Next()

        #Select the total 20k blocks whose centroid falls within the boundary
        All_20k = TrendsNames.dbLocation + "Ecoregion_20k_national"
        gp.MakeFeatureLayer_management( All_20k, lyrfile )
        gp.SelectLayerByLocation_management( lyrfile, 'HAVE_THEIR_CENTER_IN', custom_boundary )
        gp.CopyFeatures_management( lyrfile, new20kland )

        #Extract the numbers of the ecoregions in the study area
        rows = gp.SearchCursor( lyrfile )
        row = rows.Next()
        while row:
            if not (int(row.ECOREG) in totalblocks):
                totalblocks[ int(row.ECOREG) ] = []
            totalblocks[ int(row.ECOREG) ].append( int(row.BLOCK) )
            row = rows.Next()

        #Check for a coastline boundary to catch blocks that miss because a centroid
        # falls over a water area.
        Coastal = TrendsNames.dbLocation + "Coastal_total_10k"
        gp.MakeFeatureLayer_management( Coastal, lyrfile )
        gp.SelectLayerByLocation_management( lyrfile, 'INTERSECT', custom_boundary )
        gp.SelectLayerByLocation_management( lyrfile, 'CONTAINS', new10kland,
                                             "", "REMOVE_FROM_SELECTION" )
        gp.CopyFeatures_management( lyrfile, new10kcoast )
        gp.Append_management( new10kcoast, new10kland, "NO_TEST" )

        #Extract the numbers of the ecoregions in the study area
        rows = gp.SearchCursor( lyrfile )
        row = rows.Next()
        while row:
            if (int(row.ECOREG_10K) in totalblocks):
                if not (int(row.SAMPLE_10K) in totalblocks[ int(row.ECOREG_10K) ]):
                    totalblocks[ int(row.ECOREG_10K) ].append( int(row.SAMPLE_10K) )
            row = rows.Next()

        Coastal = TrendsNames.dbLocation + "Coastal_total_20k"
        gp.MakeFeatureLayer_management( Coastal, lyrfile )
        gp.SelectLayerByLocation_management( lyrfile, 'INTERSECT', custom_boundary )
        gp.SelectLayerByLocation_management( lyrfile, 'CONTAINS', new20kland,
                                             "", "REMOVE_FROM_SELECTION" )
        gp.CopyFeatures_management( lyrfile, new20kcoast )
        gp.Append_management( new20kcoast, new20kland, "NO_TEST" )

        #Extract the numbers of the ecoregions in the study area
        rows = gp.SearchCursor( lyrfile )
        row = rows.Next()
        while row:
            if (int(row.ECOREG) in totalblocks):
                if not (int(row.BLOCK) in totalblocks[ int(row.ECOREG) ]):
                    totalblocks[ int(row.ECOREG) ].append( int(row.BLOCK) )
            row = rows.Next()
        
        #For each ecoregion in the ecoregions list, open the sampleblock
        #table and get the sample block numbers.
        sourceName = TrendsNames.dbLocation + "SampleBlocks"
        gp.Overwriteoutput = True
        gp.MakeFeatureLayer_management( new10kland, lyrfile10k )
        gp.MakeFeatureLayer_management( new20kland, lyrfile20k )
        
        logfile = False
        try:
            logfile = open( os.path.join( outFolder, "ecoregions_totals_samples.txt"), 'w')
        except Exception:
            pass
        for eco in totalblocks:
            #get this ecoregion's info from sample block table
            sampleblocks[ eco ] = []
            where_clause = "Ecoregion = " + str( eco )
            rows = gp.SearchCursor( sourceName, where_clause )
            row = rows.Next()
            while row:
                if row.SampleBlock in totalblocks[ eco ]:
                    sampleblocks[ eco ].append( row.SampleBlock )
                row = rows.Next()

            msg = "Ecoregion " + str(eco) + ": Total blocks = " + str(len(totalblocks[eco])) + \
                          "  Sample blocks = " + str(len(sampleblocks[eco]))
            gp.AddMessage(msg)
            if logfile:
                logfile.write( msg + "\n" )

            #Make selections of all total blocks whose ecoregions contain at least
            # one sample block and then copy these into the resulting shapefile.
            if len( sampleblocks[eco]) > 0:
                ecoregions[ eco ] = (len(totalblocks[eco]), len(sampleblocks[eco]), resolution, "Partial stratified")
                if eco in TrendsNames.Ecos_20k:
                    where_block = "ECOREG = " + str( eco )
                    gp.SelectLayerByAttribute_management( lyrfile20k,"ADD_TO_SELECTION",where_block )
                else:
                    where_block = "ECOREG_10K = " + str( eco )
                    gp.SelectLayerByAttribute_management( lyrfile10k,"ADD_TO_SELECTION",where_block )
            else:
                del sampleblocks[eco]

        #only create the output total block file(s) if there's any total blocks in the study area
        count10k = gp.GetCount_management( lyrfile10k )
        count20k = gp.GetCount_management( lyrfile20k )

        if int(count10k.GetOutput(0)) > 0:
            gp.CopyFeatures_management( lyrfile10k, block10k )
        if int(count20k.GetOutput(0)) > 0:
            gp.CopyFeatures_management( lyrfile20k, block20k )

        #Make a shapefile of the sample blocks as well
        if len( sampleblocks ) > 0:
            All_samples = TrendsNames.dbLocation + "samples_all_us"
            lyrsamples = 'lyrsamp'
            gp.MakeFeatureLayer_management( All_samples, lyrsamples )
            for eco in sampleblocks:
                for block in sampleblocks[eco]:
                    if eco in TrendsNames.Ecos_20k:
                        where_block = "SAMPLE_10K = " + str( block ) + " and ECOREG_20K = " + str(eco) 
                        gp.SelectLayerByAttribute_management( lyrsamples,"ADD_TO_SELECTION",where_block )
                    else:
                        where_block = "ECOREG_10K = " + str(eco) + " and SAMPLE_10K = " + str( block )
                        gp.SelectLayerByAttribute_management( lyrsamples,"ADD_TO_SELECTION",where_block )
            gp.CopyFeatures_management( lyrsamples, sampleset )
                
        #delete work files
        if gp.Exists( new10kland ):
            gp.Delete( new10kland )
        if gp.Exists( new20kland ):
            gp.Delete( new20kland )
        if gp.Exists( new10kcoast ):
            gp.Delete( new10kcoast )
        if gp.Exists( new20kcoast ):
            gp.Delete( new20kcoast )

        return ecoregions, sampleblocks, splits

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
        raise
    except Exception:
        gp.AddMessage(traceback.format_exc())
        raise
    finally:
        try:
            if logfile:
                logfile.close()
        except Exception:
            pass
        try:
            del row, rows
        except Exception:
            pass

