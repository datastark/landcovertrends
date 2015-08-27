# File createRegionStats.py
#
# Creates an ecoregion container for statistics calculation
# The object contains several numpy arrays for the various data types:
#      an integer array contains the data column for each block, and
#      a floating pt. array holds the various statistics in its columns
# Methods load the block conversion data into the table, calculate the
# statistics, and store the results in the database
#
# When an ecoregion stat is created, it is passed the ecoregion number,
#    the total number of blocks and the number of
#    samples for this set of statistics.  The number of sample blocks
#    may be equal to or less than the sample block count 'n' for this
#    ecoregion.  If only part of the ecoregion is selected for analysis,
#    the 'n' passed in as initializer is < the 'n' for the ecoregion.
#    This is also true for N, when a partial ecoregion is used.
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
import arcgisscripting, numpy
import os, sys, traceback, re
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
from ..trendutil import TrendsUtilities, TrendsNames
from .ChangeData import loadChangeImageData, loadMultiChangeData
from .EcoregionStatistics import calculateEcoStatistics, storeEcoStatistics, findTotalEstimatedPixels
from .setUpCalcStructures import setUpArrays
from .gainsLosses import calcGainsLosses, calcGlgnStats, storeGainsLosses
from .allChange import calcAllChange, storeAllChange
from .aggregate import calcAddGross, storeAddGross
from .composition import calcComposition, calcCompStats, storeComposition
from .multichangeStatistics import calcMultichangeStats, storeMultichange
from .restoreEcoFromDB import loadEcoregion
from .UpdateAnalysisParams import updateParameters

class EcoStats :
    
    #define some standard values
    numCon = TrendsNames.numConversions   #types of land use conversions
    #eventual column labels of statistics array
    statName = TrendsNames.statisticsNames
    numStats = len(statName)          #number of columns in stats array

    def __init__(self, ecoNum, N, n, res, runType, strat_list, split_list = []):
        try:            
            gp = arcgisscripting.create(9.3)
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            #Set up statistics parameters for this ecoregion
            self.ecoNum = ecoNum
            self.totalBlks = N   #N actual
            self.sampleBlks = n  #n actual
            self.resolution = res
            self.runType = runType  #'Full stratified','Partial stratified'
            self.degreesf = n - 1
            self.stratBlocks = strat_list
            self.splitBlocks = split_list

            #This value is needed during statistics for gain, loss, etc., multichg, and summaries
            #It is calculated during the statistics runs on the change images and they fill in the
            #value.  Later statistics pick it up from here.
            self.totalEstPixels = 0.0

            #Make a dictionary that maps the sample block numbers to the
            #  array column numbers.  If strat_list = [16, 18, 21] and
            #  split_list = [1,20,56], then
            #  self.column = {1:0, 16:1, 18:2, 20:3, 21:4, 56:5}
            
            temp = sorted( strat_list + split_list )
            if len(temp) != n:
                raise TrendsUtilities.TrendsErrors("The number of sample blocks (" + str(self.sampleBlks) + \
                                                   ")in " + str(self.ecoNum) + \
                                   " does not match the actual count of blocks (" + str(len(temp)) + ")")
            if len(temp) == 0:
                raise TrendsUtilities.TrendsErrors("No sample blocks found for ecoregion " + str(self.ecoNum))
            self.column = dict( zip( temp, [x for x in range( len(temp))]))

            #Get the student's T values for 15%, 10%, 5%, and 1% quantiles
            # Values are contained in studentT[0] - [3].  R returns a one-tailed t
            # value, so use 7.5%, 5%, 2.5%, and .5% for 2-tailed.
            
            if self.degreesf > 0:
                r_qt = robjects.r['qt']
                self.studentT = r_qt(robjects.FloatVector([.925, .95, .975, .995]), self.degreesf)
            else:       #if n = 1 for a custom ecoregion, don't get student T since df = 0
                self.studentT = [-9999.99, -9999.99, -9999.99, -9999.99]

            tempstr = "Student T values for ecoregion %2d: %0.3f  %0.3f  %0.3f  %0.3f" %(self.ecoNum,self.studentT[0],self.studentT[1],self.studentT[2],self.studentT[3])
            trlog.trwrite( tempstr )

            #Create the conversion arrays holder, which is loaded when loadConversions is called.
            # To access elements in the dictionary, the first subscript is
            # the change interval, and this points to a tuple holding the two
            # arrays for that interval, i.e. self.ecoData['1973to1980'] points to
            # (data array, stats array).  The second subscript selects
            # the individual array, i.e. self.ecoData['1992to2000'][1] points to the
            # stats array for that change interval.  The third subscript points
            # to the row, column within the array, i.e. self.ecoData['1980to1986'][0][12,2]
            # points to the entry at the 13th row and 3rd column (entries start at 0)
            # of the conversion array for the 1980 to 1986 change interval.
            # self.ecoData[ changeInterval ][ data / stats array ][ row, column ]
            # The data array is an integer array with 121 rows and number of columns
            # equal to the number of blocks used in this analysis for this ecoregion.
            # The statistics array is a floating pt. array with 121 rows and number of
            # columns equal to the number of statistics generated.
            
            self.ecoData = {}

            #Create arrays holder for gain, loss, gross, and net data.  These tables are
            # filled from the conversion data in the ecoData arrays.

            self.ecoGlgn = {}

            #Create arrays to hold composition data and statistics.  These tables are currently
            # calculated from the conversion data in the ecoData arrays.

            self.ecoComp = {}

            #multichange arrays
            self.ecoMulti = {}

            #Create arrays for "all change", which is just the conversion data minus the no-change
            # conversions.

            self.allChange = {}

            #Create arrays for aggregate change, which is the old gross change page

            self.aggregate = {}
            self.aggGlgn = {}
            self.aggregate_gross_keys = TrendsNames.aggregate_gross_interval

            #Get the names of the change interval folders holding the change images
            #Check for the correct folder names ( they should have year1'to'year2 ) in order
            # to catch any change to folder structure that would interfere with tool operation
            folderList = os.listdir( TrendsNames.changeImageFolders )
            for folder in folderList:
                if not re.match( r'\d\d\d\dto\d\d\d\d', folder):
                    raise TrendsUtilities.TrendsErrors( "Unexpected interval folder found in Change_Images folder: " + \
                                                        folder)

            #Create the conversion data and stats arrays
            for folder in folderList:
                self.ecoData[ folder ] = ( numpy.zeros(( EcoStats.numCon, self.sampleBlks ), int),
                                        numpy.zeros(( EcoStats.numCon, EcoStats.numStats ), float))

            #Create the composition arrays.  This is currently calculated from gain/loss.
            years = TrendsUtilities.getYearsFromIntervals( gp, folderList )
            for date in years:
                self.ecoComp[ date ] = ( numpy.zeros(( TrendsNames.LCTypecntr, self.sampleBlks ), int),
                                        numpy.zeros(( TrendsNames.LCTypecntr, self.numStats ), float))


            #Create arrays holder for multi-change data.  This is read in from the multi-change
            # files.
            multiList = os.listdir( TrendsNames.multichangeFolders )
            for folder in multiList:
                if not re.match( r'\d\d\d\dto\d\d\d\d', folder):
                    raise TrendsUtilities.TrendsErrors( "Unexpected interval folder found in Multichange_Images folder: " + \
                                                        folder)
            for interval in multiList:
                self.ecoMulti[ interval ] = ( numpy.zeros(( TrendsNames.numMulti, self.sampleBlks ), int),
                                            numpy.zeros(( TrendsNames.numMulti, EcoStats.numStats ), float))

        except arcgisscripting.ExecuteError:
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

    def loadData( self ):
        try:            
            gp = arcgisscripting.create(9.3)
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            
            nointervals = []
            #For each change interval, get the conversion data into the array
            # if no data found for the interval, delete the data structures
            for interval in self.ecoData:
                loadComplete = loadChangeImageData( self, interval )
                if not loadComplete:
                    trlog.trwrite( "No data or analysis for ecoregion " + str(self.ecoNum) + \
                                  " and interval " + interval )
                    nointervals.append(interval)

            #delete data arrays for intervals where there's no data
            for interval in nointervals:
                del self.ecoData[ interval ]

            #Now load the multichange images, but first check that there was change data
            if len(self.ecoData) > 0:
                dataFound = True
                nomultiIntervals = []
                for interval in self.ecoMulti:
                    loadComplete = loadMultiChangeData( self, interval )
                    if not loadComplete:
                        trlog.trwrite( "No multichange data or analysis for ecoregion " + \
                                           str(self.ecoNum))
                        nomultiIntervals.append(interval)

                #delete data arrays for intervals where there's no data
                for interval in nomultiIntervals:
                    del self.ecoMulti[ interval ]
                        
                #Now update the arrays for composition based on the intervals found.
                # This will eventually be where composition is loaded
                folderList = self.ecoData.keys()            
                currentyears = TrendsUtilities.getYearsFromIntervals( gp, folderList )
                compyears = self.ecoComp.keys()
                for date in compyears:
                    if not (date in currentyears):
                        del self.ecoComp[ date ]

                #Now check if any aggregate data needed
                keylist = self.aggregate_gross_keys
                compyears = self.ecoComp.keys()
                for interval in keylist:
                    ptr = self.aggregate_gross_keys.index(interval)
                    splitInfo = interval.split('to')
                    start = splitInfo[0]
                    end = splitInfo[1]
                    if not (start in compyears) or not (end in compyears):
                        del self.aggregate_gross_keys[ptr]
                    
            else:
                dataFound = False
            return dataFound
                
        except arcgisscripting.ExecuteError:
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

    def performStatistics( self, analysisNum ):
        try:            
            #Set up a log object
            trlog = TrendsUtilities.trLogger()
            
            firstInterval = TrendsUtilities.getFirstInterval( self )
            findTotalEstimatedPixels( self, self.ecoData[firstInterval][0] )
            trlog.trwrite("Total est pixel count for eco "+str(self.ecoNum)+ " is " +str(self.totalEstPixels))
            setUpArrays( self )
                
            for interval in self.ecoData:
                calculateEcoStatistics( self, interval )
                storeEcoStatistics( self, interval, analysisNum )
                calcGainsLosses( self.ecoData[interval], self.ecoGlgn[interval] )
                calcGlgnStats( self, self.ecoGlgn[interval] )
                storeGainsLosses( self, interval, analysisNum )
                calcComposition( self, interval )
            for year in self.ecoComp:
                calcCompStats( self, year )
                storeComposition( self, year, analysisNum )

            for interval in self.ecoMulti:
                calcMultichangeStats( self, interval ) 
                storeMultichange( self, interval, analysisNum )

            if self.aggregate_gross_keys:  #are there any aggregates needed for this data?
                calcAddGross( self )
                #change pixel count for aggregate
                findTotalEstimatedPixels( self, self.aggregate[self.aggregate_gross_keys[0]]['gross'][0] )
                for interval in self.aggregate_gross_keys:
                    calcGainsLosses( self.aggregate[interval]['gross'],self.aggGlgn[interval]['gross'] )
                    calcGlgnStats( self, self.aggGlgn[interval]['gross'] )
                storeAddGross( self, analysisNum )

                firstInterval = TrendsUtilities.getFirstInterval( self )
                findTotalEstimatedPixels( self, self.ecoData[firstInterval][0] )
                
            calcAllChange( self )
            storeAllChange( self, analysisNum )

            if self.runType == "Full stratified":
                tableName = "Ecoregions"
            else:
                tableName = "SummaryEcoregions"
            updateParameters(tableName, analysisNum, self.ecoNum, self.sampleBlks,
                             self.totalBlks, self.totalEstPixels,
                             self.studentT[0],self.studentT[1],self.studentT[2],self.studentT[3],
                             self.resolution, self.runType)
        except arcgisscripting.ExecuteError:
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

    def loadDataAndStatisticsTables( self, analysisNum ):
        try:            
            #Set up a log object
            trlog = TrendsUtilities.trLogger()

            #Set a local analysisNum variable for the ecoregion so it
            # can load data from either Trends tables or custom tables.
            # If this is a summary, the study area object still has the
            # summary's analysisNum.  Data is only loaded from the custom
            # tables when the Excel output files are generated.
            if self.runType == "Full stratified":
                self.analysisNum = TrendsNames.TrendsNum
            else:
                self.analysisNum = analysisNum
            dataFound = loadEcoregion( self )
            if dataFound:
                firstInterval = TrendsUtilities.getFirstInterval( self )
                findTotalEstimatedPixels( self, self.ecoData[firstInterval][0] )
                tableName = "SummaryEcoregions"
                updateParameters(tableName, analysisNum, self.ecoNum, self.sampleBlks,
                             self.totalBlks, self.totalEstPixels,
                             self.studentT[0],self.studentT[1],self.studentT[2],self.studentT[3],
                             self.resolution, self.runType)
            return dataFound
        except arcgisscripting.ExecuteError:
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
            
if __name__ == '__main__':            #test an ecoregion object setup
    stratified = [16,18,32,35,57,61,67,82,99,126,128,133]
    split = []
    resolution = '60m'
    Ecoregion_7 = EcoStats( 7, 458, 12, resolution, stratified, split )
    Ecoregion_7.loadConversions()

