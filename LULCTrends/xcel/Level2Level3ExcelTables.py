# Level2Level3ExcelTables.py
#
# Create an excel file for each Level 2 ecoregion.
# Each file has a page for each change interval.
# For each interval, extract the conversion estimated change values
#  for all the level 3s that make up this level 2 ecoregion.
#  Divide all the values by the corresponding total change value for
#  the level 2 ecoregion.  Write a table to the excel sheet containing
#  121 rows and same number of columns as there are level 3s.  Write
#  the ratio values for each eco to the page.
#
# Written:         Jan 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import arcgisscripting, numpy
import os, sys, traceback, time
import xlwt
from ..trendutil import TrendsNames, AnalysisNames

gp = arcgisscripting.create(9.3)
header_style = xlwt.easyxf("font: bold on; align: horiz center")
stat_style = xlwt.easyxf(num_format_str="#0.00000000")

def extractDBStatistics(gp, sourceName, localName, where_clause ):
    #create a table view of the data for quicker extraction
    try:
        sourceTable = TrendsNames.dbLocation + sourceName
        print("creating query table for " + sourceTable)
        gp.Overwriteoutput = True
        gp.MakeQueryTable_management( sourceTable, localName, "USE_KEY_FIELDS","","",where_clause )

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        gp.AddMessage(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        gp.AddMessage(pymsg)
        raise

def getLevel3ChangeStats( resolution ):
    #get the estimated change for all level 3s
    try:
        gp.OverwriteOutput = True
        
        #Get data from source table into memory
        where_clause = "AnalysisNum = " + str(TrendsNames.TrendsNum) + " and Resolution = \'" + resolution + "\'" + \
                       " and Statistic = \'EstChange\'"
        localTable = "level3s"
        extractDBStatistics( gp, "TrendsChangeStats", localTable, where_clause )

        #get field names and offset for start of conversion values
        desc = gp.Describe( localTable )
        fields = desc.Fields
        for counter, field in enumerate(fields):
            if field.Name == "Statistic":
                offset = counter + 1
        
        return localTable, fields, offset
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise

def getLevel2ChangeStats():
    #get the estimated change for all summaries
    try:
        gp.OverwriteOutput = True
        
        #Get data from source table into memory
        where_clause = "Statistic = \'TotalChng\'"
        localTable = "level2s"
        extractDBStatistics( gp, "SummaryChangeStats", localTable, where_clause )

        #get field names and offset for start of conversion values
        desc = gp.Describe( localTable )
        fields = desc.Fields
        for counter, field in enumerate(fields):
            if field.Name == "Statistic":
                offset = counter + 1
        
        return localTable, fields, offset
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise

def Map2to3():
    #get the level2 to level3 mapping
    try:
        gp.OverwriteOutput = True
        
        #Get data from source table into memory
        where_clause = ""
        localTable = "Map2to3"
        extractDBStatistics( gp, "EcoregionHierarchy", localTable, where_clause )
        return localTable
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise

def getAnalysisMapping():
    try:
        names = []
        for entry in TrendsNames.Level2Names:
            dbname = 'SM_'+entry[0]
            names.append( (entry[0], entry[1], AnalysisNames.getAnalysisNum(gp, dbname)))
        return names
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise

def create_a_workbook( entry, level3values, eco3fields, eco3offset,
                               level2values, eco2fields, eco2offset, map2to3, folderList, outfolder, justdate ):
    try:
        # Make spreadsheet
        workbook = xlwt.Workbook()

        #Get Level3 ecos for this level 2
        print("creating workbook for " + entry[0])
        ecoList = []
        where_clause = "EcoLevel2ID = " + str(entry[1])
        rows = gp.SearchCursor( map2to3, where_clause )
        row = rows.Next()
        while row:
            ecoList.append( int(row.EcoLevel3ID) )
            print("Level 3 eco # " + str(row.EcoLevel3ID))
            row = rows.Next()

        for interval in folderList:
            #create excel page in workbook
            worksheet = workbook.add_sheet( interval )

            totalvals = []
            #extract TotalChng for this interval from local table
            where_clause = "AnalysisNum = " + str(int(entry[2])) + " and ChangePeriod = \'" + interval + "\'"
            rows = gp.SearchCursor( level2values, where_clause )
            row = rows.Next()
            while row:
                for field in eco2fields[eco2offset:]:
                    totalvals.append( row.GetValue( field.Name ))
                row = rows.Next()

            #Create an array to hold all level 3 eco info
            stats = numpy.zeros(((TrendsNames.numConversions), len(ecoList)), float)

            for eco in ecoList:
                #Get estimated change values
                where_clause = "EcoLevel3ID = " + str(eco) + " and ChangePeriod = \'" + interval + "\'"
                rows = gp.SearchCursor( level3values, where_clause )
                row = rows.Next()
                while row:
                    for (ptr, field) in enumerate( eco3fields[eco3offset:]):
                        #write into array column, dividing by totalChange values, check for division by 0
                        if totalvals[ptr] > 0.0:
                            stats[ ptr, ecoList.index(eco) ] = float(row.GetValue( field.Name )) / float(totalvals[ptr])
                    row = rows.Next()

            #write array and header to page
            for index, eco in enumerate(ecoList):
                worksheet.write(0, index+1, eco, header_style)
            
            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(1)
            worksheet.set_remove_splits(True)

            for row in range(0,TrendsNames.numConversions):
                worksheet.write(row+1, 0, row+1, header_style)
                for col in range(len(ecoList)):
                    worksheet.write(row+1, col+1,stats[row,col],stat_style)

        #write workbook to file
        filename = os.path.join(outfolder, entry[0] + "_RATIO_OF_ECO3s_" + justdate + ".xls")
        print("Storing workbook: " + filename)
        workbook.save( filename )
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise
    finally:
        try:
            del row, rows
        except Exception:
            pass

def Eco2Eco3ToExcel( res, outfolder ):
    try:
        #create a time for the filenames
        tmstp = time.localtime()
        justdate = str(tmstp.tm_mon).rjust(2).replace(" ","0") + \
                    str(tmstp.tm_mday).rjust(2).replace(" ","0") + str(tmstp.tm_year)
                          
        folderList = TrendsNames.TrendsIntervals
        level3values, eco3fields, eco3offset = getLevel3ChangeStats( res )
        level2values, eco2fields, eco2offset = getLevel2ChangeStats()
        map2to3 = Map2to3()
        names = getAnalysisMapping()
        for entry in names:
            print ('workbook for ' + entry[0])
            #if entry[0] == 'MISSISSIPPIALLUVIALPLAIN':
            create_a_workbook( entry, level3values, eco3fields, eco3offset,
                               level2values, eco2fields, eco2offset,
                               map2to3, folderList, outfolder, justdate )
        return True
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
        raise

if __name__ == '__main__':
    outfolder = r"REMOVED\Trends\tempStorage\level3sTolevel2s"
    res = "60m"
    try:
        Eco2Eco3ToExcel( res, outfolder )
        print "Complete"
    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        print(msgs)
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print(pymsg)
