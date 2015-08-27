# File loadChangeImages.py
#
#   Take the Trends land cover change images generated with Imagine
#   and add the file locations into the Trends geodatabase changeImages
#   table.  In addition, extract relevant metadata from the filename
#   and enter into the changeImages table along with the filename.
#   Filename should contain full pathname for retrieval by a
#   geoprocessing tool.
#
# Written:         July 2010
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import arcgisscripting, os
import sys, traceback
from stat import *
from LULCTrends.trendutil import TrendsNames

def walktree(top, callback, fileList):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''
    try:
        for f in os.listdir(top):
            pathname = os.path.join(top, f)
            mode = os.stat(pathname).st_mode
            if S_ISDIR(mode):
                # It's a directory, recurse into it
                walktree(pathname, callback, fileList)
            elif S_ISREG(mode):
                # It's a file, call the callback function
                if pathname.split('.')[-1] == "img":
                    callback(pathname, fileList)
            else:
                # Unknown file type, print a message
                print 'Skipping %s' % pathname
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print pymsg
        raise

def splitTheFileName (fileName):
    #split the filename into metadata parts
    #sample filename looks like: 'samp07_0426_1992to2000_change_60m.img'
    #For mosaic blocks (block + slivers), a sample name looks like
    #       'samp83_0388_mosaic_1992to2000_change_60m.img'
    
    try:
        nameList = fileName.split( '_' )
        #Pull out the various pieces and return
        ecoregion = int( nameList[0][4:6] )
        blkLabel = int( nameList[1] )
        sampleBlkID = nameList[0][4:6].lstrip('0') + '-' + nameList[1]
        changePeriod = nameList[2]
        resolution = nameList[4][0:3]
            
        return ecoregion, blkLabel, sampleBlkID, changePeriod, resolution
    except:
        print("Unable to parse filename " + fileName)
        raise

def getFileList( filename, fileList ):
    try:
        fileList.append( filename )
    except Exception:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        print pymsg
        raise

try:
    #Create the geoprocessor object
    gp = arcgisscripting.create(9.3)
    topPath = TrendsNames.changeImageFolders

    changeLoc =  TrendsNames.dbLocation + "ChangeImage"
    gp.DeleteRows_management( changeLoc )
    print changeLoc

    allFiles = []
    walktree(topPath, getFileList, allFiles)
    
    changeRows = gp.InsertCursor( changeLoc )
    changeRow = changeRows.Next()

    for raster in allFiles:
        if raster.count('mos') or raster.count('sliver'):
            print("Found sliver or mosaic file - skipping over " + raster)
            continue
        #Split the raster filename up and extract its metadata
        ecoregion, blkLabel, sampleBlkID, changePeriod, resolution = splitTheFileName( os.path.basename(raster) )
        changeRow = changeRows.NewRow()
        changeRow.EcoLevel3ID = ecoregion
        changeRow.BlkLabel = blkLabel
        changeRow.SampleBlkID = sampleBlkID
        changeRow.ChangePeriod = changePeriod
        changeRow.Resolution = resolution
        changeRow.ImageLocation = raster.replace('\\','/')

        #Insert the new row into the table
        changeRows.InsertRow( changeRow )
        
except arcgisscripting.ExecuteError:
    # Get the geoprocessing error messages
    msgs = gp.GetMessage(0)
    msgs += gp.GetMessages(2)
    gp.AddError(msgs)
    print msgs
    
except Exception:
    #print out the system error traceback
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
    gp.AddError(pymsg)
    print pymsg
    
finally:
    #delete the row and rows objects to free up any schema lock on the database
    if 'changeRow' in dir():
        del changeRow
    if 'changeRows' in dir():
        del changeRows
    gp = None
