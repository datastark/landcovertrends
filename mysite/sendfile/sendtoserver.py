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

dj_media_root = "C:/trends_temp/"

def get_uploaded_folder(f, infolder):
    try:
        newname = os.path.join(infolder,f.name)
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
        logfile = ""
        msg = []
        path = dj_media_root
        logfile = open( os.path.join( path, "zipfiletest.txt"), 'w')
        logfile.write("media root: " + dj_media_root)
        logfile.write("recipient: " + recipient + "\nzip file name: " + f.name)
        arcpy.ImportToolbox("http://REMOVED/arcgis/services;CreateCustomShapefile", "CreateCustomShapefile")

        #get the uploaded file
        zipfold = get_uploaded_folder( f, path )
        logfile.write("\nzip file after read in: " + zipfold)
        
        if not zipfile.is_zipfile( zipfold ):
            logfile.write("\nFolder isn't a valid zip folder")
            msg.append("Folder isn't a valid zip folder")
            return msg
        
        #unzip the folder and extract the shapefile
        zipit = zipfile.ZipFile( zipfold,'r' )
        filelist = extract_shp( zipit, path )
        logfile.write("\nafter zip extract: number of files = " + str(len(filelist)))
        if filelist:   #are there any valid shapefile names?
            for name in filelist:
                folderpth, rootname = os.path.split( name )
                shapename = rootname + ".shp"
                shapeloc = os.path.join( path, name+".shp")
                arcpy.AddMessage("name: " + rootname + " and fullname: " + shapeloc)
                # Run the server tool with input parameters set 
                # This is an asynchronous tool so execution exits after tool is called
                boundary = arcpy.FeatureSet()
                boundary.load( shapeloc )
                result = arcpy.CreateCustomShapefile_CustomShapefile(recipient, boundary, rootname)
            msg.append("Thank you")
            msg.append("Processing is in progress")
            msg.append("You will receive an email when the files are ready")
        else:
            msg.append("No valid shapefile names found in the zip folder")
        return msg
    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
    except Exception:
        print(traceback.format_exc())
    finally:
        if logfile:
            logfile.close()

if __name__ == '__main__':
    try:
        arcpy.GetParameterAsText(0, recipient)
        arcpy.GetParameterAsText(1, infolder)
        sendfile_for_boundary(recipient, infolder)
        print "Complete"
    except Exception:
        pass
