#!/usr/bin/env python3
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2019                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Retrieving average values from result files							   #
##############################################################################

""" EVOLIFE: Retrieving average values from result files
"""


import sys
import os.path
import glob
import re
import string

def getResult(FileName, NroLine=-1, Numeric=True):
	""" retrieves the last line of a resut file, checks that it only contains
		numbers, and returns it
	"""
	print(FileName)
	LL = open(FileName,'r').readlines()[NroLine]
	if Numeric:
		# checking that there are only numeric values
		NumberList = re.split("\s+",string.strip(LL))
		Test = [int(N) for N in NumberList]
	return LL	

def saveResults(Results, Header, OutputFileName):
	"   appends lines to a global result file "
	F = open(OutputFileName, 'a')
	F.write(Header)
	for R in Results:	F.write(R)
	F.close()
	
	
if __name__ == "__main__":
	##	print __doc__ + '\n'
	if len(sys.argv) < 3:
		print('usage:')
		print('%s <file1.res... fileN.res | file*.res> <outputfile.res>' % os.path.basename(sys.argv[0]))
		print("The last line of each fileI.res is appended to outputfile.res ")
		sys.exit()
	if len(sys.argv) == 3 and sys.argv[1].find('*') >= 0:
		Args = glob.glob(sys.argv[1])
	else:	Args = sys.argv[1:-1]
	OutputFileName = sys.argv[-1]
	Header = open(Args[1]).readline()
	print("Appending those results to %s" % OutputFileName)
	saveResults([getResult(A, 1, Numeric=False) for A in Args], Header, OutputFileName)
	print ('%d files processed' % len(Args))

