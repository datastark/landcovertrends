#student_wilcoxon.py
#
# Perform Student's T and Wilcoxon Signed Rank tests with R
#
# The expected input data is a numpy array (data) containing the
#  dependent variables and a list (inyears) of the independent variables.
#  The data should be structured such that each column in the data array
#  contains a set of dependent values corresponding to the independent
#  values in the list.

# First, linear regression is performed on each column of the array and
#  the resulting slopes of the regression lines extracted into a separate
#  vector.  This vector is input to R's t.test function to find the
#  p value for the Student T test.  Nonzero values are extracted from the
#  slope vector and this new vector is input to R's Wilcox.test function to
#  find the p value for the Wilcoxon Signed Rank test with only one dataset.
#
# Written:         Aug 2011
# Release date:    Mar 2012
# Written by: Jeanne Jones, USGS, jmjones@usgs.gov
# 
# This software is in the public domain because it contains materials that 
# originally came from the United States Geological Survey, an agency of the 
# United States Department of Interior. For more information, see the official 
# USGS copyright policy at 
# http://www.usgs.gov/visual-id/credit_usgs.html#copyright

#Import modules
import numpy
import traceback
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri

def studentWilcoxon( gp, data, inyears ):
    try:
        #Define the independent variable 'years' in R's workspace
        # to make it easier to access results from the model
        years = robjects.IntVector( inyears )
        globalEnv = robjects.globalEnv
        robjects.r.ls(globalEnv)
        globalEnv["years"] = years

        #Apply R's lm (linear model - linear regression) to each column
        # of the data array.
        getLine = robjects.r('function(x) {lm(x ~ years)}')
        r_apply = robjects.r['apply']
        lines = r_apply( data, MARGIN=2, FUN=getLine )

        #Extract just the slope of the regression lines into another vector
        # and apply the t.test to the slopes.
        r_sapply = robjects.r['sapply']
        r_mean = robjects.r['mean']
        r_ttest = robjects.r['t.test']
        r_wilcox = robjects.r['wilcox.test']
        getSlopes = robjects.r('function(s) {coef(s)["years"]}')
        justSlopes = r_sapply( lines, getSlopes )
        meanval = r_mean( justSlopes )
        slopes_mean = meanval[0]

        if len(justSlopes) > 2:
            resultStudent = r_ttest( justSlopes )
            p_student = resultStudent.r['p.value'][0][0]
        else:
            p_student = -9999.9

        #Extract just the nonzero slopes for the Wilcoxon test and
        # call the test to get the p value.
        nonzeroSlopes = [x for x in justSlopes if x>0.0001 or x<-0.0001]
        if len( nonzeroSlopes ) > 0:
            validSlopes = robjects.FloatVector( nonzeroSlopes )
            resultWilcox = r_wilcox( validSlopes )
            p_wilcox = resultWilcox.r['p.value'][0][0]
        else:
            p_wilcox = -9999.9

        return slopes_mean, len(nonzeroSlopes), p_student, p_wilcox
    except Exception:
        gp.AddMessage(traceback.format_exc())
        raise

if __name__ == '__main__':
    values = "waterEco1.csv"
    try:
        data = numpy.loadtxt( values, dtype= int, delimiter=',')
    except:
        print("Unable to get data from file " + values)
        print(traceback.format_exc())

    years = [1973,1980,1986,1992,2000]
    studentWilcoxon( data, years )
    print "Complete"
