# File indexTrendsTables.py
#
#   deletes old index and creates a new attribute
#   index on all major search fields
#
# Written:         Feb 2012
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import traceback
import arcgisscripting
from LULCTrends.trendutil import TrendsNames


allTables = [   "TrendsChangeData",
                "TrendsChangeStats",
                "TrendsGlgnData",
                "TrendsGlgnStats",
                "TrendsCompData",
                "TrendsCompStats",
                "TrendsMultichangeData",
                "TrendsMultichangeStats",
                "TrendsAllChangeData",
                "TrendsAllChangeStats",
                "TrendsAggregateData",
                "TrendsAggregateStats",
                "TrendsAggGlgnData",
                "TrendsAggGlgnStats",]

def indexTrendsTables():
    try:
        gp = arcgisscripting.create(9.3)
        gp.OverwriteOutput = True

        #delete old indexes on Trends tables  
        for tableName in allTables:
            tableLoc = TrendsNames.dbLocation + tableName
            try:
                gp.removeindex (tableLoc, "fullsearch")
            except Exception:
                pass

        #add new index to each table on all searched fields
        tableName = "TrendsChangeData"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsChangeStats"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsGlgnData"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Glgn", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsGlgnStats"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Glgn", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsCompData"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;CompYear;Resolution", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsCompStats"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;CompYear;Resolution", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsMultichangeData"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsMultichangeStats"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsAggGlgnData"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Source;Glgn", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsAggGlgnStats"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Source;Glgn", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsAggregateData"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Source", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsAggregateStats"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Source", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsAllChangeData"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Source", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

        tableName = "TrendsAllChangeStats"
        tableLoc = TrendsNames.dbLocation + tableName
        gp.addindex (tableLoc, "AnalysisNum;EcoLevel3ID;ChangePeriod;Resolution;Source", "fullsearch", "NON_UNIQUE", "NON_ASCENDING")

    except arcgisscripting.ExecuteError:
        print(gp.GetMessage(0) + gp.GetMessages(2))
        raise

    except Exception:
        print(traceback.format_exc())
        raise     #push the error up to exit

if __name__ == '__main__':
    indexTrendsTables()
    print "Complete"
