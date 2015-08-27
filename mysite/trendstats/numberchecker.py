#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

def parseNumberList( invalues ):
    
    #expects a string of numerical entries (1,2,4-6) for numbers 
    # between 1 and 84 and returns an error if unable to parse
    entries = str(invalues)
    numlist = []
    outmsg = ""
    if entries:
        temp = entries.split(",")            
        for each in temp:
            entry = each.strip()
            if entry.isdigit():
                numlist.append( int(entry))
            else:
                try:
                    values = entry.split("-")
                    for x in range(int(values[0]), int(values[1])+1):
                        numlist.append( x )
                except Exception:
                    numlist = []
                    outmsg = "Unable to create list of ecoregions. Check for invalid characters."
                    break
    else:
        outmsg = "Couldn't find list of ecoregion numbers."
    if numlist:
        numlist.sort()
        if numlist[0] < 1 or numlist[-1] > 84:
            outmsg = "Invalid ecoregion number.  Numbers must be between 1 and 84."
        elif len(numlist) < 2:
            outmsg = "Ecoregion list must contain at least 2 ecoregions."
    return outmsg
