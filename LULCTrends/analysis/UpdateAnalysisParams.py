# UpdateAnalysisParams.py
#
# Written:         Nov 2010
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
from ..trendutil import TrendsUtilities, TrendsNames

def updateParameters( tableName, analysisNum, ecoNum, sampleblks, totalblks,
                      totalPix, T85, T90, T95, T99, resolution="", runType = "" ):
    try:
        gp = arcgisscripting.create(9.3)    
        trlog = TrendsUtilities.trLogger()
        trlog.trwrite("Writing analysis parameters to " + tableName + " table    " + time.asctime())  
            
        tableLoc = TrendsNames.dbLocation + tableName
        if analysisNum == TrendsNames.TrendsNum:
            #Update existing rows in table
            where_clause = "Ecoregion = " + str(ecoNum)

            rows = gp.UpdateCursor( tableLoc, where_clause )
            row = rows.Next()  #Get the row
            if row:
                row.num_samples = sampleblks
                row.Total_Blocks = totalblks
                row.TotalPixels = totalPix
                row.StudentT_85 = T85
                row.StudentT_90 = T90
                row.StudentT_95 = T95
                row.StudentT_99 = T99
                rows.UpdateRow( row )
            else:  #trenderror
                pass
        elif ecoNum > 0:
            #insert new rows for custom ecoregion
            rows = gp.InsertCursor( tableLoc )
            row = rows.NewRow()
            row.AnalysisNum = analysisNum
            row.Ecoregion = ecoNum
            row.SampleBlks = sampleblks
            row.TotalBlks = totalblks
            row.Resolution = resolution
            row.RunType = runType
            row.TotalPixels = totalPix
            row.StudentT_85 = T85
            row.StudentT_90 = T90
            row.StudentT_95 = T95
            row.StudentT_99 = T99
            rows.InsertRow( row )
        else:
            #Insert new rows for summary
            rows = gp.InsertCursor( tableLoc )
            row = rows.NewRow()
            row.AnalysisNum = analysisNum
            row.num_samples = sampleblks
            row.Resolution = resolution
            row.Total_Blocks = totalblks
            row.TotalPixels = totalPix
            row.StudentT_85 = T85
            row.StudentT_90 = T90
            row.StudentT_95 = T95
            row.StudentT_99 = T99
            rows.InsertRow( row )

    except arcgisscripting.ExecuteError:
        msgs = gp.GetMessage(0)
        msgs += gp.GetMessages(2)
        trlog.trwrite(msgs)
        raise            
    except TrendsUtilities.TrendsErrors, Terr:
        trlog.trwrite( Terr.message )
        raise
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        trlog.trwrite(pymsg)
        raise  #push the error up to exit
    finally:
        try:
            del row, rows
        except Exception:
            pass
