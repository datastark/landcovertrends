# File basicStatistics.py
#
# Contains the functions that generate basic statistics such as mean and variance.
#  These are the statistics for the data arrays, such as the conversion arrays and
#   the gain, loss, gross, net and multichange data.
#
# In: eco - the current ecoregion object, provides access to globals such as N, n, and
#               statistics column names
#     numRow - number of rows in the data array
#     data - reference to the data array
#     stat - reference to the statistics array
# 
#
# Written:         Sept 2010
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
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
import numpy
from ..trendutil import TrendsUtilities

def dataStats( eco, numRow, data, stat ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()
        
        #Define the necessary R functions.  Use numpy's version of mean
        #since it may be faster, but can't use var and std since they
        #are defined for population instead of sample in version 2.5
        r_var = robjects.r['var']

        #First, do calculations that are based on all the rows in the data array
        #If only one block in this eco (custom boundary case), then the mean just equals the value
        #  for that block and the variance is set to 0.0
        #Calculate mean, variance
        for row in range( numRow ):
            if eco.sampleBlks > 1:
                #mean   (pixels)
                stat[row, eco.statName.index('Mean')] = numpy.mean( data[ row, : ])
                #s_squared   (pixels)
                stat[row, eco.statName.index('S_Squared')] = TrendsUtilities.makeAtomic( r_var( data[ row, : ]))
            else:
                #mean   (pixels)
                stat[row, eco.statName.index('Mean')] = data[ row, : ]
                #s_squared   (pixels)
                stat[row, eco.statName.index('S_Squared')] = 0.0                

        #Now do the calculations that are based on other columns in the statistics array
        #estimated change = mean * N  (pixels)
        stat[:, eco.statName.index('EstChange')] = stat[ :, eco.statName.index('Mean') ] * eco.totalBlks
        
        #estimated change % = (estimated change (per row) / sum of estimated change column) * 100  (percent)
        #  and screen for division by zero
        sumChgColumn = eco.totalEstPixels
        if sumChgColumn > 0.0:
            stat[:,eco.statName.index('ChgPercent')] = ( stat[:,eco.statName.index('EstChange')] / sumChgColumn ) * 100.0
        #else, do nothing since column was initialized to 0.0

        #estimated variance = ((total blocks^2)*(1-(n/N))*(s_squared))/n    (pixels)
        stat[:,eco.statName.index('EstVar')] = \
            ((eco.totalBlks**2)*(1.0 - float(eco.sampleBlks)/float(eco.totalBlks))*stat[:,eco.statName.index('S_Squared')])/float(eco.sampleBlks)

        #standard error = sqrt( estimated variance )   (pixels)
        stat[:, eco.statName.index('StdError')] = numpy.sqrt( stat[:, eco.statName.index('EstVar')] )

        #standard error % = (standard error (per row) / sum of estimated change column) * 100,
        #  and screen for division by zero
        if sumChgColumn > 0.0:
            stat[:,eco.statName.index('PerStdErr')] = ( stat[:,eco.statName.index('StdError')] / sumChgColumn ) * 100.0
        #else, do nothing since column was initialized to 0.0

        #relative error = standard error % / estimated change %, and screen for division by zero
        for row in range( numRow ):
            if stat[row, eco.statName.index('ChgPercent')] != 0.0:
                stat[row,eco.statName.index('RelError')] = (stat[row,eco.statName.index('PerStdErr')] / stat[row,eco.statName.index('ChgPercent')]) * 100.0
            #else, do nothing since column was initialized to 0.0

        #low or high confidence = percent change - or + (percent standard error * student T)
        #85% confidence interval
        stat[:,eco.statName.index('Lo85Conf')] = stat[:,eco.statName.index('ChgPercent')] - (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[0])
        stat[:,eco.statName.index('Hi85Conf')] = stat[:,eco.statName.index('ChgPercent')] + (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[0])

        #90% confidence interval
        stat[:,eco.statName.index('Lo90Conf')] = stat[:,eco.statName.index('ChgPercent')] - (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[1])
        stat[:,eco.statName.index('Hi90Conf')] = stat[:,eco.statName.index('ChgPercent')] + (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[1])
        
        #95% confidence interval
        stat[:,eco.statName.index('Lo95Conf')] = stat[:,eco.statName.index('ChgPercent')] - (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[2])
        stat[:,eco.statName.index('Hi95Conf')] = stat[:,eco.statName.index('ChgPercent')] + (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[2])

        #99% confidence interval
        stat[:,eco.statName.index('Lo99Conf')] = stat[:,eco.statName.index('ChgPercent')] - (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[3])
        stat[:,eco.statName.index('Hi99Conf')] = stat[:,eco.statName.index('ChgPercent')] + (stat[:,eco.statName.index('PerStdErr')] * eco.studentT[3])

    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit
