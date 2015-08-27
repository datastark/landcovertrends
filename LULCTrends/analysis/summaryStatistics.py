# File sa.summaryStatistics.py
#
# In:   study -dictionary containing each ecoregion object,
#       keyed by the ecoregion numbers
#       num - key for data belonging to this
#               study
#
# Out:  sa.summary table additions for each interval to the database containing sa.summary
#       statistics for the change images
#
# Takes each ecoregion object and extracts the estimated change
#  and estimated variance columns from their statistics arrays.
#  These columns are added together and form the basis for the
#  rest of the sa.summary statistics in the sa.summary table.
#
# Written:         Sep 2010
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import arcgisscripting, os, sys, traceback, time
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
import numpy
from ..trendutil import TrendsNames, TrendsUtilities
from . import UpdateAnalysisParams
from ..database import databaseWriteClass
from . import basicSummaryStatistics
from .setUpCalcStructures import setUpSummaryArrays

#Calculate the sa.summary statistics for all ecoregions in the study area.
#Get the estimated change and estimated variance from the statistics arrays
# for each ecoregion and add together.  Calculate other columns in the
# sa.summary from these two columns.  Then store all to database.

def genSummaryStats( sa, analysisNum ):
    try:
        #Create the geoprocessor object
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("starting summary statistics   " + time.asctime())
        
        for eco in sa.study:
            sa.summarySamples += sa.study[ eco ].sampleBlks
            sa.totalBlocks += sa.study[ eco ].totalBlks
        trlog.trwrite("Total sample blocks in summary statistics: " + str(sa.summarySamples))
        
        #Get the student's T values for 15%, 10%, 5%, and 1% quantiles
        # Values are contained in studentT[0] - [3].  R returns a one-tailed t
        # value, so use 7.5%, 5%, 2.5%, and .5% for 2-tailed.
        degreesFreedom = sa.summarySamples - 1
        r_qt = robjects.r['qt']
        if sa.summarySamples > 1:
            sa.studentT = r_qt(robjects.FloatVector([.925, .95, .975, .995]), degreesFreedom)
        else:
            sa.studentT = [-9999.99, -9999.99, -9999.99, -9999.99]
        tempstr = "Student T values for study area: %0.3f  %0.3f  %0.3f  %0.3f" %(sa.studentT[0],sa.studentT[1],sa.studentT[2],sa.studentT[3])
        trlog.trwrite( tempstr )
        
        for eco in sa.study:    #count up the total estimated pixels for all ecoregions
            sa.sumEstPixels += sa.study[ eco ].totalEstPixels
        trlog.trwrite("Total estimated pixels in summary statistics: " + str(sa.sumEstPixels))
        
        #Find the number of intervals to use for this sa.summary. Find the eco in the study with the fewest
        # intervals and make this the sa.summary interval list.
        tempList = []
        ecos = sa.study.keys()
        intervals = os.listdir( TrendsNames.changeImageFolders )
        for eco in ecos:
            tempList.extend( [x for x in intervals if x not in sa.study[eco].ecoData.keys()] )

        #Determine which multichange intervals are common to all ecos in study area
        # and fall within the change image data range.
        sa.intervals = [ x for x in intervals if x not in tempList ]
        for interval in sa.intervals:
            trlog.trwrite("summary interval: " + interval)
        sa.years = TrendsUtilities.getYearsFromIntervals( gp, sa.intervals )

        #Find the common multichange intervals within the Trends data intervals window
        tempintervals = sa.intervals
        tempList = []
        for eco in ecos:
            tempList.extend( [x for x in tempintervals if x not in sa.study[eco].ecoMulti.keys()] )
        sa.multiIntervals = [ x for x in tempintervals if x not in tempList ]
            
        #create and initialize arrays for the stats, multichange array is currently initialized in studyareaclass
        setUpSummaryArrays( sa )

        #Set the resolution for the sa.summary to the max of any eco in study
        sa.resolution = TrendsNames.minResolution
        for eco in sa.study:
            if sa.study[eco].resolution != TrendsNames.minResolution:
                sa.resolution = TrendsNames.maxResolution
                
        #get all the summary stats added up
        addAllSummaryStats( sa )

        #calculate the statistics
        calcAllSummaryStats( sa )

        #store the tables to the database
        storeAllSummaryStats( gp, sa )
        
        #Write general analysis parameters to supplemental table
        tableName = "SummaryAnalysisParams"
        UpdateAnalysisParams.updateParameters( tableName, analysisNum, 0, sa.summarySamples, sa.totalBlocks, sa.sumEstPixels,
                                               sa.studentT[0],sa.studentT[1],sa.studentT[2],sa.studentT[3], sa.resolution)
        
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def addAllSummaryStats( sa ):
    try:
        trlog = TrendsUtilities.trLogger()
        for eco in sa.study:
            for interval in sa.intervals:
            
                #for each interval, add the estimated change column and estimated
                #variance columns.  Est change is in the 2nd
                #column of reach ecoregion's statistics array and est variance is in the
                #5th column.  See statName definition in createRegionStats.py.
                #The [1] in region[folder][1][:,1] is pointing to the statistics array.
                #The notation ':' with a numpy array performs the operation item by
                #item in the column.
                #First column is total change
                #Total change = sum (est. change columns for each ecoregion) (pixels)
                #Second column is total variance
                #Total variance = sum (est. variance columns for each ecoregion) (pixels)
                
                sa.summary[ interval ][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                         sa.study[ eco ].ecoData[ interval ][1][:,sa.study[eco].statName.index('EstChange')]
                sa.summary[ interval ][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                         sa.study[ eco ].ecoData[ interval ][1][:,sa.study[eco].statName.index('EstVar')]

                for tabType in TrendsNames.glgnTabTypes:
                    sa.sumglgn[ interval ][ tabType ][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                             sa.study[eco].ecoGlgn[ interval ][ tabType ][1][:,sa.study[eco].statName.index('EstChange')]
                    
                    sa.sumglgn[ interval ][ tabType ][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                             sa.study[eco].ecoGlgn[ interval ][ tabType ][1][:,sa.study[eco].statName.index('EstVar')]

                sa.sumallchange[ interval ]['conversion'][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                         sa.study[ eco ].allChange[ interval ]['conversion'][1][:,sa.study[eco].statName.index('EstChange')]
                sa.sumallchange[ interval ]['conversion'][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                         sa.study[ eco ].allChange[ interval ]['conversion'][1][:,sa.study[eco].statName.index('EstVar')]
   
            for year in sa.years:
                # Now sum est change( really composition ) and variance for composition data
                sa.sumcomp[ year ][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                         sa.study[ eco ].ecoComp[ year ][1][:,sa.study[eco].statName.index('EstChange')]
                sa.sumcomp[ year ][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                         sa.study[ eco ].ecoComp[ year ][1][:,sa.study[eco].statName.index('EstVar')]

            #Sum est change and variance for aggregated gross change
            for key in TrendsNames.aggregate_gross_interval:
                sa.sumallchange[ key ]['addgross'][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                         sa.study[ eco ].allChange[ key ]['addgross'][1][:,sa.study[eco].statName.index('EstChange')]
                sa.sumallchange[ key ]['addgross'][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                         sa.study[ eco ].allChange[ key ]['addgross'][1][:,sa.study[eco].statName.index('EstVar')]

                sa.sumaggregate[ key ]['gross'][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                         sa.study[ eco ].aggregate[ key ]['gross'][1][:,sa.study[eco].statName.index('EstChange')]
                sa.sumaggregate[ key ]['gross'][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                         sa.study[ eco ].aggregate[ key ]['gross'][1][:,sa.study[eco].statName.index('EstVar')]

                for tabType in TrendsNames.glgnTabTypes:
                    sa.sumaggglgn[ key ]['gross'][ tabType ][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                             sa.study[eco].aggGlgn[ key ]['gross'][ tabType ][1][:,sa.study[eco].statName.index('EstChange')]
                    
                    sa.sumaggglgn[ key ]['gross'][ tabType ][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                             sa.study[eco].aggGlgn[ key ]['gross'][ tabType ][1][:,sa.study[eco].statName.index('EstVar')]


            #Now sum est change and variance for multichange data
            for key in sa.multiIntervals:
                sa.summulti[key][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                                            sa.study[eco].ecoMulti[key][1][:,sa.study[eco].statName.index('EstChange')]
                sa.summulti[key][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                                            sa.study[eco].ecoMulti[key][1][:,sa.study[eco].statName.index('EstVar')]
                sa.sumallchange[ key ]['multichange'][1][:,TrendsNames.sumStatsNames.index('TotalChng')] += \
                         sa.study[ eco ].allChange[ key ]['multichange'][1][:,sa.study[eco].statName.index('EstChange')]
                sa.sumallchange[ key ]['multichange'][1][:,TrendsNames.sumStatsNames.index('TotalVar')] += \
                         sa.study[ eco ].allChange[ key ]['multichange'][1][:,sa.study[eco].statName.index('EstVar')]
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def calcAllSummaryStats( sa ):
    try:
        trlog = TrendsUtilities.trLogger()
        for interval in sa.intervals:
            #Calculate sa.summary statistics on conversions
            basicSummaryStatistics.basicSummaryStats( TrendsNames.numConversions, sa.summary[ interval ][1],
                                                      sa.studentT, sa.sumEstPixels )

            #Calculate sa.summary statistics on gain, loss, gross, net
            for tabType in TrendsNames.glgnTabTypes:
                basicSummaryStatistics.basicSummaryStats( TrendsNames.numLCtypes, sa.sumglgn[ interval ][ tabType ][1],
                                                          sa.studentT, sa.sumEstPixels )

            #Calculate sa.summary statistics on all change (only 1 row)
            basicSummaryStatistics.basicSummaryStats( 1, sa.sumallchange[ interval ]['conversion'][1],
                                                            sa.studentT, sa.sumEstPixels )

        for year in sa.years:
            #Calculate sa.summary statistics on composition years
            basicSummaryStatistics.basicSummaryStats( TrendsNames.numLCtypes, sa.sumcomp[ year ][1],
                                                       sa.studentT, sa.sumEstPixels )

        #Calculate sa.summary statistics on aggregated gross change
        interval = TrendsNames.aggregate_gross_interval[0]
        aggPixelCount = numpy.sum(sa.sumaggregate[ interval ]['gross'][1][:,TrendsNames.sumStatsNames.index('TotalChng')])
        

        for key in TrendsNames.aggregate_gross_interval:
            basicSummaryStatistics.basicSummaryStats( 1, sa.sumallchange[ key ]['addgross'][1],
                                                            sa.studentT, aggPixelCount )
            basicSummaryStatistics.basicSummaryStats( TrendsNames.numConversions, sa.sumaggregate[ key ]['gross'][1],
                                                        sa.studentT, aggPixelCount )
            #Calculate sa.summary statistics on aggregate gain, loss, gross, net
            for tabType in TrendsNames.glgnTabTypes:
                basicSummaryStatistics.basicSummaryStats( TrendsNames.numLCtypes, sa.sumaggglgn[ key ]['gross'][ tabType ][1],
                                                          sa.studentT, aggPixelCount )

                
        #Calculate sa.summary statistics on multichange images
        for key in sa.multiIntervals:
            basicSummaryStatistics.basicSummaryStats( TrendsNames.numMulti, sa.summulti[key][1],
                                                    sa.studentT, sa.sumEstPixels )
            basicSummaryStatistics.basicSummaryStats( 1, sa.sumallchange[ key ]['multichange'][1],
                                                        sa.studentT, sa.sumEstPixels )

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def storeAllSummaryStats( gp, sa ):
    try:
        trlog = TrendsUtilities.trLogger()
        tableName = TrendsNames.dbLocation + "SummaryChangeStats"
        dbWriter = databaseWriteClass.changeWrite( gp, tableName)
        for interval in sa.summary:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution,
                                        sa.summary[interval][1], "stats", TrendsNames.sumStatsNames )

        tableName = TrendsNames.dbLocation + "SummaryGlgnStats"
        dbWriter = databaseWriteClass.glgnWrite( gp, tableName)
        for interval in sa.sumglgn:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution,
                                        sa.sumglgn[interval], "stats", TrendsNames.sumStatsNames )

        tableName = TrendsNames.dbLocation + "SummaryCompStats"
        dbWriter = databaseWriteClass.compositionWrite( gp, tableName)
        for year in sa.sumcomp:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, year, sa.resolution,
                                        sa.sumcomp[year][1], "stats", TrendsNames.sumStatsNames )

        tableName = TrendsNames.dbLocation + "SummaryMultichangeStats"
        dbWriter = databaseWriteClass.multichangeWrite( gp, tableName)
        for interval in sa.multiIntervals:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution,
                                    sa.summulti[interval][1], "stats", TrendsNames.sumStatsNames )

        tableName = TrendsNames.dbLocation + "SummaryAllChangeStats"
        dbWriter = databaseWriteClass.allChangeWrite( gp, tableName)
        for interval in sa.intervals:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution, 'conversion',
                                        sa.sumallchange[interval]['conversion'][1], "stats", TrendsNames.sumStatsNames )

        for interval in TrendsNames.aggregate_gross_interval:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution, 'addgross',
                                        sa.sumallchange[interval]['addgross'][1], "stats", TrendsNames.sumStatsNames )

        for interval in sa.multiIntervals:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution, 'multichange',
                                        sa.sumallchange[interval]['multichange'][1], "stats", TrendsNames.sumStatsNames )

        tableName = TrendsNames.dbLocation + "SummaryAggregateStats"
        dbWriter = databaseWriteClass.aggregateWrite( gp, tableName)
        for interval in TrendsNames.aggregate_gross_interval:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution, 'gross',
                                        sa.sumaggregate[interval]['gross'][1], "stats", TrendsNames.sumStatsNames )

        tableName = TrendsNames.dbLocation + "SummaryAggGlgnStats"
        dbWriter = databaseWriteClass.aggGlgnWrite( gp, tableName)
        for interval in TrendsNames.aggregate_gross_interval:
            dbWriter.databaseWrite( gp, sa.analysisNum, sa.study, interval, sa.resolution, 'gross',
                                        sa.sumaggglgn[interval]['gross'], "stats", TrendsNames.sumStatsNames )
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
