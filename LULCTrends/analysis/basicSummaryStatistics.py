# basicSummaryStatistics.py

#Calculates summary statistics for a given summary stats array.  Assumes columns 0 and 1 are already filled in with
# the sums of all the total change and total variance values from each ecoregion in the study area.
# In: number of rows in the stats array, statistics array, studentT values for the summary
# Out: filled in columns in the stat array
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
import arcgisscripting, os, sys, traceback, time
import numpy
from ..trendutil import TrendsNames, TrendsUtilities

def basicSummaryStats( numberRow, stat, studentT, changeSum ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        #Calculate the rest of the summary statistics from values in first two columns
        #If an interval missed data, it's summary table will contain all zeros

        #Third column in summary table is estimate change percent (percent)
        #total change % = (total change (per row) / total estimated pixels) * 100  (percent)
        #First, check for division by zero
        if changeSum <= 0.0:
            raise TrendsUtilities.TrendsErrors( "Unable to process summary statistics. Total pixel count found: " + str(changeSum) )

        stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] = \
                                            ( stat[:,TrendsNames.sumStatsNames.index('TotalChng')] / changeSum ) * 100.0

        #Fourth column is standard error (pixels)
        #standard error = sqrt( total variance ) for each row
        stat[:,TrendsNames.sumStatsNames.index('StdError')] = numpy.sqrt( stat[:,TrendsNames.sumStatsNames.index('TotalVar')] )

        #Fifth column is standard error percent (percent)
        #std error % = (standard error (per row) / sum of total change column) * 100
        stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] = \
                                            ( stat[:,TrendsNames.sumStatsNames.index('StdError')] / changeSum ) * 100.0

        #Sixth column is relative error (percent)
        #Relative error % =  ( standard error % / estimated change % ), and screen for division by zero
        for row in range( numberRow ):
            if stat[row,TrendsNames.sumStatsNames.index('ChgPercent')] != 0.0:
                stat[row,TrendsNames.sumStatsNames.index('RelError')] = \
                        ( stat[row,TrendsNames.sumStatsNames.index('PerStdErr')] / stat[row,TrendsNames.sumStatsNames.index('ChgPercent')] ) * 100.0

        #Seventh through fourteenth columns are the confidence intervals.  They are using student T
        # values calculated from the sum of the sample block counts for all ecoregions in the study area

        #Intervals = estimated change % - or + (standard error % * student T)
        #85% confidence interval
        stat[:,TrendsNames.sumStatsNames.index('Lo85Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] - \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[0])
        stat[:,TrendsNames.sumStatsNames.index('Hi85Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] + \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[0])

        #90% confidence interval
        stat[:,TrendsNames.sumStatsNames.index('Lo90Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] - \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[1])
        stat[:,TrendsNames.sumStatsNames.index('Hi90Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] + \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[1])
        
        #95% confidence interval
        stat[:,TrendsNames.sumStatsNames.index('Lo95Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] - \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[2])
        stat[:,TrendsNames.sumStatsNames.index('Hi95Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] + \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[2])

        #99% confidence interval
        stat[:,TrendsNames.sumStatsNames.index('Lo99Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] - \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[3])
        stat[:,TrendsNames.sumStatsNames.index('Hi99Conf')] = stat[:,TrendsNames.sumStatsNames.index('ChgPercent')] + \
                                                              (stat[:,TrendsNames.sumStatsNames.index('PerStdErr')] * studentT[3])
    except TrendsUtilities.TrendsErrors, Terr:
        trlog.trwrite( Terr.message )
        raise
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

