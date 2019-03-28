#!/usr/bin/env python3
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2019                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  EVOLIFE: Automatic manipulation of Evolife configuration files.		   #
##############################################################################

""" EVOLIFE: Automatic manipulation of Evolife configuration files.
	Parameter values are replaced by randomly selecting actual values
	from a range of values mentioned in a 'meta-configuration-file'
	Useful to generate series of experiences automatically
"""

if __name__ == "__main__":
	# Putting Evolife into the path (supposing we are in the same directory tree)
	import sys, os
	for R in os.walk(os.path.abspath('.')[0:os.path.abspath('.').find('Evo')]):
		if os.path.exists(os.path.join(R[0],'Evolife','__init__.py')):
			sys.path.append(R[0])
			break


import sys
import os.path
import random 
import re
import copy
import itertools

# sys.path.append('..')
from Evolife.Tools.Tools import error
from Evolife.Scenarii.Parameters import Parameters, Num

#########################################
# Loading global parameters			 #
#########################################


AlreadyExploredValuesFileName = "EvoGen.dat"

class MetaParameters(Parameters):
	""" class MetaParameters: Parameter values and Parameter ranges
	"""

	def __init__(self, ConfigFile, MetaConfigFile, Multiplicative=False):
		Parameters.__init__(self, ConfigFile)
		self.Original = copy.deepcopy(self.Params)	 # saving the original values
		self.RangeParamWithStep = []
		self.ListParam = []
		self.FixedParam = []
		self.txt_to_ValueRange(MetaConfigFile)
		self.Ranges = self.Get_Ranges()
		self.NoRanges = dict(self.FixedParam)
		self.MetaParams = list(self.Ranges.keys()) + list(self.NoRanges.keys())
		# checking that metaparameters are parameters
		for PP in self.Ranges:
			if not PP in self.Original:
				print("**************************************")
				print("Warning: unknown metaparameter:", PP)
				print("**************************************")
		for PP in self.NoRanges:
			if not PP in self.Original:
				print("******************* Warning: unknown metaparameter:", PP)
			
		self.Multiplicative = Multiplicative
##		print self.FixedParam
		self.ExploredSingle = dict()
		self.ExploredCouple = dict()
		self.ExploredValues(AlreadyExploredValuesFileName)   # gets already explored values
		# checking that explored values are metaparameters 
		for MP in list(self.ExploredSingle.keys()):	#	copy keys
			if MP[0] not in self.MetaParams:
				print("Warning: Explored parameter not metaparameter:", MP[0])
				del self.ExploredSingle[MP]
		for (MP1,MP2) in list(self.ExploredCouple.keys()):	# copy keys
			if MP1[0] not in self.MetaParams:
				print("Warning: Explored parameter not Metaparameter:", MP1[0])
				del self.ExploredCouple[(MP1,MP2)]
			elif MP1[1] not in self.MetaParams:
				print("Warning: explored parameter not metaparameter:", MP1[1])
				del self.ExploredCouple[(MP1,MP2)]
				

	def txt_to_ValueRange(self, MetaConfigFile):
		""" Retrieves parameter range
			Either: <ParamName> <valmin>-<valmax> [<step>]
			or:	 <ParamName> <val1> <val2> ...
		"""
		try:
			Filin = open(MetaConfigFile,"r")
			CfgTxtStr = Filin.read()
			Filin.close()
			self.RangeParamWithStep = re.findall(r"""   # e.g.: GSize  10-20 2 (to mean range(10,21,2)) 
				^(\w+)\s+   # parameter name
				(-?\d+--?\d+)\s+   # integer range:  10-20
				(-?\d+)*   # optional step
				""",CfgTxtStr, flags=re.MULTILINE|re.VERBOSE)
			self.ListParam = re.findall("""  # e.g.:  GSize  10 12 14 16
				^(\w+)\s+   # parameter name
				((?:-?[\d\.]+\s+)+   # sequence of values (note the non-capturing sub-group)
				(?:-?[\d\.]+))\s*$   # terminating value
				""",CfgTxtStr, flags=re.MULTILINE|re.VERBOSE)
			self.FixedParam = re.findall("""  # e.g.:  DisplayPeriod  10
				^(\w+)\s+   # parameter name
				(-?[\d\.]+)\s*$   # terminating value
				""",CfgTxtStr, flags=re.MULTILINE|re.VERBOSE)
		except IOError:
			error("Evolife Evogen: Problem accessing or interpreting metaconfiguration file", CfgTxtFile)
		
	def Range_to_List(self, ParamRange):
		""" Converts a range of values into actual values: '10-20 4' --> [10,14,18]
			Keeps the list if no range
		"""
		PR = re.findall("(-?\d+)-(-?\d+)",ParamRange[1])
		if PR != []:
			if ParamRange[2] != '':
				Step = int(ParamRange[2])
			else:
				Step = 1
			return (ParamRange[0], range(int(PR[0][0]),int(PR[0][1])+1,Step))
		# no range case:
		# return (ParamRange[0], [int(P) for P in re.split("[\-\D]+",ParamRange[1]) if P != ''])
		return (ParamRange[0], [Num(P) for P in ParamRange[1].split()])
		
	def Get_Ranges(self):
		return dict([self.Range_to_List(PR) for PR in self.RangeParamWithStep]
					+ [self.Range_to_List(PR) for PR in self.ListParam]
					)
			
	def Possibilities(self):
		" computes the total number of parameter configurations "
		Configurations = 0
		for R in self.Ranges:
			L = len(self.Ranges[R])
			if self.Multiplicative and Configurations:	Configurations *= L
			else:	Configurations += L
		return Configurations

	def ExploredValues(self, ExploredFileName, Store=False):
		" Retrieves or stores already explored values "
		if Store and (self.ExploredSingle or self.ExploredCouple):
			try:	ExploredFile = open(ExploredFileName, 'w')
			except IOError:	return
			for ParamValue in sorted(self.ExploredSingle):
				ExploredFile.write(ParamValue[0] + '\t' + str(ParamValue[1]) + '\t' )
				ExploredFile.write(str(self.ExploredSingle[ParamValue]) + '\n')
			for ParamValue in sorted(self.ExploredCouple):
				ExploredFile.write(ParamValue[0][0] + '\t' + ParamValue[0][1] + '\t' )
				ExploredFile.write(str(ParamValue[1][0]) + '\t' + str(ParamValue[1][1]) + '\t' )
				ExploredFile.write(str(self.ExploredCouple[ParamValue]) + '\n')
		else:
			try:
				ExploredFile = open(ExploredFileName, 'r')
			except IOError:
				return
			Lines = ExploredFile.read()
##			for L in Lines:
##				SL = L.split('\t')
##				self.Explored[(SL[0],int(SL[1]))] = int(SL[2])
			# Reading explored value file
			ExploredSingle = re.findall(r"""   # e.g.: GSize  10 20 (meaning that value 10 has been tried 20 times) 
				^(\w+)\s+   # parameter name
				(-?[\d\.]+)\s+(\d+)\s*$   # one parameter value followed by count
				""",Lines, flags=re.MULTILINE|re.VERBOSE)
			ExploredCouple = re.findall("""   # e.g.:  GSize  MRate 10 3 16 (meaning that couple (10,3) has been tried 16 times)
				^(\w+)\s+(\w+)\s+   # parameter names
				(-?[\d\.]+)\s+(-?[\d\.]+)\s+   # sequence of two values
				(\d+)\s*$   # terminating count
				""",Lines, flags=re.MULTILINE|re.VERBOSE)

			self.ExploredSingle = dict([((S[0],Num(S[1])),Num(S[2])) for S in ExploredSingle])
			self.ExploredCouple = dict([(((S[0],S[1]),(Num(S[2]),Num(S[3]))),Num(S[4])) for S in ExploredCouple])
								
		ExploredFile.close()
		return

	def PreferredValue(self, Param):
		# priority is given to values that have not been properly explored
		if not self.ExploredSingle:
			return random.choice(self.Ranges[Param])
		PossibleValues = list(self.Ranges[Param][:])
		random.shuffle(PossibleValues)
		for v in PossibleValues:
			if (Param,v) not in self.ExploredSingle:
				return v
		CandidateValue = min(PossibleValues, key=lambda v: self.ExploredSingle[(Param, v)])
		return CandidateValue
			
	def ParamChanging(self, ChangedParam, ChangedValue=None):
		if ChangedParam is not None:
			print('changed parameter:', ChangedParam)
			if ChangedValue is None:	self.Params[ChangedParam] = self.PreferredValue(ChangedParam)
			else:	self.Params[ChangedParam] = ChangedValue
			# self.Params[ChangedParam] = random.choice(self.Ranges[ChangedParam])
			print('\tchosen value:', self.Params[ChangedParam])
			# storing new choice
			NewChoice = (ChangedParam, self.Params[ChangedParam])
			if NewChoice in self.ExploredSingle:
				self.ExploredSingle[NewChoice] += 1
			else:
				self.ExploredSingle[NewChoice] = 1
		else:
			print('No parameter changed')
		
	def PreferredCouple(self, ParamCouple):
		# priority is given to values that have not been properly explored
		(Param1, Param2) = ParamCouple
		if not self.ExploredCouple:
			return (self.PreferredValue(Param1),self.PreferredValue(Param2))
		PV1 = self.Ranges[Param1][:]
		PV2 = self.Ranges[Param2][:]
		random.shuffle(PV1)
		random.shuffle(PV2)
		for v1 in PV1:
			for v2 in PV2:
				if ((Param1,Param2),(v1,v2)) not in self.ExploredCouple:
					return (v1,v2)
		Candidates = sorted([(CoupleValues[1],self.ExploredCouple[CoupleValues])
							 for CoupleValues in self.ExploredCouple], key=lambda x: x[1])
		return Candidates[0][0]
			
	def CoupleChanging(self, Params):
		print('changed parameters: %s and %s' % Params)
		(self.Params[Params[0]],self.Params[Params[1]]) = self.PreferredCouple(Params)
		print('\tchosen values: %d and %d' % (self.Params[Params[0]],self.Params[Params[1]]))
		# storing new choice
		NewChoice = (Params, (self.Params[Params[0]],self.Params[Params[1]]))
		if NewChoice in self.ExploredCouple:
			self.ExploredCouple[NewChoice] += 1
		else:
			self.ExploredCouple[NewChoice] = 1
		
	def RandomSelect(self, OutputFile, verbose=True):
		""" Propagates imposed values, then chooses a parameter to change,
			and chooses a value for this parameter
		"""
		if verbose:
			print(self)
		# print 'Fixed	parameters:', ', '.join(self.NoRanges.keys())
		for ChangedParam in self.NoRanges:
			self.Params[ChangedParam] = self.NoRanges[ChangedParam]
			if verbose:
				# print 'changed parameter:', ChangedParam,
				# print '\timposed value:', self.Params[ChangedParam]
				pass

		# print 'Variable parameters:', ', '.join(self.Ranges.keys())
		if self.Multiplicative:
			if len(self.Ranges) == 2:
				self.CoupleChanging(tuple(sorted(list(self.Ranges.keys()))))
			else:
				for ChangedParam in self.Ranges:
					self.ParamChanging(ChangedParam)
		else:
			# Choosing a variable parameter to change
			# ChangedParam = random.choice([None] + list(self.Ranges.keys()))
			
			(ChangedParam, ChangedValue) = min(itertools.chain(*[[(p, v) for v in self.Ranges[p]] \
				for p in self.Ranges]), key= lambda pv: self.ExploredSingle.get(pv, 0))
			# ChangedParam = random.choice(list(self.Ranges.keys()))
			self.ParamChanging(ChangedParam, ChangedValue)

		self.relevant = set(self.Params.keys())  # all parameters are output
		if OutputFile:
			self.cfg_to_txt(OutputFile)
		else:
			print('No output generated')
		self.Params = self.Original	 # restoring original values

	def __str__(self):
		Msg  = 'Possible %d choices are:\n\t' % self.Possibilities()
		Msg += '\n\t'.join(['\t'.join(P) for P in self.RangeParamWithStep]) + '\n\t'
		Msg += '\n\t'.join(['\t'.join(P) for P in self.ListParam]) + '\n'
		return Msg

#################################
# Loading global parameters	 #
#################################

##Evolife_Parameters = Parameters('Evolife.evo')


	
	
if __name__ == "__main__":
	#	print __doc__ + '\n'
	MULT = False
	if len(sys.argv) > 1 and sys.argv[1] == '-m':
		MULT = True
		sys.argv.pop(1)
	if len(sys.argv) < 3 or len(sys.argv) > 4 or not sys.argv[2].endswith('.evm'):
		print('usage:')
		print('%s [-m] <stable-configuration-file> <meta-configfile> [<output-configfile>]' % os.path.basename(sys.argv[0]))
	else:	
		Evolife_Parameters = MetaParameters(sys.argv[1], sys.argv[2], Multiplicative=MULT)
		# print Evolife_Parameters
		# print Evolife_Parameters.RangeParamWithStep
		# print Evolife_Parameters.ListParam
		# print(Evolife_Parameters.Ranges)
		# print(Evolife_Parameters.ExploredSingle)
		
		
		if len(sys.argv) == 3:
			Evolife_Parameters.RandomSelect('', verbose = True)
		else:
			Evolife_Parameters.RandomSelect(sys.argv[3], verbose = False)
			# storing new choices
			Evolife_Parameters.ExploredValues(AlreadyExploredValuesFileName, Store=True)


