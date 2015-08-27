# File startStratified.py
#
# In:   ecoregion shapefile
#       text string containing the ecoregion numbers for this summary
#       table name to store the block info in
#       resolution for this analysis
#       data source for analysis
# Out:  table to database containing the block numbers for the ecoregions
#       table containing the ecoregion numbers and the total block count
#       analysis name
#       data source
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
from LULCTrends.trendutil import TrendsNames, AnalysisNames, TrendsUtilities
from LULCTrends.analysis import TrendsDataAccess, CustomDataAccess, testStudyAreaStats

try:
    gp = arcgisscripting.create(9.3)

    Input_Features = gp.GetParameterAsText(0)
    ecoString = gp.GetParameterAsText(1)
    runName = gp.GetParameterAsText(3)
    resolution = gp.GetParameterAsText(2)

    ecoList = []
    if ecoString:
        temp = ecoString.split(",")            
        for entry1 in temp:
            entry = entry1.strip()
            if entry.isalnum():
                ecoList.append( int(entry))
            else:
                if entry.count("-") == 1:
                    values = entry.split("-")
                    for x in range(int(values[0]), int(values[1])+1):
                        ecoList.append( x )
                else:
                    gp.AddError("Unable to parse list of ecoregions")
                    raise TrendsUtilities.JustExit()

    #check for invalid entries in ecolist
    if ecoList:
        for eco in ecoList:
            if eco < 1 or eco > 84:
                gp.AddError("Invalid ecoregion number.  Numbers must be between 1 and 84.")
                raise TrendsUtilities.JustExit()
            
    if runName[0].isdigit():
        gp.AddError("Analysis name must begin with a letter")
        raise TrendsUtilities.JustExit()

    if len(runName) > 25:
        gp.AddError("Maximum length for analysis name is 25 characters")
        raise TrendsUtilities.JustExit()

    found = AnalysisNames.isInAnalysisNames( gp, runName )

    if found and runName.upper() != TrendsNames.name:
        gp.AddError("Analysis name is already in use.  To use this name again, delete previous results from database.")
        raise TrendsUtilities.JustExit()
    else:
        AnalysisNames.updateAnalysisNames( gp, runName )
        analysisNum = AnalysisNames.getAnalysisNum( gp, runName )

    if runName.upper() == TrendsNames.name:
        gp.AddWarning("The Trends run name causes a refresh of data and statistics in the database for the given ecoregions.")
        gp.AddWarning("No summary statistics will be generated.")

    path = os.path.dirname(sys.argv[0])    
    scratchpath = path.replace(r'\TrendsToolShare\scripts',r'\TrendsToolShare\Scratch\scratch.gdb')


    if ecoList:  #run a full-stratified Trends or summary
        newEcos, strats, splits = TrendsDataAccess.accessTrendsData( Input_Features, ecoList, analysisNum, resolution, scratchpath )
    else:
        if Input_Features:  #use the custom boundary to run a custom stratified analysis
            newEcos, strats, splits = CustomDataAccess.accessCustomData( Input_Features, analysisNum, resolution, scratchpath )
        else:
            gp.AddMessage("Either a boundary shapefile or a list of ecoregions must be entered for analysis.")

    if len(newEcos) > 0:
        samplecount = [ len(strats[x]) for x in strats if len(strats[x]) > 0] #make list of non-zero sample block counts
        if samplecount != []:
            testStudyAreaStats.buildStudyAreaStats( runName, analysisNum, newEcos, strats, splits )
        else:  #no samples blocks found in custom area
            gp.AddMessage("No sample blocks found within the study area. No Trends analysis can be performed.")
    else:
        gp.AddMessage("No Trends ecoregions found within the study area.")

except arcgisscripting.ExecuteError:
    # Get the geoprocessing error messages
    msgs = gp.GetMessage(0)
    msgs += gp.GetMessages(2)
    gp.AddMessage(msgs)

except TrendsUtilities.JustExit:
    pass

except Exception:
    #print out the system error traceback
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
    gp.AddMessage(pymsg)

