# MODULE: Typerig / Proxy / Kern (Objects)
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2018-2020 	(http://www.kateliev.com)
# (C) Karandash Type Foundry 		(http://www.karandash.eu)
#------------------------------------------------------------
# www.typerig.com

# No warranties. By using this you agree
# that you use it at your own risk!

# - Dependencies -------------------------
from __future__ import print_function

import fontlab as fl6
import PythonQt as pqt

from typerig.core.objects.collection import extBiDict

# - Init ---------------------------------
__version__ = '0.26.0'

# - Classes -------------------------------
class pKerning(object):
	'''Proxy to fgKerning object

	Constructor:
		pKerning(fgKerning)

	Attributes:
		.fg (fgKerning): Original Fontgate Kerning object 
		.groups (fgKerningGroups): Fontgate Group kerning object
	'''
	def __init__(self, fgKerningObject, externalGroupData=None):
		self.fg = self.kerning = fgKerningObject
		self.useExternalGroupData = False
		self.external_groups = None

		
		if externalGroupData is not None:
			self.external_groups = externalGroupData
			self.useExternalGroupData = True

		self.__kern_group_type = {'L':'KernLeft', 'R':'KernRight', 'B': 'KernBothSide'}
		self.__kern_pair_mode = ('glyphMode', 'groupMode')
		
		#self.groups = self.groups()
		
	def __repr__(self):
		return '<%s pairs=%s groups=%s external=%s>' % (self.__class__.__name__, len(self.kerning), len(self.groups().keys()), self.useExternalGroupData)

	# - Basic functions -------------------------------------
	def groups(self):
		if not self.useExternalGroupData:
			return self.fg.groups
		else:
			return self.external_groups

	def setExternalGroupData(self, externalGroupData):
		self.external_groups = externalGroupData
		self.useExternalGroupData = True	

	def storeExternalGroupData(self):
		for key, value in self.useExternalGroupData.iteritems():
			self.fg.groups[key] = value

	def resetGroups(self):
		# - Delete all group kerning at given layer
		self.groups().clear()	

	def asDict(self):
		return self.fg.asDict()

	def asList(self):
		# Structure:
		# 	fgKerning{fgKernigPair(fgKerningObject(glyph A, mode), fgKerningObject(glyph B, mode)) : kern value, ...}
		return [[[item.asTuple() for item in key.asTuple()], value] for key, value in self.kerning.asDict().iteritems()]

	def groupsAsDict(self):
		# - Semi working fixup of Build 6927 Bug
		if not self.useExternalGroupData:
			return self.fg.groups.asDict()
		else:
			return self.external_groups

	def groupsBiDict(self):
		temp_data = {}

		for key, value in self.groupsAsDict().iteritems():
			temp_data.setdefault(value[1], {}).update({key : value[0]})

		return {key:extBiDict(value) for key, value in temp_data.iteritems()}

	def groupsFromDict(self, groupDict):
		# - Build Group kerning from dictionary
		kerning_groups = self.groups()
		
		for key, value in groupDict.iteritems():
			kerning_groups[key] = value

	def removeGroup(self, key):
		'''Remove a group from fonts kerning groups at given layer.'''
		del self.groups()[key]

	def renameGroup(self, oldkey, newkey):
		'''Rename a group in fonts kerning groups at given layer.'''
		self.groups().rename(oldkey, newkey)

	def addGroup(self, key, glyphNameList, type):
		'''Adds a new group to fonts kerning groups.
		Args:
			key (string): Group name
			glyphNameList (list(string)): List of glyph names
			type (string): Kern group types: L - Left group (1st), R - Right group (2nd), B - Both (1st and 2nd)
			layer (None, Int, String)
		
		Returns:
			None
		'''
		self.groups()[key] = (glyphNameList, self.__kern_group_type[type.upper()])

	def getPairObject(self, pairTuple):
		left, right = pairTuple
		modeLeft, modeRight = 0, 0
		groupsBiDict = self.groupsBiDict()
		
		if len(groupsBiDict.keys()):
			if groupsBiDict['KernLeft'].inverse.has_key(left):
				left = groupsBiDict['KernLeft'].inverse[left]
				modeLeft = 1

			elif groupsBiDict['KernBothSide'].inverse.has_key(left):
				left = groupsBiDict['KernBothSide'].inverse[left]
				modeLeft = 1

			if groupsBiDict['KernRight'].inverse.has_key(right):
				right = groupsBiDict['KernRight'].inverse[right]
				modeRight = 1

			elif groupsBiDict['KernBothSide'].inverse.has_key(right):
				right = groupsBiDict['KernBothSide'].inverse[right]
				modeRight = 1

		
		return self.newPair(left[0], right[0], modeLeft, modeRight)

	def getPair(self, pairTuple):
		pairObject = self.getPairObject(pairTuple)
		kern_pairs = self.fg.keys()

		if pairObject in kern_pairs:
			return (pairObject, self.fg[kern_pairs.index(pairObject)])

	def getKerningForLeaders(self, transformLeft=None, transformRight=None):
		''' Now in FL6 we do not have leaders, but this returns the first glyph name in the group '''
		kerning_data = self.fg.items()
		return_data = []

		for kern_pair, kern_value in kerning_data:
			left_name, right_name = kern_pair.left.id, kern_pair.right.id
			left_mode, right_mode = kern_pair.left.mode, kern_pair.right.mode

			left_leader = left_name if left_mode == self.__kern_pair_mode[0] else self.groups()[left_name][0][0]
			right_leader = right_name if right_mode == self.__kern_pair_mode[0] else self.groups()[right_name][0][0]

			left_leader = left_leader if transformLeft is None else transformLeft(left_leader)
			right_leader = right_leader if transformRight is None else transformRight(right_leader)

			return_data.append(((left_leader, right_leader), kern_value))

		return return_data
	
	def newPair(self, glyphLeft, glyphRight, modeLeft, modeRight):
		if not isinstance(modeLeft, str): modeLeft = self.__kern_pair_mode[modeLeft]
		if not isinstance(modeRight, str): modeRight = self.__kern_pair_mode[modeRight]
		return fgt.fgKerningObjectPair(glyphLeft, glyphRight, modeLeft, modeRight)