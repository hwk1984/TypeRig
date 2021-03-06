# MODULE: Typerig / Proxy / Node (Obejcts)
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2017-2020 	(http://www.kateliev.com)
# (C) Karandash Type Foundry 		(http://www.karandash.eu)
#------------------------------------------------------------
# www.typerig.com

# No warranties. By using this you agree
# that you use it at your own risk!

# - Dependencies -------------------------
from __future__ import print_function
import math

import fontlab as fl6
import PythonQt as pqt

from typerig.proxy.objects.base import *
#from typerig.proxy.objects.curve import eCurveEx
#from typerig.proxy.objects.contour import pContour
#from typerig.proxy.objects.node import pNode, eNode

# - Init ---------------------------------
__version__ = '0.26.3'

# - Classes -------------------------------
class pNode(object):
	'''Proxy to flNode object

	Constructor:
		pNode(flNode)

	Attributes:
		.fl (flNode): Original flNode 
		.parent (flContour): parent contour
		.contour (flContour): parent contour
	'''
	def __init__(self, node):
		self.fl = node
		self.parent = self.contour = self.fl.contour
		self.name = self.fl.name
		self.index = self.fl.index
		self.selected = self.fl.selected
		self.id = self.fl.id
		self.isOn = self.fl.isOn()
		self.type = self.fl.type
		self.x, self.y = float(self.fl.x), float(self.fl.y)
		self.angle = float(self.fl.angle)

	def __repr__(self):
		return '<{} ({}, {}) index={} time={} on={}>'.format(self.__class__.__name__, self.x, self.y, self.index, self.getTime(), self.isOn)
	
	# - Basics -----------------------------------------------
	def getTime(self):
		return self.contour.getT(self.fl)

	def getNext(self, naked=True):
		return self.fl.nextNode() if naked else self.__class__(self.fl.nextNode())

	def getNextOn(self, naked=True):
		nextNode = self.fl.nextNode()
		nextNodeOn = nextNode if nextNode.isOn() else nextNode.nextNode().getOn()
		return nextNodeOn if naked else self.__class__(nextNodeOn)

	def getPrevOn(self, naked=True):
		prevNode = self.fl.prevNode()
		prevNodeOn = prevNode if prevNode.isOn() else prevNode.prevNode().getOn()
		return prevNodeOn if naked else self.__class__(prevNodeOn)

	def getPrev(self, naked=True):
		return self.fl.prevNode() if naked else self.__class__(self.fl.prevNode())

	def getOn(self, naked=True):
		return self.fl.getOn() if naked else self.__class__(self.fl.getOn())

	def getMaxY(self, naked=True):
		next_node = self.getNextOn()
		prev_node = self.getPrevOn()

		if next_node.position.y() > prev_node.position.y():
			return next_node if naked else self.__class__(next_node)

		return prev_node if naked else self.__class__(prev_node)

	def getMinY(self, naked=True):
		next_node = self.getNextOn()
		prev_node = self.getPrevOn()

		if next_node.position.y() < prev_node.position.y():
			return next_node if naked else self.__class__(next_node)

		return prev_node if naked else self.__class__(prev_node)

	def getSegment(self, relativeTime=0):
		return self.contour.segment(self.getTime() + relativeTime)

	def getSegmentNodes(self, relativeTime=0):
		if len(self.getSegment(relativeTime)) == 4:
			currNode = self.fl if self.fl.isOn() else self.fl.getOn()
			
			if currNode != self.fl:
				tempNode = self.__class__(currNode)

				if tempNode.getTime() != self.getTime():
					currNode = tempNode.getPrevOn()

			currNode_bcpOut = currNode.nextNode()
			nextNode_bcpIn = currNode_bcpOut.nextNode()
			nextNode = nextNode_bcpIn.getOn()
		
			return (currNode, currNode_bcpOut, nextNode_bcpIn, nextNode)
		
		elif len(self.getSegment(relativeTime)) == 2:
			return (self.fl, self.fl.nextNode())

	def getContour(self):
		return self.fl.contour

	def distanceTo(self, node):
		if isinstance(node, self.__class__):
			return self.fl.distanceTo(node.fl.position)
		else:
			return self.fl.distanceTo(node.position)

	def distanceToNext(self):
		return self.fl.distanceTo(self.getNext().position)

	def distanceToPrev(self):
		return self.fl.distanceTo(self.getPrev().position)

	def angleTo(self, node):
		if isinstance(node, self.__class__):
			return self.fl.angleTo(node.fl.position)
		else:
			return self.fl.angleTo(node.position)

	def angleToNext(self):
		return self.fl.angleTo(self.getNext().position)

	def angleToPrev(self):
		return self.fl.angleTo(self.getPrev().position)

	def insertAfter(self, time):
		return self.contour.insertNodeTo(self.getTime() + time)

	def insertBefore(self, time):
		return self.contour.insertNodeTo(self.getPrevOn(False).getTime() + time)

	def insertAfterDist(self, distance):
		return self.insertAfter(ratfrac(distance, self.distanceToNext(), 1))

	def insertBeforeDist(self, distance):
		return self.insertBefore(1 - ratfrac(distance, self.distanceToPrev(), 1))

	def remove(self):
		self.contour.removeOne(self.fl)

	def update(self):
		self.fl.update()
		self.x, self.y = float(self.fl.x), float(self.fl.y)

	# - Transformation -----------------------------------------------
	def reloc(self, newX, newY):
		'''Relocate the node to new coordinates'''
		self.fl.x, self.fl.y = newX, newY
		self.x, self.y = newX, newY	
		#self.update()
	
	def shift(self, deltaX, deltaY):
		'''Shift the node by given amout'''
		self.fl.x += deltaX
		self.fl.y += deltaY
		self.x, self.y = self.fl.x, self.fl.y 
		#self.update()

	def smartReloc(self, newX, newY):
		'''Relocate the node and adjacent BCPs to new coordinates'''
		self.smartShift(newX - self.fl.x, newY - self.fl.y)

	def smartShift(self, deltaX, deltaY):
		'''Shift the node and adjacent BCPs by given amout'''
		if self.isOn:	
			nextNode = self.getNext(False)
			prevNode = self.getPrev(False)

			for node, mode in [(prevNode, not prevNode.isOn), (self, self.isOn), (nextNode, not nextNode.isOn)]:
				if mode: node.shift(deltaX, deltaY)
		else:
			self.shift(deltaX, deltaY)

	# - Effects --------------------------------
	def getSmartAngle(self):
		return (self.fl.isSmartAngle(), self.fl.smartAngleR)

	def setSmartAngle(self, radius):
		self.fl.smartAngleR = radius
		return self.fl.setSmartAngleEnbl(True)

	def delSmartAngle(self):
		return self.fl.setSmartAngleEnbl(False)

	def setSmartAngleRadius(self, radius):
		self.fl.smartAngleR = radius

	def getSmartAngleRadius(self):
		return self.fl.smartAngleR

class pNodesContainer(object):
	'''Abstract nodes container

	Constructor:
		pNodesContainer(list(flNode))

	Attributes:
		
	'''
	def __init__(self, nodeList, extend=pNode):
		
		# - Init
		if extend is not None: 
			self.nodes = [extend(node) for node in nodeList]
		else:
			self.nodes = nodeList
		
		self.extender = extend
		self.bounds = self.getBounds()
		self.x = lambda : self.getBounds().x
		self.y = lambda : self.getBounds().y
		self.width = lambda : self.getBounds().width
		self.height  = lambda : self.getBounds().height

	def __getitem__(self, index):
		return self.nodes.__getitem__(index)

	def __setitem__(self, index, value):
		return self.nodes.__setitem__(index, value)

	def __delitem__(self, index):
		self.nodes.__delitem__(index)

	def __repr__(self):
		return '<{} ({}, {}, {}, {}) nodes={}>'.format(self.__class__.__name__, self.bounds.x, self.bounds.y, self.bounds.width, self.bounds.height, len(self.nodes))

	def __len__(self):
		return len(self.nodes)

	def __hash__(self):
		return self.nodes.__hash__()

	def clone(self):
		try:
			return self.__class__([node.fl.clone() for node in self.nodes], extend=self.extender)
		except AttributeError:
			return self.__class__([node.clone() for node in self.nodes], extend=self.extender)

	def reverse(self):
		return self.__class__(list(reversed(self.nodes)), extend=None)

	def insert(self, index, value):
		self.nodes.insert(index, value)

	def append(self, index):
		self.nodes.append(index)

	def getPosition(self):
		return [(node.x, node.y) for node in self.nodes]

	def getCoord(self):
		return [Coord(node) for node in self.nodes]

	def getBounds(self):
		return bounds(self.getPosition())

	def shift(self, dx, dy):
		for node in self.nodes:
			node.shift(dx, dy)

	def smartShift(self, dx, dy):
		for node in self.nodes:
			node.smartShift(dx, dy)

	def applyTransform(self, transform):
		for node in self.nodes:
			try:
				node.fl.applyTransform(transform)
			except AttributeError:
				node.applyTransform(transform)

	def cloneTransform(self, transform):
		temp_container = self.clone()
		temp_container.applyTransform(transform)
		return temp_container


# -- Extensions --------------------------------------		
class eNode(pNode):
	'''Extended representation of the Proxy Node, adding some advanced functionality

	Constructor:
		eNode(flNode)
		
	'''
	# - Extension -----------------------
	def asCoord(self):
		'''Returns Coord object of the node.'''
		return Coord(float(self.x), float(self.y))

	def getNextLine(self):
		return Line(self.fl, self.getNextOn())

	def getPrevLine(self):
		return Line(self.getPrevOn(), self.fl)

	def diffTo(self, node):
		cPos = self.fl.position
		nPos = node.fl.position if isinstance(node, self.__class__) else node.position
		
		xdiff = nPos.x() - float(cPos.x())
		ydiff = nPos.y() - float(cPos.y())
		return xdiff, ydiff

	def diffToNext(self):
		return self.diffTo(self.getNext())

	def diffToPrev(self):
		return self.diffTo(self.getPrev())

	def shiftFromNext(self, diffX, diffY):
		newX = self.getNext().x + diffX
		newY = self.getNext().y + diffY
		self.reloc(newX, newY)	

	def shiftFromPrev(self, diffX, diffY):
		newX = self.getPrev().x + diffX
		newY = self.getPrev().y + diffY
		self.reloc(newX, newY)		

	def polarTo(self, node):
		return self.angleTo(node), self.distanceTo(node)

	def polarToNext(self):
		return self.angleToNext(), self.distanceToNext()

	def polarToPrev(self):
		return self.angleToPrev(), self.distanceToPrev()

	def polarReloc(self, angle, distance):
		newX = distance * math.cos(angle) + self.x
		newY = distance * math.sin(angle) + self.y
		self.reloc(newX, newY)

	def smartPolarReloc(self, angle, distance):
		newX = distance * math.cos(angle) + self.x
		newY = distance * math.sin(angle) + self.y
		self.smartReloc(newX, newY)

	def polarRelocFromPrev(self, distance):
		newX = distance * math.cos(angle + pi/2*[-1,1][self.contour.clockwise]) + self.getPrev().x
		newY = distance * math.sin(angle + pi/2*[-1,1][self.contour.clockwise]) + self.getPrev().y

		self.reloc(newX, newY)

	# - Corner operations ---------------
	def cornerMitre(self, mitreSize=5, isRadius=False):
		# - Calculate unit vectors and shifts
		nextNode = self.getNextOn(False)
		prevNode = self.getPrevOn(False)

		nextUnit = Coord(nextNode.asCoord() - self.asCoord()).unit
		prevUnit = Coord(prevNode.asCoord() - self.asCoord()).unit
		
		if not isRadius:
			angle = math.atan2(nextUnit | prevUnit, nextUnit & prevUnit)
			radius = abs((float(mitreSize)/2)/math.sin(angle/2))
		else:
			radius = mitreSize

		nextShift = nextUnit * radius
		prevShift = prevUnit * radius

		# - Insert Node and process
		nextNode = self.__class__(self.insertAfter(.01)) # Was 0?, something went wrong in 6871
		nextNode.smartReloc(self.x, self.y) # Go back because something went wrong in 6871

		self.smartShift(*prevShift.tuple)
		nextNode.smartShift(*nextShift.tuple)

		return (self.fl, nextNode.fl)

	def cornerRound(self, size=5, proportion=None, curvature=None, isRadius=False):
		# - Calculate unit vectors and shifts
		nextNode = self.getNextOn(False)
		prevNode = self.getPrevOn(False)

		nextUnit = Coord(nextNode.asCoord() - self.asCoord()).unit
		prevUnit = Coord(prevNode.asCoord() - self.asCoord()).unit
		
		if not isRadius:
			angle = math.atan2(nextUnit | prevUnit, nextUnit & prevUnit)
			radius = abs((float(size)/2)/math.sin(angle/2))
		else:
			radius = size

		nextShift = nextUnit * radius
		prevShift = prevUnit * radius

		# - Insert Nodes and process
		nextNode = self.__class__(self.insertAfter(.01)) # Was 0?, something went wrong in 6871
		nextNode.smartReloc(self.x, self.y) # Go back because something went wrong in 6871

		self.smartShift(*prevShift.tuple)
		nextNode.smartShift(*nextShift.tuple)
		
		# -- Make round corner
		nextNode.fl.convertToCurve(True)
		segment = self.getSegmentNodes()
		
		# -- Curvature and handle length  
		curve = Curve(segment)

		if proportion is not None: 
			new_curve = curve.solve_proportional_handles(proportion)
			segment[1].x = new_curve.p1.x; segment[1].y = new_curve.p1.y
			segment[2].x = new_curve.p2.x; segment[2].y = new_curve.p2.y
					
		if curvature is not None: 
			new_curve = curve.solve_hobby(curvature)
			segment[1].x = new_curve.p1.x; segment[1].y = new_curve.p1.y
			segment[2].x = new_curve.p2.x; segment[2].y = new_curve.p2.y

		return segment

	def cornerTrap(self, aperture=10, depth=20, trap=2):
		'''Trap a corner by given aperture.

		Arguments:
			aperture (float): Width of the traps mouth (opening);
			depth (float): Length of the traps sides;
			trap (float): Width of the traps bottom.

		Returns:
			tuple(flNode, flNode, flNode, flNode)
		'''
		# - Init
		adjust = float(aperture - trap)/2

		# - Calculate for aperture postision and structure
		nextNode = self.getNextOn(False)
		prevNode = self.getPrevOn(False)

		nextUnit = Coord(nextNode.asCoord() - self.asCoord()).unit
		prevUnit = Coord(prevNode.asCoord() - self.asCoord()).unit

		angle = math.atan2(nextUnit | prevUnit, nextUnit & prevUnit)
		radius = abs((float(aperture)/2)/math.sin(angle/2))
		
		bCoord = self.asCoord() + (nextUnit * -radius)
		cCoord = self.asCoord() + (prevUnit * -radius)

		aCoord = self.asCoord() + (prevUnit * radius)
		dCoord = self.asCoord() + (nextUnit * radius)

		# - Calculate for depth
		abUnit = Coord(aCoord - bCoord).unit
		dcUnit = Coord(dCoord - cCoord).unit

		bCoord = aCoord + abUnit*-depth
		cCoord = dCoord + dcUnit*-depth

		# - Calculate for trap (size)
		bcUnit = (bCoord - cCoord).unit
		cbUnit = (cCoord - bCoord).unit

		bCoord += bcUnit*-adjust
		cCoord += cbUnit*-adjust

		# - Insert Nodes and cleanup
		b = self.__class__(self.insertAfter(0.01)) # .01 quickfix - should be 0
		c = self.__class__(b.insertAfter(0.01))
		d = self.__class__(c.insertAfter(0.01))

		b.fl.convertToLine()
		c.fl.convertToLine()
		d.fl.convertToLine()

		# - Position nodes
		self.smartReloc(*aCoord.tuple)
		b.smartReloc(*bCoord.tuple)
		d.smartReloc(*dCoord.tuple)
		c.smartReloc(*cCoord.tuple)

		return (self.fl, b.fl, c.fl, d.fl)

	def cornerTrapInc(self, incision=10, depth=50, trap=2, smooth=True):
		'''Trap a corner by given incision into the glyph flesh.
		
		Arguments:
			incision (float): How much to cut into glyphs flesh based from that corner inward;
			depth (float): Length of the traps sides;
			trap (float): Width of the traps bottom;
			smooth (bool): Creates a smooth trap.

		Returns:
			tuple(flNode, flNode, flNode, flNode) four base (ON) nodes of the trap.
		'''
		# - Init
		remains = depth - incision
		base_coord = self.asCoord()

		# - Calculate for aperture postision and structure
		nextNode = self.getNextOn(False)
		prevNode = self.getPrevOn(False)

		nextUnit = Coord(nextNode.asCoord() - self.asCoord()).unit
		prevUnit = Coord(prevNode.asCoord() - self.asCoord()).unit

		angle = math.atan2(nextUnit | prevUnit, nextUnit & prevUnit)
		aperture = abs(2*(remains/math.sin(math.radians(90) - angle/2)*math.sin(angle/2)))
		adjust = float(aperture - trap)/2
		radius = abs((float(aperture)/2)/math.sin(angle/2))
		
		bCoord = self.asCoord() + (nextUnit * -radius)
		cCoord = self.asCoord() + (prevUnit * -radius)

		aCoord = self.asCoord() + (prevUnit * radius)
		dCoord = self.asCoord() + (nextUnit * radius)

		# - Calculate for depth
		abUnit = Coord(aCoord - bCoord).unit
		dcUnit = Coord(dCoord - cCoord).unit

		bCoord = aCoord + abUnit*-depth
		cCoord = dCoord + dcUnit*-depth

		# - Calculate for trap (size)
		bcUnit = (bCoord - cCoord).unit
		cbUnit = (cCoord - bCoord).unit

		bCoord += bcUnit*-adjust
		cCoord += cbUnit*-adjust

		# - Insert Nodes and cleanup
		b = self.__class__(self.insertAfter(0.01)) # .01 quickfix - should be 0
		c = self.__class__(b.insertAfter(0.01))
		d = self.__class__(c.insertAfter(0.01))

		b.fl.convertToLine()
		c.fl.convertToLine()
		d.fl.convertToLine()

		# - Position nodes
		self.smartReloc(*aCoord.tuple)
		b.smartReloc(*bCoord.tuple)
		d.smartReloc(*dCoord.tuple)
		c.smartReloc(*cCoord.tuple)

		# - Make smooth trap transition
		if smooth: 
			# -- Convert nodes and extend bpc-s
			b.fl.convertToCurve()
			d.fl.convertToCurve()

			# -- Set nodes as smooth
			self.fl.smooth = True
			d.fl.smooth = True

			# -- Align bpc-s to the virtual lines connection sides of the trap with the original base node
			side_ab = Line(self.asCoord(), base_coord)
			side_cd = Line(base_coord, d.asCoord())
			control = (True, False)
			
			bpc_a, bpc_c = self.getNext(False), c.getNext(False)
			bpc_b, bpc_d = b.getPrev(False), d.getPrev(False)

			bpc_a.alignTo(side_ab, control)
			bpc_b.alignTo(side_ab, control)
			bpc_c.alignTo(side_cd, control)
			bpc_d.alignTo(side_cd, control)
			
		return (self.fl, b.fl, c.fl, d.fl)

	# - Movement ------------------------
	def interpShift(self, shift_x, shift_y):
		'''Interpolated move aka Interpolated Nudge.
		
		Arguments:
			shift_x, shift_y (float)
		'''
		if self.isOn:
			# - Init 
			shift = Coord(shift_x, shift_y)
			currSegmet, prevSegment = self.getSegment(), self.getSegment(-1)

			if prevSegment == None:
				prevSegment = self.contour.segments()[-1]
			
			# - Process segments
			if len(currSegmet) == 4:
				currCurve = Curve(currSegmet)
				new_currCurve = currCurve.lerp_first(shift)
				
				currNode_bcpOut = self.getNext(False)
				nextNode_bcpIn = currNode_bcpOut.getNext(False)
				nextNode = nextNode_bcpIn.getOn(False)

				currSegmetNodes = [self, currNode_bcpOut, nextNode_bcpIn, nextNode]
				
				# - Set node positions
				for i in range(len(currSegmetNodes)):
					currSegmetNodes[i].smartReloc(*new_currCurve.points[i].tuple)

			if len(prevSegment) == 4:
				prevCurve = Curve(prevSegment)
				new_prevCurve = prevCurve.lerp_last(shift)

				currNode_bcpIn = self.getPrev(False)
				prevNode_bcpOut = currNode_bcpIn.getPrev(False)
				prevNode = prevNode_bcpOut.getOn(False)

				prevSegmentNodes = [prevNode, prevNode_bcpOut, currNode_bcpIn, self]
				
				# - Set node positions
				for i in range(len(prevSegmentNodes)-1,-1,-1):
					prevSegmentNodes[i].smartReloc(*new_prevCurve.points[i].tuple)

			if len(currSegmet) == 2 and len(prevSegment) == 2:
				self.smartShift(*shift.tuple)

	def slantShift(self, shift_x, shift_y, angle):
		'''Slanted move - move a node (in inclined space) according to Y coordinate slanted at given angle.
		
		Arguments:
			shift_x, shift_y (float)
			angle (float): Angle in degrees
		'''
		# - Init
		cNode = Coord((self.x + shift_x, self.y))
		cNode.angle = angle
		
		# - Calculate & set
		newX = cNode.solve_width(cNode.y + shift_y)
		#self.fl.smartSetXY(pqt.QtCore.QPointF(newX, self.y + shift_y))
		self.smartReloc(newX, self.y + shift_y)

	def alignTo(self, entity, align=(True, True)):
		'''Align current node to a node or line given.
		Arguments:
			entity (flNode, pNode, eNode or Line)
			align (tuple(Align_X (bool), Align_Y (bool)) 
		'''
		if isinstance(entity, (fl6.flNode, pNode, self.__class__)):
			newX = entity.x if align[0] else self.fl.x
			newY = entity.y if align[1] else self.fl.y
				
			#self.fl.smartSetXY(pqt.QtCore.QPointF(newX, newY))
			self.smartReloc(newX, newY)

		elif isinstance(entity, (Line, Vector)):
			newX = entity.solve_x(self.fl.y) if align[0] else self.fl.x
			newY = entity.solve_y(self.fl.x) if align[1] else self.fl.y

			#self.fl.smartSetXY(pqt.QtCore.QPointF(newX, newY))
			self.smartReloc(newX, newY)


class eNodesContainer(pNodesContainer):
	'''Extended representation of Abstract nodes container

	Constructor:
		eNodesContainer(list(flNode))
			
	'''
	def alignTo(self, entity, alignMode='', align=(True,True)):
		'''Align Abstract nodes container to.
		Arguments:
			entity ()
			alignMode (String) : L(left), R(right), C(center), T(top), B(bottom), E(vertical center) !ORDER MATTERS
		'''
			
		# - Helper
		def getAlignDict(item):
			align_dict = {	'L': item.x(), 
							'R': item.x() + item.width(), 
							'C': item.x() + item.width()/2,
							'B': item.y(), 
							'T': item.y() + item.height(), 
							'E': item.y() + item.height()/2
						}

			return align_dict

		# - Init
		if len(alignMode)==2:
			alignX, alignY = alignMode.upper()

			# -- Get target for alignment
			if isinstance(entity, (fl6.flNode, pNode, eNode, Coord, pqt.QtCore.QPointF)):
				target = Coord(entity.x, entity.y)

			elif isinstance(entity, (fl6.flContour, self.__class__)): #(fl6.flContour, pContour, self.__class__)
				
				if isinstance(entity, fl6.flContour):
					temp_entity = self.__class__(fl6.flContour.nodes())
				else:
					temp_entity = entity

				align_dict = getAlignDict(temp_entity)
				target = Coord(align_dict[alignX], align_dict[alignY])

			# -- Get source for alignment
			align_dict = getAlignDict(self)
			source =  Coord(align_dict[alignX], align_dict[alignY])

			# - Process
			shift = source - target
			shift_dx = abs(shift.x)*[1,-1][source.x > target.x] if align[0] else 0.
			shift_dy = abs(shift.y)*[1,-1][source.y > target.y] if align[1] else 0.
			
			self.shift(shift_dx, shift_dy)

		else:
			print('ERROR:\t Invalid Align Mode: {}'.format(alignMode))