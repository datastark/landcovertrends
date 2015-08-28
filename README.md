# landcovertrends

The Land Cover Trends project examined the rates, causes, and consequences of contemporary U.S. land-use/ land-cover change since the early 1970s, using a probability sampling approach to estimate change within the conterminous U.S. The Trends data set contains over 16,000 images, including land cover classification files that were interpreted from Landsat imagery, and change files and multi-change files derived from the land cover files. Statistics on types and amounts of change were also calculated for each of 84 ecoregions, summaries, and custom geographic boundaries and stored in the database. This repository contains four different sections of the Trends software development effort.

##LULCTrends
LULCTrends is a python package containing the analysis processing engine. This package retrieves change image data from the database (not included), calculates statistics, and formats the results as multi-page excel spreadsheets. It accesses the R statistical package inline (with the Python rpy2 package) to perform linear regression and Wilcoxon tests for detecting sigificant trends over time, and uses the Python xlwt package to build excel spreadsheets. Written in Python 2.6, the main is testStudyAreaStats.py in the analysis folder.

##toolbox
toolbox contains the ArcMap (ESRI commercial mapping application) scripts that make up the Trends toolbox and access the analysis code. (ArcGIS 9.3/10.0) Uses the ESRI arcgisscripting python api.

##dbcreate
dbcreate contains the scripts to set up the Trends database tables.

##mysite
mysite contains the code for the Django webpage to access the analysis processing running on ArcGIS Server. This webpage was set up to allow access to the Trends data and statistics from the USGS internal network
