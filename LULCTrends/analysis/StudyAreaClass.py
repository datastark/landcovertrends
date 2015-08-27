#study area class for Trends
#
# StudyAreaClass.py
#
# Written:         Mar 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting, numpy
import os, sys, traceback
from ..trendutil import TrendsNames, TrendsUtilities
from . import summaryStatistics

class studyArea:

    def __init__(self, gp, analysisName, analysisNum):
        try:
            trlog = TrendsUtilities.trLogger()
            self.analysisName = analysisName
            self.analysisNum = analysisNum
            self.resolution = ""
            self.intervals = []
            self.multiIntervals = []
            self.aggIntervals = []
            self.years = []
            self.sumEstPixels = 0.0
            self.summarySamples = 0
            self.totalBlocks = 0
            self.studentT = []
            self.study = {}
            #Create a dictionary for the summary tables, and key by interval
            #Create and initialize a floating point numpy 2-dim array for the stats
            #The '0' in the tuple is just a placeholder for the data array.  Summaries use only statistics.
            self.summary = {}
            self.sumglgn = {}
            self.sumcomp = {}
            self.summulti = {}
            self.sumallchange = {}
            self.sumaggregate = {}
            self.sumaggglgn = {}

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            trlog.trwrite(pymsg)
            raise

    def generateSummary( self ):
        try:
            trlog = TrendsUtilities.trLogger()
            summaryStatistics.genSummaryStats( self, self.analysisNum )
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            trlog.trwrite(pymsg)
            raise     #push the error up to exit
