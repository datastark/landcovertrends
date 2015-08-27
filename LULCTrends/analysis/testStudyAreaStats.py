# File testStudyAreaStats.py
#
#   In: a name for this analysis run that identifies data in
#       tables stored in the database for the current run.  Some tables
#       have already been generated and are stored in the database.
#
#   Out: analysis data in the database
#
#  This is the main module for the Trends statistics calculations.
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
import arcgisscripting, os, sys, traceback, time
from . import createRegionStats
from . import StudyAreaClass
from ..trendutil import TrendsNames, TrendsUtilities, AnalysisNames

def buildStudyAreaStats( analysisName, analysisNum, ecos, strats, splits ):
    try:
        #Create the geoprocessor object for setting up workspaces and parameters
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #identify potential workspaces for this tool
        #!!gp.ScratchWorkspace =

        #Set up a log file
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Starting analysis: "  + time.asctime())
        trlog.trwrite("Database in use: " + TrendsNames.dbLocation)

        #Initialize a dictionary to hold each ecoregion in the study area
        #  Once each ecoregion is initialized, load its change info and perform statistics
        #  Hold on to all the ecoregion info in order to create summary statistics
        sa = StudyAreaClass.studyArea( gp, analysisName, analysisNum )
        dataFound = False
        for region in ecos:
            total, sample, res, runType  = ecos[ region ]
            sa.study[ region ] = createRegionStats.EcoStats( region, total, sample, res, runType, strats[ region ] )
            if analysisNum == TrendsNames.TrendsNum or runType == "Partial stratified":
                dataFound = sa.study[ region ].loadData()
                if dataFound:
                    sa.study[ region ].performStatistics( analysisNum )
            else:   #load data from tables
                dataFound = sa.study[ region ].loadDataAndStatisticsTables( analysisNum )

        #Create summary statistics and write to database - only do if not Trends run
        if (analysisNum != TrendsNames.TrendsNum) and dataFound:
            sa.generateSummary()
            #summaryStatistics.genSummaryStats( sa.study, analysisNum )

        trlog.trwrite("Analysis complete for " + analysisName + "  " + time.asctime())

    except arcgisscripting.ExecuteError:
        # Get the geoprocessing error messages
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        trlog.trwrite(msgs)
        raise
    except TrendsUtilities.TrendsErrors, Terr:
        #Get errors specific to Trends execution
        trlog.trwrite( Terr.message )
        raise
    except Exception:
        #print out the system error traceback
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise
    finally:
        try:
            trlog.trclose()
        except Exception:
            pass

