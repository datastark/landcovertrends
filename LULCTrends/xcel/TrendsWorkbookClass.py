#TrendsWorkbookClass.py
#
# extends the ExcelWorkbook class for creating a
#  workbook for an ecoregion in the Trends tables
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
from ..trendutil import TrendsNames, TrendsUtilities
from .ExcelWorkbookClass import ExcelWorkbook
from . import ExcelSaveFix, createExcelEcoregion

class TrendsWorkbook (ExcelWorkbook):

    def __init__(self, gp, analysisName, analysisNum, res, outfolder, eco):
        try:
            ExcelWorkbook.__init__(self, gp, analysisName, analysisNum, res, outfolder)
            self.eco = eco
            self.reportType = "Trends"
            self.ecoData = self.get_ecoregions( gp, eco )
            self.totalPix['standardconversion'] = self.ecoData[3]
            self.intervals, self.years,self.incyears, self.bookends, self.multiIntervals = self.get_intervals_and_years(gp)
            self.cumulativeintervals = self.get_aggregate_intervals_and_years(gp, 'gross')
            self.ecoHolder = createExcelEcoregion.EcoExcel( gp, eco, self.ecoData[1],
                                self.ecoData[2], res, self.intervals, self.years, self.multiIntervals,
                                analysisNum)
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def get_ecoregions(self, gp, eco ):
        try:
            dataset = TrendsNames.dbLocation + "Ecoregions"
            where_clause = "Ecoregion = " + str( eco )
            rows = gp.SearchCursor( dataset, where_clause )
            row = rows.Next()
            ecoData = (row.Ecoregion, row.Total_Blocks, row.num_samples,
                            row.TotalPixels, row.StudentT_85, row.StudentT_90,
                            row.StudentT_95, row.StudentT_99 )
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
        try:
            tableLoc = TrendsNames.dbLocation + "TrendsChangeData"
            where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                           " and EcoLevel3ID = " + str(self.eco) + \
                           " and Resolution = '" + str(self.resolution) + "'"
            field = "ChangePeriod"
            intervals, years = TrendsUtilities.getIntervalList( gp, tableLoc, where_clause, field)
            incyears = [(years[x]+'to'+years[x+1]) for x in range(len(years)) if years[x] != years[-1]]
            bookends = [inc for inc in intervals if inc not in incyears]

            tableLoc = TrendsNames.dbLocation + "TrendsMultichangeData"
            where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                           " and EcoLevel3ID = " + str(self.eco) + \
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
            tableLoc = TrendsNames.dbLocation + "TrendsAggregateData"
            where_clause = "AnalysisNum = " + str(self.analysisNum) + \
                           " and EcoLevel3ID = " + str(self.eco) + \
                           " and Resolution = '" + str(self.resolution) + "'" + \
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
            self.ecoHolder.loadDataAndStatisticsTables( gp )
            self.dheader, self.sheader = self.ecoHolder.buildHeaders( gp )
            
            ExcelWorkbook.build_workbook( self, gp )
            #write workbook to file
            filename = os.path.join(self.outfolder, "TRENDS_ECOREG" + str(self.eco) + \
                                    "_CHANGE_STRATA_AUTO_" + self.justdate + ".xls")
            gp.Addmessage("Storing ecoregion " + str(self.eco) + " workbook: " + filename)
            self.workbook.save( filename )
            ExcelSaveFix.excelsave( gp, filename )
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_interval_page( self, gp, interval ):
        try:
            worksheet = ExcelWorkbook.build_interval_page( self, gp, interval,
                                                           self.dheader,
                                                           self.ecoHolder.ecoData[interval][0],
                                                           self.sheader,
                                                           self.ecoHolder.ecoData[interval][1])

            self.add_glgn_entries_to_page( gp, worksheet, interval,
                                            len(self.dheader),
                                            self.ecoHolder.ecoGlgn[interval] )

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_aggregate_interval_page( self, gp, interval, source ):
        try:
            worksheet = ExcelWorkbook.build_aggregate_interval_page( self, gp,
                                                        self.dheader,
                                                        self.ecoHolder.aggregate[interval][source][0],
                                                        self.sheader,
                                                        self.ecoHolder.aggregate[interval][source][1],
                                                        interval, source )

            self.add_glgn_entries_to_page( gp, worksheet, interval,
                                            len(self.dheader),
                                            self.ecoHolder.aggGlgn[interval][source] )

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_allchange_page( self, gp ):
        try:
            ExcelWorkbook.build_allchange_page( self, gp,
                                                self.dheader,
                                                self.sheader,
                                                self.ecoHolder.allChange )

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
