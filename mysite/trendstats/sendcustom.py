# sendcustom.py
#
# Access custom server geoprocessing tool with boundary shapefile
# This geoprocessing tool will send an email upon completion.
#
# Written:         Dec 2011
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

path = "C:/trends_temp/"

def get_uploaded_folder(f, infolder):
    try:
        msg = []
        newname = os.path.join(infolder,f.name)
        dest = open(newname, 'wb+')
        for chunk in f.chunks():
            dest.write(chunk)
        dest.close()
    except Exception:
        msg.append("We have a problem.")
        msg.append(traceback.format_exc())
        
    return newname, msg

def extract_shp( zipit, path ):
    try:
        os.chdir( path )
        msg = []
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

    except arcpy.ExecuteError:
        msg.append("We have a problem.")
        msg.append(arcpy.GetMessages())
    except Exception:
        msg.append("We have a problem.")
        msg.append(traceback.format_exc())

    return unique, msg
        
def sendfile_for_custom(recipient, f):
    try:
        msg = []
        arcpy.ImportToolbox("http://REMOVED/arcgis/services;CreateCustomAnalysis", "Custom")

        #get the uploaded file
        zipfold, errmsg = get_uploaded_folder( f, path )

        if errmsg:
            return errmsg
        
        if not zipfile.is_zipfile( zipfold ):
            msg.append("The zipfile upload failed.")
            msg.append("The folder isn't a valid zip folder.")
            msg.append("Please check that you're sending a compressed folder and try again.")
            return msg
        
        #unzip the folder and extract the shapefile
        zipit = zipfile.ZipFile( zipfold,'r' )
        filelist, errmsg = extract_shp( zipit, path )
        if errmsg:
            return errmsg
        if filelist:   #are there any valid shapefile names?
            for name in filelist:
                folderpth, rootname = os.path.split( name )
                shapename = rootname + ".shp"
                shapeloc = os.path.join( path, name+".shp")
                # Run the server tool with input parameters set 
                # This is an asynchronous tool so execution exits after tool is called
                boundary = arcpy.FeatureSet()
                boundary.load( shapeloc )
                result = arcpy.createCustomAnalysis_Custom(recipient, boundary, rootname)
            msg.append("Thank you.")
            msg.append("Processing is in progress.")
            msg.append("You will receive an email when the files are ready.")
        else:
            msg.append("The zipfile upload failed.")
            msg.append("No valid shapefile names were found in the zip folder.")
            msg.append("Please check the contents of your compressed folder and try again.")
    except arcpy.ExecuteError:
        msg.append("We have a problem.")
        msg.append(arcpy.GetMessages())
    except Exception:
        msg.append("We have a problem.")
        msg.append(traceback.format_exc())

    return msg

if __name__ == '__main__':
    try:
        arcpy.GetParameterAsText(0, recipient)
        arcpy.GetParameterAsText(1, infolder)
        sendfile_for_custom(recipient, infolder)
    except Exception:
        pass
