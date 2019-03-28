#!/usr/bin/env python3
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2019                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Retrieving average values from result files                               #
##############################################################################

""" EVOLIFE: Retrieving average values from result files
"""


import sys
import os.path
import glob
import re
import string
import operator

def getResult(FileName, ParamName, NroLine=3, extension='.dat', Constraints=()):
	""" retrieves a line from a result file,
		and appends it to the appropriate file
	"""
	F = open(FileName,'r')
	L = F.readlines()
	F.close()
	Parameters = L[0].split()
	Values = L[1].split()
	# Checking the constraint
	if Constraints:
		for Constraint in Constraints:
			(CParam, CVal) = Constraint
			if CVal != int(Values[Parameters.index(CParam)]):
				return
	try:
		RelevantValue = Values[Parameters.index(ParamName)]
	except ValueError:
		print FileName, ParamName, Constraints
		print '\n'.join(L)
		raise ValueError
	if Constraints:
		ResultFileName = ('%s=%d_' * len(Constraints)) % reduce(operator.__add__, Constraints) \
							+ '%s_%d' % (ParamName, int(RelevantValue)) \
							+ '%s' % extension
	else:
		ResultFileName = '%s_%d%s' % (ParamName, int(RelevantValue), extension)
	# print 'Writing on %s' % ResultFileName	
	if not os.path.exists(ResultFileName):
		print '\ncreating %s' % ResultFileName
		G = open(ResultFileName, 'w')
		G.write('%s\t%s\n' % (ParamName, RelevantValue))
	else:
		G = open(ResultFileName, 'a')
	G.write(L[NroLine-1])
	if NroLine == 4:
		G.write('\n')
	G.close()
	return '%s --> %s' % (FileName, ResultFileName)



# Filter = (('MaxFollowers',3),('MemorySpan',10))
# Filter = ()
Filter = (('RankEffect',70),)

if __name__ == "__main__":
##    print __doc__ + '\n'
	if len(sys.argv) < 3:
		print 'usage:',
		print os.path.basename(sys.argv[0]),
		print '<file1.res... fileN.res | file*.res> <ParamName>'
		print """ The third line of each fileI.res is appended to <ParamName>_Val.csv
		where Val is the value of ParamName in fileI
		"""
		sys.exit()
	if len(sys.argv) == 3 and sys.argv[1].find('*'):
		Args = glob.glob(sys.argv[1])
	else:
		Args = sys.argv[1:-1]
	ParamName = sys.argv[-1]
	for A in Args:
		R = getResult(A, ParamName, NroLine=3, extension='.dat', Constraints=Filter)
##        R = getResult(A, ParamName, NroLine=4, extension='.dis', Constraints=Filter)
		print '.',

