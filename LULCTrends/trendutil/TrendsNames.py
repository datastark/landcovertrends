# TrendsNames.py
#
# module containing any definitions to be used by
# several other modules  #!!!!!! specific server names have been removed !!!!!
#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Define database name
dbName = "Database Connections/Connection to REMOVED_TrendsStats.sde/DEVELOP.dbo."

#server XXXX version
#dbLocation = "//REMOVED/DBconnections/Connection to REMOVED_TrendsStats.sde/ANALYSIS.dbo."

#Set the database location for the workstations to either DEVELOP (on XXXX) or ANALYSIS (on XXXX)
dbLocation = "Database Connections/Connection to REMOVED_TrendsStats.sde/DEVELOP.dbo."

#Point to template db for table creation.  Tables are then copied to db server.
dbTemplate = "REMOVED/Trends/Database/TrendsTemplate.gdb/"

#Set the change and multichange images folders to either \Data\ for Server and workstation XXXX (ANALYSIS) or
# \TestData\ for workstation XXXX (DEVELOP)
changeImageFolders = r"\\REMOVED\REMOVED\LULCTrends\TestData\Change_Images" 
multichangeFolders = r"\\REMOVED\REMOVED\LULCTrends\TestData\Multichange_Images"

#Set the number of Level 3 ecoregions
numEcoregions = 84

#The mapping for analysis name to number for Trends ecoregions - see AnalysisNames table in DB
TrendsNum = 1
name = "TRENDS"

#Define the number of land use conversions, which is used as the number of columns in the arrays
numConversions = 121

#Define the number of land cover types
numLCtypes = 11

#Define the number of multichange intervals (0 - lots of changes)
numMulti = 30

#Define the statistics column names
statisticsNames = ['Mean','EstChange','ChgPercent','S_Squared','EstVar','StdError',
                    'PerStdErr','RelError','Lo85Conf','Hi85Conf','Lo90Conf','Hi90Conf',
                    'Lo95Conf','Hi95Conf','Lo99Conf','Hi99Conf']
statprintNames = ['Mean(pix)','EstChange(pix)','ChgPercent(%)','S_Squared(pix)','EstVar(pix)',
                  'StdError(pix)','PerStdErr(%)','RelError(%)','Lo85Conf(%)','Hi85Conf(%)',
                  'Lo90Conf(%)','Hi90Conf(%)',
                    'Lo95Conf(%)','Hi95Conf(%)','Lo99Conf(%)','Hi99Conf(%)']
numStatisticsNames = len( statisticsNames )

sumStatsNames = ['TotalChng','TotalVar','ChgPercent','StdError',
            'PerStdErr','RelError','Lo85Conf','Hi85Conf','Lo90Conf','Hi90Conf',
            'Lo95Conf','Hi95Conf','Lo99Conf','Hi99Conf']
sumprintNames = ['TotalChng(pix)','TotalVar(pix)','ChgPercent(%)','StdError(pix)',
            'PerStdErr(%)','RelError(%)','Lo85Conf(%)','Hi85Conf(%)','Lo90Conf(%)','Hi90Conf(%)',
            'Lo95Conf(%)','Hi95Conf(%)','Lo99Conf(%)','Hi99Conf(%)']
numSumStatsNames = len( sumStatsNames )

#Define land cover 
LCtype = {1:'Water',2:'Developed',3:'Mechanically disturbed',
            4:'Mining',5:'Barren',6:'Forest',7:'Grassland/Shrubland',
            8:'Agriculture',9:'Wetland',10:'Nonmechanically disturbed',
            11:'Snow/Ice'}
LCTypecntr = len( LCtype )
LCshort = ['Water   ','Developed','Mech.Dist.','Mining  ','Barren  ','Forest  ',
           'Grs/Shrub','Agricult','Wetland','N.M.Dist.','Snow/Ice']
glgnTabTypes = ('gain','loss','gross','net')

#Standard intervals for Trends dbf table building
TrendsIntervals = ['1973to2000','1973to1980','1980to1986','1986to1992','1992to2000']

#Standard composition years for Trends dbf table building
TrendsYears = ['1973','1980','1986','1992','2000']

#Mapping of intervals to number of changes for multichange processing
#Count here includes 1 extra for no change
MultiMap = {'1973to2000':5, '1973to2010':7, '2000to2010':7}

#Count of the number of intervals used to make the given cumulative
#data and stats.  This is used in the excel builder to determine average
#annual values.
CumulativeMap = {'1973to2000':4}

#Standard multichange years for Trends dbf table building
TrendsMultiIntervals = ['1973to2000']
TrendsDBFmulti = 5  #max no change + 4 changes

#minimum and maximum resolutions
minResolution = '30m'
maxResolution = '60m'

#aggregated gross change interval list
aggregate_gross_interval = ['1973to2000']

#List of the ecoregions with 20k blocks
Ecos_20k = [16,45,62,63,64,65,66,79,84]

#Values for area calculations
block20Area = 399200400
block10Area = 100000000
block20_51per = 203592204
block10_51per = 51000000

#Level 2 analysis names and corresponding number for Level2Ecoregions table
Level2Names = [("MIXEDWOODSHIELD",5.2),
               ("ATLANTICSHIELD",5.3),
               ("WESTERNCORDILLERA",6.2),
               ("MARINEWESTFORESTS",7.1),
               ("MIXEDWOODPLAINS",8.1),
               ("CENTRALUSAPLAINS",8.2),
               ("SOUTHEASTERNUSAPLAINS",8.3),
               ("OZARKAPPALACHIANFORESTS",8.4),
               ("MISSISSIPPIALLUVIALPLAIN",8.5),
               ("TEMPERATEPRAIRIES",9.2),
               ("WESTCENTRALARIDPRAIRIES",9.3),
               ("SOUTHCENTRALPRAIRIESTEXAS",9.4),
               ("COLDDESERTS",10.1),
               ("WARMDESERTS",10.2),
               ("MEDITERRANEANCA",11.1)]
