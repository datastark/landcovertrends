#
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

import re

test = ['name', '1name', '.name', '_name', '-name', 'name1', 'na.me', 'na_me', 'na-me',
        'name@me', 'name$23', 'name#werwerwerw', 'n]23.']

r1 = re.compile(r'^[\d._-]')

#r2 = re.compile(r'[^\w._-]+')
r2 = re.compile(r'[^\w]+')

r12 = re.compile(r'^[a-zA-Z][a-zA-Z0-9._-]*$')

for name in test:
    print name
    print("r1: " + str(re.match(r1,name)))
    print("r2: " + str(re.match(r2,name)))
    print("r12: " + str(re.match(r12,name)))
