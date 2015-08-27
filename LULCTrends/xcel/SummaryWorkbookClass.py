#SummaryWorkbookClass.py
#
# extends the ExcelWorkbook class for creating a
#  workbook for a summary in the summary tables
#
# Written:         Feb 2011
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
from .ExcelWorkbookClass import ExcelWorkbook
from . import ExcelSaveFix
from .ExcelStyleNames import header_style, stat_style, bold_italic_style, plain_italic_style
from .ExcelStyleNames import bold_stat_style, short_style
from .ExcelStyleNames import plain_2dig_style, italic_2dig_style, bold_2dig_style
from ..trendutil import TrendsNames, TrendsUtilities
from ..analysis import StudyAreaClass
from ..analysis.setUpCalcStructures import setUpSummaryArrays
from ..analysis.restoreSummaryFromDB import loadSummary, loadEcosForSummary

class SummaryWorkbook (ExcelWorkbook):

    def __init__(self, gp, analysisName, analysisNum, res, outfolder):
        try:
            ExcelWorkbook.__init__(self, gp, analysisName, analysisNum, res, outfolder)
            self.reportType = "Summary"
            
            # Reading:  Total_Blocks, num_samples, TotalPixels, Resolution,
            #         StudentT_85, StudentT_90, StudentT_95, StudentT_99
            
            self.params = self.ParamRead( gp, self.analysisNum )
            self.resolution = self.params[3]
            self.totalPix['standardconversion'] = self.params[2]
            self.ecoData = self.get_ecoregions( gp, analysisNum )
            self.ecoList = [x[0] for x in self.ecoData]
            self.ecoList.sort()
            self.intervals,self.years,self.incyears,self.bookends,self.multiIntervals = self.get_intervals_and_years(gp)
            self.cumulativeintervals = self.get_aggregate_intervals_and_years(gp, 'gross')
            self.summary = StudyAreaClass.studyArea( gp, analysisName, analysisNum)
            self.summary.resolution = self.params[3]
            self.summary.intervals = self.intervals
            self.summary.aggIntervals = self.cumulativeintervals #expand for more agg types
            self.summary.years = self.years
            self.summary.multiIntervals = self.multiIntervals
            self.summary.sumEstPixels = self.params[2]
            self.summary.summarySamples = self.params[1]
            self.summary.totalBlocks = self.params[0]
            self.summary.studentT = [self.params[4],self.params[5],
                                     self.params[6],self.params[7]]
            self.sheader = TrendsNames.sumprintNames
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def get_ecoregions(self, gp, runNum ):
        try:
            dataset = TrendsNames.dbLocation + "SummaryEcoregions"
            where_clause = "AnalysisNum = " + str( runNum )
            rows = gp.SearchCursor( dataset, where_clause )
            row = rows.Next()
            ecoData = []
            while row:
                ecoData.append((row.Ecoregion, row.TotalBlks, row.SampleBlks,
                                row.TotalPixels, row.StudentT_85, row.StudentT_90,
                                row.StudentT_95, row.StudentT_99, row.Resolution,
                                row.RunType))
                row = rows.Next()
            return ecoData
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
        finally:
            try:
                del row, rows
            except Exception:
                pass

    def get_intervals_and_years(self, gp):
        #Get number of intervals for this study
        try:
            tableLoc = TrendsNames.dbLocation + "SummaryChangeStats"
            field = "ChangePeriod"
            where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                           " and Resolution = '" + str(self.resolution) + "'"
            intervals, years = TrendsUtilities.getIntervalList( gp, tableLoc, where_clause, field)
            incyears = [(years[x]+'to'+years[x+1]) for x in range(len(years)) if years[x] != years[-1]]
            bookends = [inc for inc in intervals if inc not in incyears]

            tableLoc = TrendsNames.dbLocation + "SummaryMultichangeStats"
            where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                           " and Resolution = '" + str(self.resolution) + "'"
            field = "ChangePeriod"
            multiIntervals, noyears = TrendsUtilities.getIntervalList( gp, tableLoc, where_clause, field)

            return intervals, years, incyears, bookends, multiIntervals
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def get_aggregate_intervals_and_years(self, gp, source):
        #Upgrade: expand this to first check for different types of aggregation and then
        #check for the intervals of each type.  Right now it only looks for 'gross'
        try:
            tableLoc = TrendsNames.dbLocation + "SummaryAggregateStats"
            where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                           " and Source = '" + source + "'"
            field = "ChangePeriod"
            intervals, years = TrendsUtilities.getIntervalList( gp, tableLoc, where_clause, field)
            return intervals
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
        
    def build_workbook( self, gp ):
        try:
            #Set up the summary object arrays and load from the database.  These
            # modules are really methods of the summary object.
            setUpSummaryArrays( self.summary )
            loadSummary( self.summary )
            loadEcosForSummary( self.summary, self.ecoData )
            
            ExcelWorkbook.build_workbook( self, gp )
            #write workbook to file
            filename = os.path.join(self.outfolder,"SUMMARY_" + self.analysisName.upper() + \
                                    "_CHANGE_STRATA_AUTO_" + self.justdate + ".xls")
            gp.Addmessage("Storing summary workbook: " + filename)
            self.workbook.save( filename )
            ExcelSaveFix.excelsave( gp, filename )
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def ParamRead( self, gp, runNum ):
        try:
            tableName = TrendsNames.dbLocation + "SummaryAnalysisParams"
            where_clause = "AnalysisNum = " + str(runNum)
            rows = gp.SearchCursor( tableName, where_clause )
            row = rows.Next()
            return (row.Total_Blocks, row.num_samples, row.TotalPixels, row.Resolution,
                      row.StudentT_85, row.StudentT_90, row.StudentT_95, row.StudentT_99)
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
        finally:
            try:
                del row, rows
            except Exception:
                pass
            
    def add_front_page( self, gp ):
        try:
            #add a worksheet to the workbook for this page
            worksheet = self.workbook.add_sheet( "General" )

            #Set up header row, freeze panes
            worksheet.write(1, 0, self.analysisName, header_style)
            worksheet.write(1, 5, "DATA RETRIEVAL DATE:", header_style)
            readdate = self.justdate[:2] + "/" + self.justdate[2:4] + "/" + self.justdate[4:]
            worksheet.write(2, 5, readdate, header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(1)
            worksheet.set_remove_splits(True)

            # Reading:  Total_Blocks, num_samples, TotalPixels, Resolution,
            #         StudentT_85, StudentT_90, StudentT_95, StudentT_99

            worksheet.write(3, 0, "TOTAL BLOCKS", header_style)
            worksheet.write(3, 1, self.params[0])
            worksheet.write(5, 0, "SAMPLE BLOCKS", header_style)
            worksheet.write(5, 1, self.params[1])
            worksheet.write(7, 0, "TOTAL PIXELS", header_style)
            worksheet.write(7, 1, self.params[2])
            worksheet.write(9, 0, "STUDENT T 85%", header_style)
            worksheet.write(9, 1, self.params[4], stat_style)
            worksheet.write(10, 0, "STUDENT T 90%", header_style)
            worksheet.write(10, 1, self.params[5], stat_style)
            worksheet.write(11, 0, "STUDENT T 95%", header_style)
            worksheet.write(11, 1, self.params[6], stat_style)
            worksheet.write(12, 0, "STUDENT T 99%", header_style)
            worksheet.write(12, 1, self.params[7], stat_style)
            
            self.ecoData.sort()
            worksheet.write(15, 0, "INDIVIDUAL ECOREGIONS", header_style)
            worksheet.write(17, 0, "ECOREGION", header_style)
            worksheet.write(17, 1, "TOTAL BLOCKS", header_style)
            worksheet.write(17, 2, "SAMPLE BLOCKS", header_style)
            worksheet.write(17, 3, "TOTAL PIXELS", header_style)
            worksheet.write(17, 4, "STUDENT'S T", header_style)
            for row, entry in enumerate( self.ecoData ):
                worksheet.write(18+row, 0, entry[0])
                worksheet.write(18+row, 1, entry[1])
                worksheet.write(18+row, 2, entry[2])
                worksheet.write(18+row, 3, entry[3])
                worksheet.write(18+row, 4, entry[4], plain_2dig_style)
               
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
        
    def build_interval_page( self, gp, interval ):
        try:
            sheader = self.sheader
            srows = self.summary.summary[interval][1].tolist()
            statsums = numpy.sum(self.summary.summary[interval][1], axis=0)
            
            if self.resolution == "60m":
                sqkm = 0.0036
            else:  # 30m resolution
                sqkm = 0.0009
            student85 = self.params[4]

            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( interval )

            #Set up header row, freeze panes
            worksheet.write(1, 1, interval.split("to")[0], header_style)
            worksheet.write(1, 2, interval.split("to")[1], header_style)

            statstart = 3+ len(self.ecoList)*2
            
            for index, ecoNum in enumerate( self.ecoList ):
                worksheet.write(0, 3+index*2, "Eco", header_style)
                worksheet.write(0, 4+index*2, str(ecoNum), header_style)
                worksheet.write(1, 3+index*2, "Est.Chg(pix)", header_style)
                worksheet.write(1, 4+index*2, "Est.Var(pix)", header_style)
            for index, colheader in enumerate(sheader):
                worksheet.write(1, statstart+index, colheader.replace(".","_"), header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(2)
            worksheet.set_remove_splits(True)

            #Write out estimated change and estimated variance for each ecoregion in the summary
            # The ecoregion arrays here are defined only for 2 stats columns in setUpCalcStructures
            #  setUpShortEcoArrays
            for index, ecoNum in enumerate( self.ecoList ):
                conv = self.summary.study[ecoNum].conv[interval].tolist()
                sumchg = numpy.sum(self.summary.study[ecoNum].conv[interval], axis=0)
                for rowidx, row in enumerate( conv ):
                    worksheet.write( rowidx+2, 3+index*2, conv[rowidx][0], plain_2dig_style)
                    worksheet.write( rowidx+2, 4+index*2, conv[rowidx][1], plain_2dig_style)
                #write totals
                worksheet.write(len(self.ctrans)+2, 3+index*2, sumchg[0], bold_2dig_style)
                worksheet.write(len(self.ctrans)+2, 4+index*2, sumchg[1], bold_2dig_style)
                allch = self.summary.study[ecoNum].allchg[interval]['conversion'].tolist()
                worksheet.write(len(self.ctrans)+4, 3+index*2, allch[0][0], bold_2dig_style)
                worksheet.write(len(self.ctrans)+4, 4+index*2, allch[0][1], bold_2dig_style)

            # Write stat rows
            for rowidx, row in enumerate(srows):
                worksheet.write(rowidx+2, 0, rowidx+1) #add transition id to first column
                worksheet.write(rowidx+2, 1, self.ctrans[rowidx][ 0])   #write 'from' class
                worksheet.write(rowidx+2, 2, self.ctrans[rowidx][ 1])   #write 'to' class
                for colindex, col in enumerate(row):
                    worksheet.write(rowidx+2, colindex+statstart, col, plain_2dig_style)

            #Write estimated change, std. error, and 85% CI in sq.km. after statistics columns
            start = len(sheader) + statstart
            worksheet.write(1, start,"EST.CHANGE(sqkm)", header_style)
            worksheet.write(1, start+1,"STD.ERROR(sqkm)", header_style)
            worksheet.write(1, start+2,"85% CI +-(sqkm)", header_style)
            for rowidx, row in enumerate(srows):
                worksheet.write(rowidx+2, start,
                                row[TrendsNames.sumStatsNames.index("TotalChng")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+1,
                                row[TrendsNames.sumStatsNames.index("StdError")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+2,
                                row[TrendsNames.sumStatsNames.index("StdError")]*student85*sqkm, short_style)

            # Write out the first 3 column totals
            worksheet.write(len(srows)+2, 1,"TOTALS", header_style)
            for colindex, col in enumerate(statsums[:3]):
                worksheet.write(len(srows)+2, colindex+statstart, col, bold_2dig_style)

            # Write the change totals below all data and stats cols
            change_srows = self.summary.sumallchange[interval]['conversion'][1].tolist()
            worksheet.write(len(srows)+4, 1,"ALL CHANGE", header_style)
            for rowidx, row in enumerate(change_srows):
                for colindex, col in enumerate(row):
                    worksheet.write(len(srows)+4+rowidx, colindex+statstart, col, bold_2dig_style)

            worksheet.write(len(srows)+4, start,
                                change_srows[0][TrendsNames.sumStatsNames.index("TotalChng")]*sqkm, short_style)
            worksheet.write(len(srows)+4, start+1,
                                change_srows[0][TrendsNames.sumStatsNames.index("StdError")]*sqkm, short_style)
            worksheet.write(len(srows)+4, start+2,
                                change_srows[0][TrendsNames.sumStatsNames.index("StdError")]*student85*sqkm, short_style)

            #Pick up the change, stderror, and class transition in order to create common
            # conversions page later.
            self.ranking[ interval ] = []
            for index, row in enumerate(srows):
                if (index in self.chngList) and (row[TrendsNames.sumStatsNames.index("TotalChng")] > 0.0):
                    self.ranking[ interval ].append((row[TrendsNames.sumStatsNames.index("TotalChng")],
                                                row[TrendsNames.sumStatsNames.index("StdError")],
                                                index))
                    
            self.add_glgn_entries_to_page( gp, worksheet, interval )

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
        
    def add_glgn_entries_to_page( self, gp, worksheet, interval ):
        try:
            rowoffset = len(self.ctrans) + 9
            
            if self.resolution == "60m":
                sqkm = 0.0036
            else:  # 30m resolution
                sqkm = 0.0009
            student85 = self.params[4]
            statstart = 3+ len(self.ecoList)*2

            for tab in TrendsNames.glgnTabTypes:

                #Write out estimated change and estimated variance for each ecoregion in the summary
                # The ecoregion arrays here are defined only for 2 stats columns in setUpCalcStructures
                #  setUpShortEcoArrays
                for index, ecoNum in enumerate( self.ecoList ):
                    glgn = self.summary.study[ecoNum].glgn[interval][tab].tolist()
                    for rowidx, row in enumerate( glgn ):
                        worksheet.write( rowidx+rowoffset, 3+index*2, glgn[rowidx][0], plain_2dig_style)
                        worksheet.write( rowidx+rowoffset, 4+index*2, glgn[rowidx][1], plain_2dig_style)

                # Write stat rows
                srows = self.summary.sumglgn[interval][tab][1].tolist()
                for rowidx, row in enumerate(srows):
                    if rowidx == 0:
                        worksheet.write(rowidx+rowoffset, 0, tab, header_style)   #write table name
                    worksheet.write(rowidx+rowoffset, 1, self.types[rowidx])   #write to class
                    for colindex, col in enumerate(row):
                        worksheet.write(rowidx+rowoffset, colindex+statstart, col, plain_2dig_style)

                start = len(srows[0]) + statstart
                for rowidx, row in enumerate(srows):
                    worksheet.write(rowidx+rowoffset, start,
                                    row[TrendsNames.sumStatsNames.index("TotalChng")]*sqkm, short_style)
                    worksheet.write(rowidx+rowoffset, start+1,
                                    row[TrendsNames.sumStatsNames.index("StdError")]*sqkm, short_style)
                    worksheet.write(rowidx+rowoffset, start+2,
                                    row[TrendsNames.sumStatsNames.index("StdError")]*student85*sqkm, short_style)
                rowoffset += len(self.types) + 1
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_aggregate_interval_page( self, gp, interval, source ):
        try:
            sheader = self.sheader
            if source == 'gross':
                label = 'Cumul'
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( label+interval )
            
            if self.resolution == "60m":
                sqkm = 0.0036
            else:  # 30m resolution
                sqkm = 0.0009
            student85 = self.params[4]
            statstart = 3+ len(self.ecoList)*2

            #Set up header row, freeze panes
            worksheet.write(1, 1, interval.split("to")[0], header_style)
            worksheet.write(1, 2, interval.split("to")[1], header_style)
            
            for index, ecoNum in enumerate( self.ecoList ):
                worksheet.write(0, 3+index*2, "Eco", header_style)
                worksheet.write(0, 4+index*2, str(ecoNum), header_style)
                worksheet.write(1, 3+index*2, "Est.Chg(pix)", header_style)
                worksheet.write(1, 4+index*2, "Est.Var(pix)", header_style)
            for index, colheader in enumerate(sheader):
                worksheet.write(1, index+statstart, colheader.replace(".","_"), header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(2)
            worksheet.set_remove_splits(True)

            #Write out estimated change and estimated variance for each ecoregion in the summary
            # The ecoregion arrays here are defined only for 2 stats columns in setUpCalcStructures
            #  setUpShortEcoArrays
            for index, ecoNum in enumerate( self.ecoList ):
                conv = self.summary.study[ecoNum].aggregate[interval][source].tolist()
                sumchg = numpy.sum(self.summary.study[ecoNum].aggregate[interval][source], axis=0)
                for rowidx, row in enumerate( conv ):
                    worksheet.write( rowidx+2, 3+index*2, conv[rowidx][0], plain_2dig_style)
                    worksheet.write( rowidx+2, 4+index*2, conv[rowidx][1], plain_2dig_style)
                #write totals
                worksheet.write(len(self.ctrans)+2, 3+index*2, sumchg[0], bold_2dig_style)
                worksheet.write(len(self.ctrans)+2, 4+index*2, sumchg[1], bold_2dig_style)
                allch = self.summary.study[ecoNum].allchg[interval]['addgross'].tolist()
                worksheet.write(len(self.ctrans)+4, 3+index*2, allch[0][0], bold_2dig_style)
                worksheet.write(len(self.ctrans)+4, 4+index*2, allch[0][1], bold_2dig_style)
            
            self.totalPix[source] = \
                numpy.sum(self.summary.sumaggregate[ interval ][source][1][:,TrendsNames.sumStatsNames.index('TotalChng')])
            statsums = numpy.sum(self.summary.sumaggregate[interval][source][1], axis=0)
            srows = self.summary.sumaggregate[interval][source][1].tolist()

            # Write stat rows
            for rowidx, row in enumerate(srows):
                worksheet.write(rowidx+2, 0, rowidx+1) #add transition id to first column
                worksheet.write(rowidx+2, 1, self.ctrans[rowidx][ 0])   #write 'from' class
                worksheet.write(rowidx+2, 2, self.ctrans[rowidx][ 1])   #write 'to' class
                for colindex, col in enumerate(row):
                    worksheet.write(rowidx+2, colindex+statstart, col, plain_2dig_style)

            #Write estimated change, std. error, and 85% CI in sq.km. after statistics columns
            start = len(sheader) + statstart
            worksheet.write(1, start,"EST.CHANGE(sqkm)", header_style)
            worksheet.write(1, start+1,"STD.ERROR(sqkm)", header_style)
            worksheet.write(1, start+2,"85% CI +-(sqkm)", header_style)
            for rowidx, row in enumerate(srows):
                worksheet.write(rowidx+2, start,
                                row[TrendsNames.sumStatsNames.index("TotalChng")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+1,
                                row[TrendsNames.sumStatsNames.index("StdError")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+2,
                                row[TrendsNames.sumStatsNames.index("StdError")]*student85*sqkm, short_style)

            # Write out the first 6 column totals
            worksheet.write(len(srows)+2, 1,"TOTALS", header_style)
            for colindex, col in enumerate(statsums[:3]):
                worksheet.write(len(srows)+2, colindex+statstart, col, bold_2dig_style)

            # Write the change totals below all data and stats cols
            worksheet.write(len(srows)+4, 1,"ALL CHANGE", header_style)
            change_srows = self.summary.sumallchange[interval]['addgross'][1].tolist()
            for rowidx, row in enumerate(change_srows):
                for colindex, col in enumerate(row):
                    worksheet.write(len(srows)+4+rowidx, colindex+statstart, col, bold_2dig_style)

            worksheet.write(len(srows)+4, start,
                                change_srows[0][TrendsNames.sumStatsNames.index("TotalChng")]*sqkm, short_style)
            worksheet.write(len(srows)+4, start+1,
                                change_srows[0][TrendsNames.sumStatsNames.index("StdError")]*sqkm, short_style)
            worksheet.write(len(srows)+4, start+2,
                                change_srows[0][TrendsNames.sumStatsNames.index("StdError")]*student85*sqkm, short_style)

            #Pick up the change, stderror, and class transition in order to create common
            # conversions page later.
            self.ranking[ label+interval ] = []
            for index, row in enumerate(srows):
                if (index in self.chngList) and (row[TrendsNames.sumStatsNames.index("TotalChng")] > 0.0):
                    self.ranking[ label+interval ].append((row[TrendsNames.sumStatsNames.index("TotalChng")],
                                                row[TrendsNames.sumStatsNames.index("StdError")],
                                                index))
                    
            self.add_aggregate_glgn_entries_to_page( gp, worksheet, interval, source )

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
        
    def add_aggregate_glgn_entries_to_page( self, gp, worksheet, interval, source ):
        try:
            if self.resolution == "60m":
                sqkm = 0.0036
            else:  # 30m resolution
                sqkm = 0.0009
            student85 = self.params[4]
            rowoffset = len(self.ctrans) + 9
            statstart = 3+ len(self.ecoList)*2

            for tab in TrendsNames.glgnTabTypes:

                #Write out estimated change and estimated variance for each ecoregion in the summary
                # The ecoregion arrays here are defined only for 2 stats columns in setUpCalcStructures
                #  setUpShortEcoArrays
                for index, ecoNum in enumerate( self.ecoList ):
                    glgn = self.summary.study[ecoNum].aggGlgn[interval][source][tab].tolist()
                    for rowidx, row in enumerate( glgn ):
                        worksheet.write( rowidx+rowoffset, 3+index*2, glgn[rowidx][0], plain_2dig_style)
                        worksheet.write( rowidx+rowoffset, 4+index*2, glgn[rowidx][1], plain_2dig_style)

                srows = self.summary.sumaggglgn[interval][source][tab][1].tolist()
                # Write stat rows
                for rowidx, row in enumerate(srows):
                    if rowidx == 0:
                        worksheet.write(rowidx+rowoffset, 0, tab, header_style)   #write table name
                    worksheet.write(rowidx+rowoffset, 1, self.types[rowidx])   #write to class
                    for colindex, col in enumerate(row):
                        worksheet.write(rowidx+rowoffset, colindex+statstart, col, plain_2dig_style)

                start = len(srows[0]) + statstart
                for rowidx, row in enumerate(srows):
                    worksheet.write(rowidx+rowoffset, start,
                                    row[TrendsNames.sumStatsNames.index("TotalChng")]*sqkm, short_style)
                    worksheet.write(rowidx+rowoffset, start+1,
                                    row[TrendsNames.sumStatsNames.index("StdError")]*sqkm, short_style)
                    worksheet.write(rowidx+rowoffset, start+2,
                                    row[TrendsNames.sumStatsNames.index("StdError")]*student85*sqkm, short_style)
                rowoffset += len(self.types) + 1
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_composition_page( self, gp ):
        try:
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "YearlyStats" )
            sheader = self.sheader
            statstart = 2+ len(self.ecoList)*2
            
            for index, ecoNum in enumerate( self.ecoList ):
                worksheet.write(0, 2+index*2, "Eco", header_style)
                worksheet.write(0, 3+index*2, str(ecoNum), header_style)
                worksheet.write(1, 2+index*2, "Est.Comp(pix)", header_style)
                worksheet.write(1, 3+index*2, "Est.Var(pix)", header_style)
            for index, colheader in enumerate(sheader):
                colname = colheader
                if colname == "TotalChng(pix)":
                    colname = "TotalComp(pix)"
                if colname == "ChgPercent(%)":
                    colname = "CompPercent(%)"
                worksheet.write(1, statstart+index, colname.replace(".","_"), header_style)
                
            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(2)
            worksheet.set_remove_splits(True)
            
            LCoffset = 8

            #Write out estimated change and estimated variance for each ecoregion in the summary
            # The ecoregion arrays here are defined only for 2 stats columns in setUpCalcStructures
            #  setUpShortEcoArrays

            for ptr, year in enumerate(self.years):
                for index, ecoNum in enumerate( self.ecoList ):
                    conv = self.summary.study[ecoNum].comp[year].tolist()
                    for rowidx, row in enumerate( conv ):
                        rowptr = (rowidx*LCoffset)+2+ptr
                        worksheet.write( rowptr, 2+index*2, conv[rowidx][0], plain_2dig_style)
                        worksheet.write( rowptr, 3+index*2, conv[rowidx][1], plain_2dig_style)

                srows = self.summary.sumcomp[year][1].tolist()
                #Now add the year, the LC type, and the stats
                # Write stat rows
                for rowidx, row in enumerate(srows):
                    rowptr = (rowidx*LCoffset)+2+ptr
                    worksheet.write(rowptr, 0, year, header_style)                #write year
                    worksheet.write(rowptr, 1, self.types[rowidx], header_style)       #write class
                    for colindex, col in enumerate(row):
                        worksheet.write(rowptr, colindex+statstart, col, plain_2dig_style)
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)

    def build_yearlysummary_page( self, gp ):
        try:
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "Yearly Summary" )
            
            lcs = TrendsNames.LCshort
            #Put on the header row
            worksheet.write(0,1, "Land Cover Trends", header_style)
            worksheet.write(1,0, "(%Eco)", header_style)
            for index, colheader in enumerate(lcs):
                worksheet.write(1, index+2, colheader, header_style)
                
            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(1)
            worksheet.set_remove_splits(True)

            #Now add the year and the %total ecoregion stat
            for rowidx, year in enumerate(self.years):
                worksheet.write(rowidx+2, 1, year, header_style)
                for col in range(len(self.types)):
                    worksheet.write(rowidx+2, col+2,
                        self.summary.sumcomp[year][1][col,TrendsNames.sumStatsNames.index('ChgPercent')],
                                    plain_2dig_style)

            student85 = self.params[4]
            rowoffset = len(self.years)+3
            first = self.years[0]
            last = self.years[-1]
            netdif = [0.0 for x in range(len(self.types))]
            #calculate the first year / last year difference for each lc type
            worksheet.write(rowoffset, 1, str(first)+"-"+str(last), bold_italic_style)
            for col in range(len(self.types)):
                netdif[col] = self.summary.sumcomp[last][1][col,TrendsNames.sumStatsNames.index('ChgPercent')] - \
                      self.summary.sumcomp[first][1][col,TrendsNames.sumStatsNames.index('ChgPercent')]
                worksheet.write(rowoffset, col+2,netdif[col],italic_2dig_style)

            trendsTableLen = len(self.years) + 9
            trendsTabWidth = len(self.types) + 2

            #Add the transposed %ecoregion table with standard error and confidence intervals

            startcol = trendsTabWidth + 2
            for colidx, year in enumerate(self.years):
                worksheet.write(0, startcol+1+colidx*3, year, header_style)
                worksheet.write(0, startcol+2+colidx*3, year, header_style)
                worksheet.write(0, startcol+3+colidx*3, year, header_style)
                worksheet.write(1, startcol+1+colidx*3, "Estimate(%)", header_style)
                worksheet.write(1, startcol+2+colidx*3, "Std. Err(%)", header_style)
                worksheet.write(1, startcol+3+colidx*3, "85% +/-CI(%)  ", header_style)
            for index, colheader in enumerate(lcs):
                worksheet.write(index+2, startcol, colheader, header_style)
                for col,year in enumerate(self.years):
                    worksheet.write(index+2, startcol+1+col*3,
                        self.summary.sumcomp[year][1][index,TrendsNames.sumStatsNames.index('ChgPercent')],
                                    plain_2dig_style)
                    worksheet.write(index+2, startcol+2+col*3,
                        self.summary.sumcomp[year][1][index,TrendsNames.sumStatsNames.index('PerStdErr')],
                                    plain_2dig_style)
                    worksheet.write(index+2, startcol+3+col*3,
                        self.summary.sumcomp[year][1][index,TrendsNames.sumStatsNames.index('PerStdErr')]*student85,
                                    plain_2dig_style)

            totaldif = int(last) - int(first)
            #Now write net, gross, gain, and loss tables for change percent
            rowoffset = trendsTableLen+5
            Titles = ["Net Change by Interval","Gross Change by Interval","Gains","Losses"]
            tabs = ['net','gross','gain','loss']
            for ctr, tab in enumerate(tabs):
                worksheet.write(rowoffset,1, Titles[ctr], header_style)
                worksheet.write(rowoffset,2, "(%Eco)",header_style)
                for index, colheader in enumerate(lcs):
                    worksheet.write(rowoffset+1, index+2, colheader, header_style)
                for rowidx, interval in enumerate(self.intervals):
                    worksheet.write(rowoffset+rowidx+2, 1, interval, header_style)
                    if tab == 'net' and interval == self.intervals[-1]:
                        worksheet.write(rowoffset+rowidx+3, 1, "total",header_style)
                    for col in range(len(self.types)):
                        worksheet.write(rowoffset+rowidx+2, col+2,
                            self.summary.sumglgn[interval][tab][1][col,TrendsNames.sumStatsNames.index('ChgPercent')],
                                    plain_2dig_style)
                        if tab == 'net' and interval == self.intervals[-1]:
                            worksheet.write(rowoffset+rowidx+3, col+2, netdif[col], plain_2dig_style)
                rowoffset = rowoffset + 5 + len(self.intervals)

            #Now write annualized net, gross, gain, and loss tables for change percent
            rowoffset = trendsTableLen+5
            coloffset = len(self.types)+4
            Titles = ["Average Annual Net Change","Average Annual Gross Change",
                      "Average Annual Gains","Average Annual Losses"]
            tabs = ['net','gross','gain','loss']
            worksheet.write(rowoffset-1, coloffset,"Normalized Change",header_style)
            for ctr, tab in enumerate(tabs):
                worksheet.write(rowoffset,coloffset, Titles[ctr], header_style)
                worksheet.write(rowoffset,coloffset+1, "(%Eco)",header_style)
                for index, colheader in enumerate(lcs):
                    worksheet.write(rowoffset+1, coloffset+index+2, colheader, header_style)
                for rowidx, interval in enumerate(self.intervals):
                    temp = interval.split("to")
                    dif = int(temp[1]) - int(temp[0])
                    worksheet.write(rowoffset+rowidx+2, coloffset+1, interval, header_style)
                    if tab == 'net' and interval == self.intervals[-1]:
                        worksheet.write(rowoffset+rowidx+3, coloffset+1, "total",header_style)
                    for col in range(len(self.types)):
                        worksheet.write(rowoffset+rowidx+2, coloffset+col+2,
                            self.summary.sumglgn[interval][tab][1][col,TrendsNames.sumStatsNames.index('ChgPercent')]/float(dif),
                                    plain_2dig_style)
                        if tab == 'net' and interval == self.intervals[-1]:
                            worksheet.write(rowoffset+rowidx+3, coloffset+col+2, netdif[col]/float(totaldif),plain_2dig_style)
                rowoffset = rowoffset + 5 + len(self.intervals)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_multichange_page( self, gp, interval ):
        try:
            #Get summary table for multichange
            xchg = TrendsNames.MultiMap[ interval ]
            student85 = self.params[4]
            sheader = self.sheader
            snumpyrows = self.summary.summulti[interval][1][:xchg,:]
            statsums = numpy.sum(snumpyrows, axis=0)
            xsums = numpy.sum(snumpyrows, axis=1)
            onlychg = numpy.sum(xsums[1:])
            totalchg = numpy.sum(xsums)
            srows = snumpyrows.tolist()
            percentchg = []
            for x in xsums:
                percentchg.append(float(x)/float(totalchg)*100.0)

            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "footprint" + interval )
            title3 = ["NO CHANGES","1 CHANGE"] + [str(x)+" CHANGES" for x in range(2,xchg)]
            title4 = ("FOOTPRINT","  ","% of ECO(%)","85%+/-(%)","LOWER CI(%)","UPPER CI(%)","STD. ERROR(%)","REL. ERROR(%)")
            statindex = 0 #column to start statistics

            #Set up header row, freeze panes
            for index, colheader in enumerate(sheader):
                worksheet.write(0, index+1, colheader.replace(".","_"), header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(1)
            worksheet.set_remove_splits(True)

            # Write stat rows
            for rowidx, row in enumerate(srows):
                if rowidx == 0:
                    line = 3 + 2*(len(srows)-1)
                else:
                    line = 3 + 2*(rowidx-1)
                worksheet.write(line, statindex, title3[rowidx])
                for colindex, col in enumerate(row):
                    worksheet.write(line, colindex+1+statindex, col, plain_2dig_style)

            # Write the change totals below the other columns
            worksheet.write(1, statindex, "ALL CHANGE")
            change_srows = self.summary.sumallchange[interval]['multichange'][1].tolist()
            for idx, row in enumerate(change_srows):
                for colindex, col in enumerate(row):
                    worksheet.write(1, colindex+1+statindex, col, plain_2dig_style)

            # Create summary table
            sumindex = (TrendsNames.sumStatsNames.index('ChgPercent'),
                        TrendsNames.sumStatsNames.index('PerStdErr'),
                        TrendsNames.sumStatsNames.index('Lo85Conf'),
                        TrendsNames.sumStatsNames.index('Hi85Conf'),
                        TrendsNames.sumStatsNames.index('PerStdErr'),
                        TrendsNames.sumStatsNames.index('RelError'))
            startrow = len(srows)*2 + 6
            startcol = 1
            for colindex, col in enumerate(title4):
                worksheet.write(startrow, startcol+colindex, col, header_style)
            worksheet.write(startrow+1,startcol, interval, header_style)
            worksheet.write(startrow+1,startcol+1, "ALL CHANGE", header_style)
            for x,ptr in enumerate(sumindex):
                if x == 1:
                    worksheet.write(startrow+1, startcol+2+x,change_srows[0][ptr]*student85,plain_2dig_style)
                else:
                    worksheet.write(startrow+1, startcol+2+x,change_srows[0][ptr],plain_2dig_style)
            for rowidx, row in enumerate(title3[1:]):
                worksheet.write(startrow+2+rowidx,startcol+1, row, header_style)
                for x,ptr in enumerate(sumindex):
                    if x == 1:
                        worksheet.write(startrow+2+rowidx, startcol+2+x,srows[rowidx+1][ptr]*student85,plain_2dig_style)
                    else:
                        worksheet.write(startrow+2+rowidx, startcol+2+x,srows[rowidx+1][ptr],plain_2dig_style)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_allchange_page( self, gp ):
        try:
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "Per_Period_Change" )
            student85 = self.params[4]


            #Set up header row, freeze panes
            worksheet.write(0, 0,"Estimated Change",header_style)
            worksheet.write(1, 2, "Change Est.(%)", header_style)
            worksheet.write(1, 3, "+/-(%)", header_style)
            worksheet.write(1, 4, "85%Lo(%)", header_style)
            worksheet.write(1, 5, "85%Hi(%)", header_style)
            worksheet.write(1, 6, "Std.Err.(%)", header_style)
            worksheet.write(1, 7, "Rel.Err.(%)", header_style)
            worksheet.write(1, 8, "Avg.Annual(%)", header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(1)
            worksheet.set_remove_splits(True)

            #write avg annual table
            lowertable = len(self.intervals)+len(self.cumulativeintervals)+10
            worksheet.write(lowertable, 0, "Normalized", header_style)
            worksheet.write(lowertable+1, 0, "Avg. Annual", header_style)
            worksheet.write(lowertable+2, 2, "Change Est.(%)", header_style)
            worksheet.write(lowertable+2, 3, "+/-(%)", header_style)
            worksheet.write(lowertable+2, 4, "85%Lo(%)", header_style)
            worksheet.write(lowertable+2, 5, "85%Hi(%)", header_style)
            worksheet.write(lowertable+2, 6, "Std.Err.(%)", header_style)
            worksheet.write(lowertable+2, 7, "Rel.Err.(%)", header_style)

            # Write overall change intervals and values
            worksheet.write(2, 0, "Conversion", header_style)
            for rowidx, interval in enumerate(self.intervals):
                temp = interval.split("to")
                dif = int(temp[1]) - int(temp[0])
                worksheet.write(rowidx+2, 1,interval.replace('to','-'), header_style)
                worksheet.write(lowertable+rowidx+3, 1,interval.replace('to','-'), header_style)                
                change_srows = self.summary.sumallchange[interval]['conversion'][1].tolist()
                worksheet.write(rowidx+2, 2,
                            change_srows[0][TrendsNames.sumStatsNames.index('ChgPercent')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 2,
                            change_srows[0][TrendsNames.sumStatsNames.index('ChgPercent')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 3,
                            change_srows[0][TrendsNames.sumStatsNames.index('PerStdErr')]*student85,
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 3,
                            change_srows[0][TrendsNames.sumStatsNames.index('PerStdErr')]*student85/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 4,
                            change_srows[0][TrendsNames.sumStatsNames.index('Lo85Conf')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 4,
                            change_srows[0][TrendsNames.sumStatsNames.index('Lo85Conf')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 5,
                            change_srows[0][TrendsNames.sumStatsNames.index('Hi85Conf')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 5,
                            change_srows[0][TrendsNames.sumStatsNames.index('Hi85Conf')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 6,
                            change_srows[0][TrendsNames.sumStatsNames.index('PerStdErr')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 6,
                            change_srows[0][TrendsNames.sumStatsNames.index('PerStdErr')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 7,
                            change_srows[0][TrendsNames.sumStatsNames.index('RelError')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 7,
                            change_srows[0][TrendsNames.sumStatsNames.index('RelError')],
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 8,
                            change_srows[0][TrendsNames.sumStatsNames.index('ChgPercent')]/float(dif),
                                    plain_2dig_style)

            worksheet.write(len(self.intervals)+3, 0, "Cumulative", header_style)
            # Write overall change intervals and values
            for rowidx, interval in enumerate(self.cumulativeintervals):
                temp = interval.split("to")
                dif = int(temp[1]) - int(temp[0])
                avgdif = float(dif)/float(TrendsNames.CumulativeMap[interval]) #for avg annual, divide by avg interval length
                change_srows = self.summary.sumallchange[interval]['addgross'][1].tolist()
                nextrow = rowidx+len(self.intervals)+3
                worksheet.write(nextrow, 1,interval.replace('to','-'), header_style)
                worksheet.write(nextrow, 2,
                            change_srows[0][TrendsNames.sumStatsNames.index('ChgPercent')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 3,
                            change_srows[0][TrendsNames.sumStatsNames.index('PerStdErr')]*student85,
                                    plain_2dig_style)
                worksheet.write(nextrow, 4,
                            change_srows[0][TrendsNames.sumStatsNames.index('Lo85Conf')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 5,
                            change_srows[0][TrendsNames.sumStatsNames.index('Hi85Conf')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 6,
                            change_srows[0][TrendsNames.sumStatsNames.index('PerStdErr')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 7,
                            change_srows[0][TrendsNames.sumStatsNames.index('RelError')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 8,
                            change_srows[0][TrendsNames.sumStatsNames.index('ChgPercent')]/avgdif,
                                    plain_2dig_style)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
