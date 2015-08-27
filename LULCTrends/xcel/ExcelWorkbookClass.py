#ExcelWorkbookClass.py
#
# defines a generic Trends-type excel workbook
#  this is later customized to Trends, Custom,or Summary workbook
#

# uses tableto.py from esri code gallery
#
# info on tabletoexcel.py, from which some code here is borrowed:
# http://resources.arcgis.com/gallery/file/geoprocessing?page=3&&galleryVersion=9.3
# Additional Conversion - Generic Tools
# Currently the toolbox contains the Table To Excel - Script tool
# to convert geodatabase feature classes, tables, shapefile
# by gprince (last modified: July 2, 2010)
#
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
# info on xlwt:
# Author: John Machin <sjmachin at lexicon net>
# Download URL: http://pypi.python.org/pypi/xlwt
import xlwt, numpy
from ..trendutil import TrendsNames, TrendsUtilities
from . import student_wilcoxon
from .ExcelStyleNames import header_style, stat_style, bold_italic_style, bold_style
from .ExcelStyleNames import plain_italic_style, short_style, blue_header_style
from .ExcelStyleNames import bold_stat_style, bold_data_style, bold_2dig_style
from .ExcelStyleNames import plain_2dig_style, italic_2dig_style

class ExcelWorkbook:

    def __init__(self, gp, analysisName, analysisNum, res, outfolder):
        try:
            #store information and
            #get the date and time for the filename
            self.analysisName = analysisName
            self.analysisNum = analysisNum
            self.resolution = res
            self.outfolder = outfolder
            tmstp = time.localtime()
            self.justdate = str(tmstp.tm_mon).rjust(2).replace(" ","0") + \
                            str(tmstp.tm_mday).rjust(2).replace(" ","0") + \
                            str(tmstp.tm_year)

            self.ctrans = self.get_class_transitions(gp)
            self.types = self.get_landCover_type(gp)
            self.chngList = [index for index, pair in enumerate(self.ctrans) if pair[0] != pair[1]]
            self.ranking = {}
            self.totalPix = {}  #needs to be filled in by each workbook type
            self.dheader = []  #filled in by each workbook type
            self.sheader = []  #  same
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def header_and_iterator(self, gp, dataset_name):
        try:
            """Returns a list of column names and an iterator over the same columns"""
            #This was written by gprince and obtained from the esri code gallery
            data_description = gp.Describe(dataset_name)
            fieldnames = [f.name for f in data_description.fields if f.type not in ["Geometry", "Raster", "Blob"]]
            def iterator_for_feature():
                cursor = gp.SearchCursor(dataset_name)
                row = cursor.next()
                while row:
                    yield [getattr(row, col) for col in fieldnames]
                    row = cursor.next()
            return fieldnames, iterator_for_feature()
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
                del row, cursor
            except Exception:
                pass

    def find_total_estimated_pixels( self, dataArray, totalBlks, sampleBlks ):
        #Calculate the total estimated change in pixels for this data array (and interval).  This value
        # is used in statistics calculations to determine values as % of ecoregion.
        # It will be recalculated for special case years such as cumulative gross change,
        try:
            return numpy.sum( dataArray ) * (float(totalBlks) / float(sampleBlks))
        except Exception:
            #print out the system error traceback
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise     #push the error up to exit

    def get_class_transitions(self, gp):
        try:
            #Get the fromClass and toClass columns of the ClassTransition table
            dataset = TrendsNames.dbLocation + "ClassTransition"
            header, rows = self.header_and_iterator( gp, dataset )
            fromind = header.index("FromClass")
            toind = header.index("ToClass")
            #Get contents of "FromClass" and "ToClass" columns and build a list of tuples
            return [(row[fromind], row[toind]) for row in rows]
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def get_landCover_type(self, gp):
        try:
            #Get the contents of the LandCoverType table
            dataset = TrendsNames.dbLocation + "LandCoverType"
            header, rows = self.header_and_iterator( gp, dataset)
            lcind = header.index("LandCover")
            #Get contents of "LandCover" column
            return [row[lcind] for row in rows]
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def get_ecoregions(self, gp, runNum ):
        gp.AddMessage("Method get_ecoregions must be defined in each subclass")

    def get_intervals_and_years(self, gp):
        gp.AddMessage("Method get_intervals_and_years must be defined in each subclass")

    def get_aggregate_intervals_and_years(self, gp):
        gp.AddMessage("Method get_aggregate_intervals_and_years must be defined in each subclass")

    def build_workbook( self, gp ):
        try:
            # Make spreadsheet
            self.workbook = xlwt.Workbook()

            #add analysis numbers to the first page of the workbook
            self.add_front_page( gp )

            self.incyears.sort()
            self.bookends.sort()
            self.intervals = self.incyears + self.bookends
            #build a conversion page for each interval, includes glgn
            for interval in self.intervals:
                self.build_interval_page( gp, interval )

            #build aggregated gross change (cumulative) page
            for interval in self.cumulativeintervals:
                self.build_aggregate_interval_page( gp, interval, 'gross' )

            #add a page for composition data and statistics
            self.build_composition_page( gp )

            #add a page for the yearly summary stats
            self.build_yearlysummary_page( gp )

            #add the per period change page
            self.build_allchange_page( gp )

            #build a common conversion page for each interval
            source = 'standardconversion'
            for interval in self.intervals:
                self.build_comconversions_page( gp, interval, source )

            #build a common conversion page for cumulative gross change
            source = 'gross'
            for interval in self.cumulativeintervals:
                self.build_comconversions_page( gp, interval, source )

            #add the multichange page
            for interval in self.multiIntervals:
                self.build_multichange_page( gp, interval )

            #Each specific type of workbook extends this method by writing workbook to file

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def add_front_page( self, gp ):
        try:
            #add a worksheet to the workbook for this page
            worksheet = self.workbook.add_sheet( "General" )

            #Set up header row, freeze panes
            worksheet.write(1, 0, "ECOREGION", header_style)
            worksheet.write(1, 1, self.eco)
            worksheet.write(1, 5, "DATA RETRIEVAL DATE:", header_style)
            readdate = self.justdate[:2] + "/" + self.justdate[2:4] + "/" + self.justdate[4:]
            worksheet.write(2, 5, readdate, header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(1)
            worksheet.set_remove_splits(True)

            #see this class's get_ecoregions method for ecoData values
            worksheet.write(3, 0, "TOTAL BLOCKS", header_style)
            worksheet.write(3, 1, self.ecoData[1])
            worksheet.write(5, 0, "SAMPLE BLOCKS", header_style)
            worksheet.write(5, 1, self.ecoData[2])
            worksheet.write(7, 0, "TOTAL PIXELS", header_style)
            worksheet.write(7, 1, self.ecoData[3])
            worksheet.write(9, 0, "STUDENT T 85%", header_style)
            worksheet.write(9, 1, self.ecoData[4], stat_style)
            worksheet.write(10, 0, "STUDENT T 90%", header_style)
            worksheet.write(10, 1, self.ecoData[5], stat_style)
            worksheet.write(11, 0, "STUDENT T 95%", header_style)
            worksheet.write(11, 1, self.ecoData[6], stat_style)
            worksheet.write(12, 0, "STUDENT T 99%", header_style)
            worksheet.write(12, 1, self.ecoData[7], stat_style)
            
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
            
    def build_interval_page( self, gp, interval, dheader, dnumpyrows, sheader, snumpyrows ):
        try:
            worksheet = self.workbook.add_sheet( interval )

            #Set up header row, freeze panes
            worksheet.write(1, 1, interval.split("to")[0], header_style)
            worksheet.write(1, 2, interval.split("to")[1], header_style)

            if self.resolution == "60m":
                sqkm = 0.0036
            else:  # 30m resolution
                sqkm = 0.0009
            student85 = self.ecoData[4]

            statindex = len(dheader)
            for index, colheader in enumerate(dheader):
                worksheet.write(1, index+3, colheader.replace(".","_"), header_style)
            for index, colheader in enumerate(sheader):
                worksheet.write(1, index+3 + statindex, colheader.replace(".","_"), header_style)
                
            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(2)
            worksheet.set_remove_splits(True)

            sums = numpy.sum(dnumpyrows, axis=0)
            statsums = numpy.sum(snumpyrows, axis=0)
            drows = dnumpyrows.tolist()
            srows = snumpyrows.tolist()

            # Write data rows
            for rowidx, row in enumerate(drows):
                worksheet.write(rowidx+2, 0, rowidx+1) #add transition id to first column
                worksheet.write(rowidx+2, 1, self.ctrans[rowidx][ 0])   #write from class
                worksheet.write(rowidx+2, 2, self.ctrans[rowidx][ 1])   #write to class
                for colindex, col in enumerate(row):
                    worksheet.write(rowidx+2, colindex+3, col)
                
            # Write stat rows
            for rowidx, row in enumerate(srows):
                for colindex, col in enumerate(row):
                    worksheet.write(rowidx+2, colindex+3+statindex, col, plain_2dig_style)

            #Write estimated change, std. error, and 85% CI in sq.km. after statistics columns
            start = len(dheader) + len(sheader) + 3
            worksheet.write(1, start,"EST.CHANGE(sqkm)", header_style)
            worksheet.write(1, start+1,"STD.ERROR(sqkm)", header_style)
            worksheet.write(1, start+2,"85% CI +-(sqkm)", header_style)
            for rowidx, row in enumerate(srows):
                worksheet.write(rowidx+2, start,
                                row[TrendsNames.statisticsNames.index("EstChange")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+1,
                                row[TrendsNames.statisticsNames.index("StdError")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+2,
                                row[TrendsNames.statisticsNames.index("StdError")]*student85*sqkm, short_style)

            worksheet.write(len(self.ctrans)+2, 1,"TOTALS", header_style)
            for colindex, col in enumerate(sums):
                worksheet.write(len(self.ctrans)+2, colindex+3, col, bold_data_style)
            for colindex, col in enumerate(statsums[:3]):
                worksheet.write(len(self.ctrans)+2, colindex+3+statindex, col, bold_2dig_style)

            # Write the change totals below all data and stats cols
            change_drows = self.ecoHolder.allChange[interval]['conversion'][0].tolist()
            change_srows = self.ecoHolder.allChange[interval]['conversion'][1].tolist()
            worksheet.write(len(self.ctrans)+4, 1,"ALL CHANGE", header_style)
            for colindex, col in enumerate(change_drows[0]):
                worksheet.write(len(self.ctrans)+4, colindex+3, col, bold_data_style)
            for colindex, col in enumerate(change_srows[0]):
                worksheet.write(len(self.ctrans)+4, colindex+3+statindex, col, bold_2dig_style)

            worksheet.write(len(self.ctrans)+4, start,
                                change_srows[0][TrendsNames.statisticsNames.index("EstChange")]*sqkm, short_style)
            worksheet.write(len(self.ctrans)+4, start+1,
                                change_srows[0][TrendsNames.statisticsNames.index("StdError")]*sqkm, short_style)
            worksheet.write(len(self.ctrans)+4, start+2,
                                change_srows[0][TrendsNames.statisticsNames.index("StdError")]*student85*sqkm, short_style)

            #Pick up the change, stderror, and class transition in order to create common
            # conversions page later.
            self.ranking[ interval ] = []
            for index, row in enumerate(srows):
                if (index in self.chngList) and (row[TrendsNames.statisticsNames.index("EstChange")] > 0.0):
                    self.ranking[ interval ].append((row[TrendsNames.statisticsNames.index("EstChange")],
                                                row[TrendsNames.statisticsNames.index("StdError")],
                                                index))

            return worksheet

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def add_glgn_entries_to_page( self, gp, worksheet, interval, headerlen, glgn ):
        try:
            rowoffset = len(self.ctrans) + 9
            for tab in TrendsNames.glgnTabTypes:
                #Get data and stat tables for this eco and interval
                drows = glgn[tab][0].tolist()
                srows = glgn[tab][1].tolist()
                statindex = headerlen

                if self.resolution == "60m":
                    sqkm = 0.0036
                else:  # 30m resolution
                    sqkm = 0.0009
                student85 = self.ecoData[4]
                
                # Write data rows
                for rowidx, row in enumerate(drows):
                    if rowidx == 0:
                        worksheet.write(rowidx+rowoffset, 0, tab, header_style)   #write table name
                    worksheet.write(rowidx+rowoffset, 1, self.types[rowidx])   #write 'to' class
                    for colindex, col in enumerate(row):
                        worksheet.write(rowidx+rowoffset, colindex+3, col)

                # Write stat rows
                for rowidx, row in enumerate(srows):
                    for colindex, col in enumerate(row):
                        worksheet.write(rowidx+rowoffset, colindex+3+statindex, col, plain_2dig_style)

                start = headerlen + len(srows[0]) + 3
                for rowidx, row in enumerate(srows):
                    worksheet.write(rowidx+rowoffset, start,
                                    row[TrendsNames.statisticsNames.index("EstChange")]*sqkm, short_style)
                    worksheet.write(rowidx+rowoffset, start+1,
                                    row[TrendsNames.statisticsNames.index("StdError")]*sqkm, short_style)
                    worksheet.write(rowidx+rowoffset, start+2,
                                    row[TrendsNames.statisticsNames.index("StdError")]*student85*sqkm, short_style)
                #Now shift row offset down for next type of data (glgn)
                rowoffset += len(self.types) + 1

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
            
    def build_aggregate_interval_page( self, gp, dheader, dnumpyrows, sheader, snumpyrows, interval, source ):
        try:
            if source == 'gross':
                label = 'Cumul'
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( label+interval )

            #Set up header row, freeze panes
            worksheet.write(1, 1, interval.split("to")[0], header_style)
            worksheet.write(1, 2, interval.split("to")[1], header_style)

            statindex = len(dheader)
            for index, colheader in enumerate(dheader):
                worksheet.write(1, index+3, colheader.replace(".","_"), header_style)
            for index, colheader in enumerate(sheader):
                worksheet.write(1, index+3 + statindex, colheader.replace(".","_"), header_style)
                
            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(2)
            worksheet.set_remove_splits(True)

            if self.resolution == "60m":
                sqkm = 0.0036
            else:  # 30m resolution
                sqkm = 0.0009
            student85 = self.ecoData[4]

            self.totalPix[source] = self.find_total_estimated_pixels( dnumpyrows, self.ecoData[1], self.ecoData[2] )
            sums = numpy.sum(dnumpyrows, axis=0)
            statsums = numpy.sum(snumpyrows, axis=0)
            drows = dnumpyrows.tolist()
            srows = snumpyrows.tolist()

            # Write data rows
            for rowidx, row in enumerate(drows):
                worksheet.write(rowidx+2, 0, rowidx+1) #add transition id to first column
                worksheet.write(rowidx+2, 1, self.ctrans[rowidx][ 0])   #write from class
                worksheet.write(rowidx+2, 2, self.ctrans[rowidx][ 1])   #write to class
                for colindex, col in enumerate(row):
                    worksheet.write(rowidx+2, colindex+3, col)
                
            # Write stat rows
            for rowidx, row in enumerate(srows):
                for colindex, col in enumerate(row):
                    worksheet.write(rowidx+2, colindex+3+statindex, col, plain_2dig_style)

            #Write estimated change, std. error, and 85% CI in sq.km. after statistics columns
            start = len(dheader) + len(sheader) + 3
            worksheet.write(1, start,"EST.CHANGE(sqkm)", header_style)
            worksheet.write(1, start+1,"STD.ERROR(sqkm)", header_style)
            worksheet.write(1, start+2,"85% CI +-(sqkm)", header_style)
            for rowidx, row in enumerate(srows):
                worksheet.write(rowidx+2, start,
                                row[TrendsNames.statisticsNames.index("EstChange")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+1,
                                row[TrendsNames.statisticsNames.index("StdError")]*sqkm, short_style)
                worksheet.write(rowidx+2, start+2,
                                row[TrendsNames.statisticsNames.index("StdError")]*student85*sqkm, short_style)

            worksheet.write(len(self.ctrans)+2, 1,"TOTALS", header_style)
            for colindex, col in enumerate(sums):
                worksheet.write(len(self.ctrans)+2, colindex+3, col, bold_data_style)
            for colindex, col in enumerate(statsums[:3]):
                worksheet.write(len(self.ctrans)+2, colindex+3+statindex, col, bold_2dig_style)

            # Write the change totals below all data and stats cols
            change_drows = self.ecoHolder.allChange[interval]['addgross'][0].tolist()
            change_srows = self.ecoHolder.allChange[interval]['addgross'][1].tolist()
            worksheet.write(len(self.ctrans)+4, 1,"ALL CHANGE", header_style)
            for colindex, col in enumerate(change_drows[0]):
                worksheet.write(len(self.ctrans)+4, colindex+3, col, bold_data_style)
            for colindex, col in enumerate(change_srows[0]):
                worksheet.write(len(self.ctrans)+4, colindex+3+statindex, col, bold_2dig_style)

            worksheet.write(len(self.ctrans)+4, start,
                                change_srows[0][TrendsNames.statisticsNames.index("EstChange")]*sqkm, short_style)
            worksheet.write(len(self.ctrans)+4, start+1,
                                change_srows[0][TrendsNames.statisticsNames.index("StdError")]*sqkm, short_style)
            worksheet.write(len(self.ctrans)+4, start+2,
                                change_srows[0][TrendsNames.statisticsNames.index("StdError")]*student85*sqkm, short_style)

            #Pick up the change, stderror, and class transition in order to create common
            # conversions page later.
            self.ranking[ label+interval ] = []
            for index, row in enumerate(srows):
                if (index in self.chngList) and (row[TrendsNames.statisticsNames.index("EstChange")] > 0.0):
                    self.ranking[ label+interval ].append((row[TrendsNames.statisticsNames.index("EstChange")],
                                                row[TrendsNames.statisticsNames.index("StdError")],
                                                index))
            return worksheet
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
            
            LCoffset = len(self.years) + 3
            for ptr, year in enumerate(self.years):
                dheader = self.dheader
                dnumpyrows = self.ecoHolder.ecoComp[year][0]
                sheader = self.sheader
                snumpyrows = self.ecoHolder.ecoComp[year][1]

                if ptr == 0:
                    #Put on the header row
                    dataindex = len(dheader)
                    for index, colheader in enumerate(dheader):
                        worksheet.write(1, index+2, colheader.replace(".","_"), header_style)
                    for index, colheader in enumerate(sheader):
                        colname = colheader
                        if colname == "EstChange(pix)":
                            colname = "EstComp(pix)"
                        if colname == "ChgPercent(%)":
                            colname = "CompPercent(%)"
                        worksheet.write(1, index+2 + dataindex, colname.replace(".","_"), header_style)
                
                    worksheet.set_panes_frozen(True)
                    worksheet.set_horz_split_pos(2)
                    worksheet.set_remove_splits(True)

                statindex = len(dheader)        #find length of data line on spreadsheet
                drows = dnumpyrows.tolist()
                srows = snumpyrows.tolist()

                #Now add the year, the LC type, and the data and stats
                # Write data rows
                for rowidx, row in enumerate(drows):
                    rowptr = (rowidx*LCoffset)+2+ptr
                    worksheet.write(rowptr, 0, year, header_style)                #write year
                    worksheet.write(rowptr, 1, self.types[rowidx], header_style)       #write class
                    for colindex, col in enumerate(row):
                        worksheet.write(rowptr, colindex+2, col)

                # Write stat rows
                for rowidx, row in enumerate(srows):
                    rowptr = (rowidx*LCoffset)+2+ptr
                    for colindex, col in enumerate(row):
                        worksheet.write(rowptr, colindex+2+statindex, col, plain_2dig_style)
        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_yearlysummary_page( self, gp ):
        try:
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "Yearly Summary" )
            lcs = TrendsNames.LCshort
            student85 = self.ecoData[4]
            special_style = xlwt.easyxf('font: height 200, bold on; align: horiz center')
            
            #Create an array for each LC type, then step through
            # each year and add its data to the LC
            samples = self.ecoData[2]
            lcstats = {}
            lcstats['mean'] = [0.0 for x in range(len(self.types))]
            lcstats['student'] = [0.0 for x in range(len(self.types))]
            lcstats['wilcox'] = [0.0 for x in range(len(self.types))]
            lcstats['Ncount'] = [0 for x in range(len(self.types))]
            for lc in range(len(self.types)):
                #set up data structure to hold calculations.  The data
                # array is a numpy array with a column for each sample block
                # and a row for each composition year.
                lcdata = numpy.zeros((len(self.years), samples), int)

                #build the data array for the current land cover type
                for yearctr, year in enumerate(self.years):
                    lcdata[ yearctr,: ] = self.ecoHolder.ecoComp[year][0][ lc,: ]

                #get the stats of slope mean, Wilcoxon N pairs, student's T p-value,
                # and Wilcoxon p-value
                lcstats['mean'][lc],lcstats['Ncount'][lc],lcstats['student'][lc],lcstats['wilcox'][lc]= \
                                student_wilcoxon.studentWilcoxon( gp, lcdata, self.years )

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
                        self.ecoHolder.ecoComp[year][1][col,TrendsNames.statisticsNames.index('ChgPercent')],
                                    plain_2dig_style)

            rowoffset = len(self.years)+3
            first = self.years[0]
            last = self.years[-1]
            netdif = [0.0 for x in range(len(self.types))]
            #calculate the first year / last year difference for each lc type
            worksheet.write(rowoffset, 1, str(first)+"-"+str(last), bold_italic_style)
            for col in range(len(self.types)):
                netdif[col] = self.ecoHolder.ecoComp[last][1][col,TrendsNames.statisticsNames.index('ChgPercent')] - \
                      self.ecoHolder.ecoComp[first][1][col,TrendsNames.statisticsNames.index('ChgPercent')]
                worksheet.write(rowoffset, col+2,netdif[col],italic_2dig_style)

            rowoffset = rowoffset+2
            worksheet.write(rowoffset,0, "Linear", header_style)
            worksheet.write(rowoffset,1, "Trend", bold_style)
            for colindex in range(len(self.types)):
                if lcstats['mean'][colindex] >= 0.0:
                    trendsym = '+'
                else:
                    trendsym = '-'
                worksheet.write(rowoffset, colindex+2, trendsym, special_style)
            
            worksheet.write(rowoffset+1,1, "P,t-test", bold_style)
            for colindex in range(len(self.types)):
                worksheet.write(rowoffset+1, colindex+2,lcstats['student'][colindex],stat_style)
            
            worksheet.write(rowoffset+2,1, "P,Wilcoxon", bold_style)
            for colindex in range(len(self.types)):
                worksheet.write(rowoffset+2, colindex+2,lcstats['wilcox'][colindex],stat_style)
            
            worksheet.write(rowoffset+3,1, "N(Wilcoxon Pairs)", bold_style)
            for colindex in range(len(self.types)):
                worksheet.write(rowoffset+3, colindex+2,lcstats['Ncount'][colindex],short_style)

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
                        self.ecoHolder.ecoComp[year][1][index,TrendsNames.statisticsNames.index('ChgPercent')],
                                    plain_2dig_style)
                    worksheet.write(index+2, startcol+2+col*3,
                        self.ecoHolder.ecoComp[year][1][index,TrendsNames.statisticsNames.index('PerStdErr')],
                                    plain_2dig_style)
                    worksheet.write(index+2, startcol+3+col*3,
                        self.ecoHolder.ecoComp[year][1][index,TrendsNames.statisticsNames.index('PerStdErr')]*student85,
                                    plain_2dig_style)

            #Notes from the master spreadsheet
            worksheet.write( trendsTableLen, 1,"See Notes", plain_italic_style)
            worksheet.write( trendsTableLen+1, 1,"far right", plain_italic_style)
            rowoffset = 1
            col = len(self.types)+6 + len(self.years)*3
            worksheet.write(rowoffset,col+1,"Notes:",plain_italic_style)
            worksheet.write(rowoffset+1,col,1,plain_italic_style)
            worksheet.write(rowoffset+1,col+1,
                    "Tabled values are P-values testing for statistical significance of the trend.",
                            plain_italic_style)
            worksheet.write(rowoffset+2,col+1,
                    "P-values<0.05 indicate the trend is statistically significantly different from zero at a significance level of alpha=0.05.",
                            plain_italic_style)
            worksheet.write(rowoffset+3,col+1,"P-values<0.10 indicate significance at alpha=0.10.",
                            plain_italic_style)
            worksheet.write(rowoffset+4,col,2,plain_italic_style)
            worksheet.write(rowoffset+4,col+1,
                    "The t-test is a parametric test of the significance of the linear trend.",
                            plain_italic_style)
            worksheet.write(rowoffset+5,col,3,plain_italic_style)
            worksheet.write(rowoffset+5,col+1,
                    "The Wilcoxon test is a non-parametric analog of the t-test. When in doubt, the Wilcoxon test results should be used",
                            plain_italic_style)
            worksheet.write(rowoffset+6,col+1,
                    "because it requires less stringent distributional assumptions than the parametric test.",
                            plain_italic_style)
            worksheet.write(rowoffset+7,col,4,plain_italic_style)
            worksheet.write(rowoffset+7,col+1,
                    "If fewer than 10 pairs of untied observations are present for the Wilcoxon test (i.e. N(Wilcoxon Pairs)<10),",
                            plain_italic_style)
            worksheet.write(rowoffset+8,col+1,
                    "neither test should be considered reliable.",
                            plain_italic_style)

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
                            self.ecoHolder.ecoGlgn[interval][tab][1][col,TrendsNames.statisticsNames.index('ChgPercent')],
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
                            self.ecoHolder.ecoGlgn[interval][tab][1][col,TrendsNames.statisticsNames.index('ChgPercent')]/float(dif),
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

    def build_comconversions_page( self, gp, interval, source ):
        try:
            if source == 'standardconversion':
                label = ""
            elif source == 'gross':
                label = 'Cumul'

            rankinterval = label+interval
            tpix = self.totalPix[source]
            
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "CommonConv " + rankinterval )

            #Set up header row, freeze panes
            worksheet.write(0, 1, "Most Common Conversions", header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(2)
            worksheet.set_remove_splits(True)

            if self.resolution == "60m":
                sqkm = 0.0036
            else:  # 30m resolution
                sqkm = 0.0009

            if self.reportType == "Summary":
                student85 = self.params[4]
            else:
                student85 = self.ecoData[4]
                
            headers = ['Rank','From','To','Chng(pix)','Stderr(pix)','Chng(sqkm)',
                       'Stderr(sqkm)','85% CI +-(sqkm)','Chng(%eco)','Stderr(%eco)']

            # Write common conversions and values
            self.ranking[ rankinterval ].sort(reverse=True)
            for idx, name in enumerate(headers):
                worksheet.write(1,idx, name, header_style)
            for rowidx, row in enumerate(self.ranking[rankinterval]):
                worksheet.write(rowidx+2, 0, rowidx+1)
                worksheet.write(rowidx+2, 1, self.ctrans[(self.ranking[rankinterval][rowidx][2])][ 0])   #write from class
                worksheet.write(rowidx+2, 2, self.ctrans[(self.ranking[rankinterval][rowidx][2])][ 1])   #write to class
                worksheet.write(rowidx+2, 3, self.ranking[rankinterval][rowidx][0], short_style)
                worksheet.write(rowidx+2, 4, self.ranking[rankinterval][rowidx][1], short_style)
                worksheet.write(rowidx+2, 5, (self.ranking[rankinterval][rowidx][0]*sqkm), short_style)
                worksheet.write(rowidx+2, 6, (self.ranking[rankinterval][rowidx][1]*sqkm), short_style)
                worksheet.write(rowidx+2, 7, ((self.ranking[rankinterval][rowidx][1]*student85)*sqkm), short_style)
                worksheet.write(rowidx+2, 8, ((self.ranking[rankinterval][rowidx][0]/tpix)*100.0), plain_2dig_style)
                worksheet.write(rowidx+2, 9, ((self.ranking[rankinterval][rowidx][1]/tpix)*100.0), plain_2dig_style)

            worksheet.write( 2, 11, "All conversions with nonzero estimated change values", plain_italic_style)
            worksheet.write( 3, 11, "are shown in the table.  Values are rounded to the nearest", plain_italic_style)
            worksheet.write( 4, 11, "pixel/sq.km, so small fractions of sq.km are shown = 0.", plain_italic_style)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise

    def build_multichange_page( self, gp, interval ):
        try:
            #Get data and stat tables for this eco
            xchg = TrendsNames.MultiMap[ interval ]
            dheader = self.dheader
            dnumpyrows = self.ecoHolder.ecoMulti[interval][0][:xchg,:]
            sheader = self.sheader
            snumpyrows = self.ecoHolder.ecoMulti[interval][1][:xchg,:]
            student85 = self.ecoData[4]

            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "footprint" + interval )
            title1 = ["No Change","1 date"] + [str(x)+" dates" for x in range(2,xchg)]
            title2 = ["Block"] + [str(x) for x in range(xchg)] + ["Total pixels(pix)","% Change(%)","All Change(pix)"]
            title3 = ["NO CHANGES","1 CHANGE"] + [str(x)+" CHANGES" for x in range(2,xchg)]
            title4 = ("FOOTPRINT","  ","% of ECO(%)","85%+/-(%)","LOWER CI(%)","UPPER CI(%)","STD. ERROR(%)","REL. ERROR(%)")
            statindex = xchg + 5

            drows = dnumpyrows.tolist()
            srows = snumpyrows.tolist()
            sums = numpy.sum(dnumpyrows, axis=0)
            xsums = numpy.sum(dnumpyrows, axis=1)
            onlychg = numpy.sum(xsums[1:])
            totalchg = numpy.sum(xsums)
            percentchg = []
            for x in xsums:
                percentchg.append(float(x)/float(totalchg)*100.0)
            statsums = numpy.sum(snumpyrows, axis=0)
            datalen = self.ecoData[2] #number sample blocks, same as len(drows)
            
            #Set up header rows, freeze panes
            for index, colheader in enumerate(title1):
                worksheet.write(0, index+1, colheader, header_style)
            for index, colheader in enumerate(title2):
                worksheet.write(1, index, colheader, header_style)
            
            for index, colheader in enumerate(dheader):
                worksheet.write(index+2, 0, colheader.replace(".","_"), header_style)
            for index, colheader in enumerate(sheader):
                worksheet.write(0, index+statindex+1, colheader.replace(".","_"), header_style)

            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(1)
            worksheet.set_remove_splits(True)

            # Write data rows
            for rowidx, row in enumerate(drows):
                for colindex, col in enumerate(row):
                    worksheet.write(colindex+2, rowidx+1, col)

            # Write stat rows
            for rowidx, row in enumerate(srows):
                if rowidx == 0:
                    line = 3 + 2*(len(srows)-1)
                else:
                    line = 3 + 2*(rowidx-1)
                worksheet.write(line, statindex, title3[rowidx])
                for colindex, col in enumerate(row):
                    worksheet.write(line, colindex+1+statindex, col, plain_2dig_style)

            # Write the column totals 
            for colindex, col in enumerate(sums):
                worksheet.write(colindex+2, len(drows)+1, col, bold_data_style)
            worksheet.write(datalen+3,0,"Total Change(pix)",header_style)
            worksheet.write(datalen+4,0,"% Change(%)",header_style)
            for colindex, col in enumerate(xsums):
                worksheet.write(datalen+3, colindex+1, col, bold_data_style)
            worksheet.write(datalen+3, len(xsums)+1, totalchg, bold_data_style)
            worksheet.write(datalen+3, len(xsums)+3, onlychg, bold_data_style)
            worksheet.write(datalen+3, len(xsums)+2, float(onlychg)/float(totalchg)*100.0, bold_2dig_style)
            for colindex, col in enumerate(percentchg):
                worksheet.write(datalen+4, colindex+1, col, bold_2dig_style)
            worksheet.write(datalen+4, len(xsums)+1, numpy.sum(percentchg), bold_2dig_style)
            worksheet.write(datalen+4, len(xsums)+2, numpy.sum(percentchg[1:]), bold_2dig_style)

            # Write the change totals below all data and stats cols
            change_drows = self.ecoHolder.allChange[interval]['multichange'][0].tolist()
            change_srows = self.ecoHolder.allChange[interval]['multichange'][1].tolist()
            for colindex, col in enumerate(change_drows[0]):
                worksheet.write(colindex+2, len(drows)+3, col, bold_data_style)
                worksheet.write(colindex+2,len(drows)+2,(float(col)/float(sums[colindex])*100.0), bold_2dig_style)
            worksheet.write(1, statindex, "ALL CHANGE")
            for colindex, col in enumerate(change_srows[0]):
                worksheet.write(1, colindex+1+statindex, col, plain_2dig_style)

            # Create summary table
            sumindex = (TrendsNames.statisticsNames.index('ChgPercent'),
                        TrendsNames.statisticsNames.index('PerStdErr'),
                        TrendsNames.statisticsNames.index('Lo85Conf'),
                        TrendsNames.statisticsNames.index('Hi85Conf'),
                        TrendsNames.statisticsNames.index('PerStdErr'),
                        TrendsNames.statisticsNames.index('RelError'))
            startrow = len(drows)*2 + 6
            startcol = len(drows)+6
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

    def build_allchange_page( self, gp, dheader, sheader, numpychange ):
        try:
            #add a worksheet to the workbook for this interval
            worksheet = self.workbook.add_sheet( "Per_Period_Change" )
            student85 = self.ecoData[4]

            #Set up header row, freeze panes
            worksheet.write(0, 0,"Estimated Change",header_style)
            worksheet.write(0, 10, "Total Pix Changed", header_style)
            worksheet.write(1, 2, "Change Est.(%)", header_style)
            worksheet.write(1, 3, "+/-(%)", header_style)
            worksheet.write(1, 4, "85%Lo(%)", header_style)
            worksheet.write(1, 5, "85%Hi(%)", header_style)
            worksheet.write(1, 6, "Std.Err.(%)", header_style)
            worksheet.write(1, 7, "Rel.Err.(%)", header_style)
            worksheet.write(1, 8, "Avg.Annual(%)", header_style)
            for index, colheader in enumerate(dheader):
                worksheet.write(1, index+10, colheader.replace(".","_"), header_style)

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

            totaldif = 0
            worksheet.write(2, 0, "Conversion", header_style)
            # Write overall change intervals and values
            for rowidx, interval in enumerate(self.intervals):
                temp = interval.split("to")
                dif = int(temp[1]) - int(temp[0])
                change_drows = self.ecoHolder.allChange[interval]['conversion'][0].tolist()
                change_srows = self.ecoHolder.allChange[interval]['conversion'][1].tolist()
                worksheet.write(rowidx+2, 1,interval.replace('to','-'), header_style)                
                worksheet.write(lowertable+rowidx+3, 1,interval.replace('to','-'), header_style)                
                worksheet.write(rowidx+2, 2,
                            change_srows[0][TrendsNames.statisticsNames.index('ChgPercent')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 2,
                            change_srows[0][TrendsNames.statisticsNames.index('ChgPercent')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 3,
                            change_srows[0][TrendsNames.statisticsNames.index('PerStdErr')]*student85,
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 3,
                            change_srows[0][TrendsNames.statisticsNames.index('PerStdErr')]*student85/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 4,
                            change_srows[0][TrendsNames.statisticsNames.index('Lo85Conf')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 4,
                            change_srows[0][TrendsNames.statisticsNames.index('Lo85Conf')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 5,
                            change_srows[0][TrendsNames.statisticsNames.index('Hi85Conf')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 5,
                            change_srows[0][TrendsNames.statisticsNames.index('Hi85Conf')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 6,
                            change_srows[0][TrendsNames.statisticsNames.index('PerStdErr')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 6,
                            change_srows[0][TrendsNames.statisticsNames.index('PerStdErr')]/float(dif),
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 7,
                            change_srows[0][TrendsNames.statisticsNames.index('RelError')],
                                    plain_2dig_style)
                worksheet.write(lowertable+rowidx+3, 7,
                            change_srows[0][TrendsNames.statisticsNames.index('RelError')],
                                    plain_2dig_style)
                worksheet.write(rowidx+2, 8,
                            change_srows[0][TrendsNames.statisticsNames.index('ChgPercent')]/float(dif),
                                    plain_2dig_style)
                #on this page, write the data after the abbreviated stats
                for colindex, col in enumerate(change_drows[0]):
                    worksheet.write(rowidx+2, colindex+10, col)

            worksheet.write(len(self.intervals)+3, 0, "Cumulative", header_style)
            # Write overall change intervals and values
            for rowidx, interval in enumerate(self.cumulativeintervals):
                temp = interval.split("to")
                dif = int(temp[1]) - int(temp[0])
                avgdif = float(dif)/float(TrendsNames.CumulativeMap[interval]) #for avg annual, divide by avg interval length
                change_drows = self.ecoHolder.allChange[interval]['addgross'][0].tolist()
                change_srows = self.ecoHolder.allChange[interval]['addgross'][1].tolist()
                nextrow = rowidx+len(self.intervals)+3
                worksheet.write(nextrow, 1,interval.replace('to','-'), header_style)
                worksheet.write(nextrow, 2,
                            change_srows[0][TrendsNames.statisticsNames.index('ChgPercent')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 3,
                            change_srows[0][TrendsNames.statisticsNames.index('PerStdErr')]*student85,
                                    plain_2dig_style)
                worksheet.write(nextrow, 4,
                            change_srows[0][TrendsNames.statisticsNames.index('Lo85Conf')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 5,
                            change_srows[0][TrendsNames.statisticsNames.index('Hi85Conf')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 6,
                            change_srows[0][TrendsNames.statisticsNames.index('PerStdErr')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 7,
                            change_srows[0][TrendsNames.statisticsNames.index('RelError')],
                                    plain_2dig_style)
                worksheet.write(nextrow, 8,
                            change_srows[0][TrendsNames.statisticsNames.index('ChgPercent')]/avgdif,
                                    plain_2dig_style)
                for colindex, col in enumerate(change_drows[0]):
                    worksheet.write(nextrow, colindex+10, col)

        except Exception:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
            gp.AddMessage(pymsg)
            raise
