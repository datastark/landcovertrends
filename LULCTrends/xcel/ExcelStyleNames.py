# ExcelStyleNames.py
#
# contains the definition of the printing styles
#  used by the excel generator tool.
#
# Written:         Mar 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import xlwt

header_style = xlwt.easyxf("font: bold on; align: horiz center")
bold_style = xlwt.easyxf("font: bold on")
bold_italic_style = xlwt.easyxf("font: bold on; font: italic on; align: horiz center")
plain_italic_style = xlwt.easyxf("font: italic on")
stat_style = xlwt.easyxf(num_format_str="#0.0000")
short_style = xlwt.easyxf(num_format_str="#0")
bold_stat_style = xlwt.easyxf("font: bold on", num_format_str="#0.0000")
bold_data_style = xlwt.easyxf("font: bold on")
bold_2dig_style = xlwt.easyxf("font: bold on", num_format_str="#0.00")
plain_2dig_style =xlwt.easyxf(num_format_str="#0.00")
italic_2dig_style = xlwt.easyxf("font: italic on", num_format_str="#0.00")
blue_header_style = xlwt.easyxf("font: bold on; align: horiz center; pattern: pattern solid, fore_color pale_blue")
