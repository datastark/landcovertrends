# sendtoserver.py
#
# Access server geoprocessing tool to accept email information.
# This geoprocessing tool will send an email acknowledging receipt.
#
# Written:         Nov 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import os,sys,traceback
import arcpy, zipfile

def get_uploaded_folder(f, infolder):
    try:
        newname = infolder + "/" + f.name
        dest = open(newname, 'wb+')
        for chunk in f.chunks():
            dest.write(chunk)
        dest.close()
        return newname
    except Exception:
        print(traceback.format_exc())

def extract_shp( zipit, path ):
    try:
        os.chdir( path )

        #Get the names of the contents and extract all to
        # current directory
        shapes = zipit.namelist()
        zipit.extractall()
        zipit.close()

        #find the basename of each file since a shapefile
        # is made up of several files
        unique = []
        for name in shapes:
            n = name.split(".")
            if n[0] not in unique:
                unique.append(n[0])

        #test each basename for a .shp file to make a list
        #that only contains shapefile basenames
        for each in unique:
            shp = path + each + '.shp'
            if not arcpy.Exists( shp ):
                 unique.remove( each )
        return unique

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
    except Exception:
        print(traceback.format_exc())
        
def sendfile_for_boundary(recipient, f):
    try:
        path = MEDIA_ROOT
        arcpy.ImportToolbox("http://REMOVED/arcgis/services;CustomShapefile", "CustomShapefile")

        #get the uploaded file
        zipfold = get_uploaded_folder( f, path )
        
        if not zipfile.is_zipfile( zipfold ):
            return "Folder isn't a valid zip folder"
        
        #unzip the folder and extract the shapefile
        zipit = zipfile.ZipFile( zipfold,'r' )
        filelist = extract_shp( zipit, path )
        if filelist:   #are there any valid shapefile names?
            for name in filelist:
                # Run the server tool with input parameters set 
                # This is an asynchronous tool so execution exits after tool is called
                boundary = arcpy.GetParameterValue("CustomShapefile", 0)
                boundary.load( path + name )
                result = arcpy.CreateCustomShapefile_CustomShapefile(recipient, boundary)
        else:
            return "No valid shapefile names found in the zip folder"
    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
    except Exception:
        print(traceback.format_exc())

if __name__ == '__main__':
    try:
        arcpy.GetParameterAsText(0, recipient)
        arcpy.GetParameterAsText(1, infolder)
        sendfile_for_boundary(recipient, infolder)
        print "Complete"
    except Exception:
        pass
