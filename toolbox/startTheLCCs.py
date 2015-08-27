# File startAlllccs.py
#
# Starts the analysis for selected LCCs and builds excel files
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
from LULCTrends.trendutil import AnalysisNames, TrendsUtilities, deleteAnalysisName
from LULCTrends.analysis import CustomDataAccess, testStudyAreaStats
from LULCTrends.xcel.CustomWorkbookClass import CustomWorkbook
from LULCTrends.xcel.SummaryWorkbookClass import SummaryWorkbook

lccnamelist = { "Appalachian": 1,
             "California": 2,
             "Desert": 3,
             "EasternTallgrass": 4,
             "GreatBasin": 5,
             "GreatNorthern": 6,
             "GreatPlains": 7,
             "GulfCoastPrairie": 8,
             "GulfPlainsOzarks": 9,
             "NorthAtlantic": 10,
             "NorthPacific": 11,
             "PeninsularFlorida": 12,
             "PlainsPrairiePotholes": 13,
             "SouthAtlantic": 14,
             "SouthernRockies": 15,
             "UpperMidwestAndLakes": 16 }

def startLCCs( tempList, resolution, outFolder ):
    try:
        gp = arcgisscripting.create(9.3)
        gp.overwriteOutput = True

        lccList = [ table.strip("\'") for table in tempList ]
        for lcc in lccList:
            gp.AddMessage(lcc)

        infeatures = "//REMOVE/REMOVE/LULCTrends/Vectors/LCCs/LCC_areas_US_alb_areas.shp"
        test = r'in_memory\testlccs'
            
        for lcc in lccList:
            lccname = 'lcc_' + lcc
            if AnalysisNames.isInAnalysisNames( gp, lccname):
                deleteAnalysisName.deleteAnalysisName( lccname)
                
            AnalysisNames.updateAnalysisNames( gp, lccname )
            analysisNum = AnalysisNames.getAnalysisNum( gp, lccname )
            gp.AddMessage("startStratified: lcc = " + lccname + "  analysisNum = " + str(analysisNum))

            subfolder = os.path.join( outFolder, lccname )
            if not os.path.isdir( subfolder ):
                os.mkdir( subfolder )

            where_clause = "Area_Num = " +  str(lccnamelist[ lcc.encode('utf-8') ])
            gp.Select_analysis( infeatures, test, where_clause )
            newEcos, strats, splits = CustomDataAccess.accessCustomData( test, resolution, lccname, subfolder)

            if len(newEcos) > 0:
                testStudyAreaStats.buildStudyAreaStats( lccname, analysisNum, newEcos, strats, splits )

                for eco in newEcos:
                    newExcel = CustomWorkbook( gp, lccname, analysisNum, resolution, subfolder, eco )
                    newExcel.build_workbook( gp )

                newExcel = SummaryWorkbook( gp, lccname, analysisNum, resolution, subfolder )
                newExcel.build_workbook( gp )
                del newExcel
            else:
                deleteAnalysisName.deleteAnalysisName( lccname)

        if gp.Exists( test ):
            gp.delete_management( test )

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
    except TrendsUtilities.JustExit:
        pass
    except Exception:
            gp.AddMessage(traceback.format_exc())

if __name__ == "__main__":
    try:
        gp = arcgisscripting.create(9.3)
        tList = gp.GetParameterAsText(0).split(';')
        res = gp.GetParameterAsText(1)
        oFolder = gp.GetParameterAsText(2)
        startLCCs( tList, res, oFolder )
    except Exception:
        gp.AddMessage(traceback.format_exc())
