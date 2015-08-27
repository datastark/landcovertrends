# File setUpCalcStructures.py
#
# creates the arrays for the data structures that are calculated
#  from the conversion data
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
import os, sys, traceback, time
import numpy
from ..trendutil import TrendsNames, TrendsUtilities

def setUpArrays( eco ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        folderList = eco.ecoData.keys()
        add_keys = eco.aggregate_gross_keys
        multiList = eco.ecoMulti.keys()

        for folder in folderList:
            eco.ecoGlgn[ folder ] = {}
            eco.allChange[ folder ] = {}
            #Create the gain, loss, gross, and net arrays. These arrays hold the values
            #  for all 11 land cover classes
            for tabType in TrendsNames.glgnTabTypes:
                eco.ecoGlgn[ folder ][ tabType ] = ( numpy.zeros(( TrendsNames.LCTypecntr, eco.sampleBlks ), int),
                                                numpy.zeros(( TrendsNames.LCTypecntr, TrendsNames.numStatisticsNames ), float))

            #Create the allChange arrays
            eco.allChange[ folder ]['conversion'] = ( numpy.zeros(( 1, eco.sampleBlks ), int),
                                        numpy.zeros(( 1, TrendsNames.numStatisticsNames ), float))

        for key in add_keys:
            if key not in folderList:
                eco.allChange[key] = {}
            eco.allChange[key]['addgross'] = ( numpy.zeros(( 1, eco.sampleBlks ), int),
                                        numpy.zeros(( 1, TrendsNames.numStatisticsNames ), float))
            #Create the aggregate change arrays for specified intervals
            eco.aggregate[ key ] = {}
            eco.aggGlgn[ key ] = {}
            eco.aggGlgn[ key ]['gross'] = {}
            eco.aggregate[ key ]['gross'] = ( numpy.zeros(( TrendsNames.numConversions, eco.sampleBlks ), int),
                                        numpy.zeros(( TrendsNames.numConversions, TrendsNames.numStatisticsNames ), float))
            for tabType in TrendsNames.glgnTabTypes:
                eco.aggGlgn[ key ]['gross'][ tabType ] = ( numpy.zeros(( TrendsNames.LCTypecntr, eco.sampleBlks ), int),
                                                numpy.zeros(( TrendsNames.LCTypecntr, TrendsNames.numStatisticsNames ), float))

        #Set up a multichange 'allchange' for multichange intervals
        for interval in multiList:
            if interval not in folderList:
                eco.allChange[interval] = {}
            eco.allChange[interval]['multichange'] = ( numpy.zeros(( 1, eco.sampleBlks ), int),
                                        numpy.zeros(( 1, TrendsNames.numStatisticsNames ), float))
        
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

def setUpSummaryArrays( sa ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        add_keys = TrendsNames.aggregate_gross_interval

        for interval in sa.intervals:
            sa.summary[ interval ] = (0, numpy.zeros(( TrendsNames.numConversions, TrendsNames.numSumStatsNames ), float))
            sa.sumglgn[ interval ] = {}
            for tabType in TrendsNames.glgnTabTypes:
                sa.sumglgn[ interval ][ tabType ] = (0, numpy.zeros(( TrendsNames.numLCtypes, TrendsNames.numSumStatsNames ), float))

            #Create the allChange arrays
            sa.sumallchange[ interval ] = {}
            sa.sumallchange[ interval ]['conversion'] = ( 0,
                                        numpy.zeros(( 1, TrendsNames.numSumStatsNames ), float))
            
        for year in sa.years:
            sa.sumcomp[ year ] = (0, numpy.zeros(( TrendsNames.numLCtypes, TrendsNames.numSumStatsNames ), float))

        #Create the arrays for the aggregated gross change data
        for key in add_keys:
            sa.sumallchange[key]['addgross'] = ( 0,
                                        numpy.zeros(( 1, TrendsNames.numSumStatsNames ), float))
            #Create the aggregate change arrays for specified intervals
            sa.sumaggregate[ key ] = {}
            sa.sumaggregate[ key ]['gross'] = ( 0,
                                        numpy.zeros(( TrendsNames.numConversions, TrendsNames.numSumStatsNames ), float))
            sa.sumaggglgn[ key ] = {}
            sa.sumaggglgn[ key ]['gross'] = {}
            for tabType in TrendsNames.glgnTabTypes:
                sa.sumaggglgn[ key ]['gross'][ tabType ] = (0,
                                        numpy.zeros(( TrendsNames.numLCtypes, TrendsNames.numSumStatsNames ), float))

        #Throw in a multichange 'allchange' at a fixed interval for now. Eventually multichange should have dates
        # associated with it
        for interval in sa.multiIntervals:
            sa.summulti[interval] = (0, numpy.zeros(( TrendsNames.numMulti, TrendsNames.numSumStatsNames ), float))
            sa.sumallchange[interval]['multichange'] = ( 0,
                                        numpy.zeros(( 1, TrendsNames.numSumStatsNames ), float))
        
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

class smallEco:
    def __init__(self, ecoNum):
        try:
            self.ecoNum = ecoNum
            self.conv = {}
            self.glgn = {}
            self.comp = {}
            self.multi = {}
            self.allchg = {}
            self.aggregate = {}
            self.aggGlgn = {}
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            trlog.trwrite(pymsg)
            raise     #push the error up to exit

def setUpShortEcoArrays( sa, ecoNum ):
    try:
        #Set up a log object
        trlog = TrendsUtilities.trLogger()

        folderList = sa.intervals
        add_keys = sa.aggIntervals
        years = sa.years
        multints = sa.multiIntervals
        sa.study[ ecoNum ] = smallEco( ecoNum )

        for folder in folderList:
            sa.study[ ecoNum ].conv[ folder ] = {}
            sa.study[ ecoNum ].conv[ folder ] = numpy.zeros((TrendsNames.numConversions, 2 ), float)
            sa.study[ ecoNum ].glgn[ folder ] = {}
            sa.study[ ecoNum ].allchg[ folder ] = {}
            #Create the gain, loss, gross, and net arrays. These arrays hold the values
            #  for all 11 land cover classes
            for tabType in TrendsNames.glgnTabTypes:
                sa.study[ ecoNum ].glgn[ folder ][ tabType ] = numpy.zeros(( TrendsNames.LCTypecntr, 2 ), float)

            #Create the allChange arrays
            sa.study[ ecoNum ].allchg[ folder ]['conversion'] = numpy.zeros((1, 2 ), float)

        for year in years:
            sa.study[ ecoNum ].comp[ year ] = numpy.zeros(( TrendsNames.LCTypecntr, 2 ), float)

        for key in add_keys:
            sa.study[ ecoNum ].allchg[key]['addgross'] = numpy.zeros((1, 2 ), float)
            #Create the aggregate change arrays for specified intervals
            sa.study[ ecoNum ].aggregate[ key ] = {}
            sa.study[ ecoNum ].aggGlgn[ key ] = {}
            sa.study[ ecoNum ].aggGlgn[ key ]['gross'] = {}
            sa.study[ ecoNum ].aggregate[ key ]['gross'] = numpy.zeros(( TrendsNames.numConversions, 2 ), float)
            for tabType in TrendsNames.glgnTabTypes:
                sa.study[ ecoNum ].aggGlgn[ key ]['gross'][ tabType ] = numpy.zeros(( TrendsNames.LCTypecntr, 2 ), float)

        for interval in multints:
            sa.study[ ecoNum ].allchg[interval]['multichange'] = numpy.zeros((1, 2 ), float)
            sa.study[ ecoNum ].multi[ interval ] = numpy.zeros(( TrendsNames.numMulti, 2 ), float)
        
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise     #push the error up to exit

