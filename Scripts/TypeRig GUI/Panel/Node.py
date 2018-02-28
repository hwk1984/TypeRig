#FLM: TAB Node Tools
# ----------------------------------------
# (C) Vassil Kateliev, 2018 (http://www.kateliev.com)
# (C) Karandash Type Foundry (http://www.karandash.eu)
#-----------------------------------------

# No warranties. By using this you agree
# that you use it at your own risk!

# - Init
global pLayers
pLayers = None
app_name, app_version = 'TypeRig | Nodes', '0.37'

# - Dependencies -----------------
import fontlab as fl6
import fontgate as fgt
from PythonQt import QtCore, QtGui
from typerig.glyph import eGlyph
from typerig.node import eNode
from typerig.proxy import pFont

#from typerig.utils import outputHere # Remove later!

# - Sub widgets ------------------------
class basicOps(QtGui.QGridLayout):
	# - Basic Node operations
	def __init__(self):
		super(basicOps, self).__init__()
		
		# - Basic operations
		self.btn_insert = QtGui.QPushButton('&Insert')
		self.btn_remove = QtGui.QPushButton('&Remove')
		self.btn_mitre = QtGui.QPushButton('&Mitre')
		self.btn_knot = QtGui.QPushButton('&Overlap')
				
		self.btn_insert.setMinimumWidth(80)
		self.btn_remove.setMinimumWidth(80)
		self.btn_mitre.setMinimumWidth(80)
		self.btn_knot.setMinimumWidth(80)

		self.btn_insert.setToolTip('Insert Node after Selection\nat given time T.')
		self.btn_remove.setToolTip('Remove Selected Nodes!\nFor proper curve node deletion\nalso select the associated handles!')
		self.btn_mitre.setToolTip('Mitre corner using size X.')
		self.btn_knot.setToolTip('Overlap corner using radius -X.')
		
		self.btn_insert.clicked.connect(self.insertNode)
		self.btn_remove.clicked.connect(self.removeNode)
		self.btn_mitre.clicked.connect(lambda: self.cornerMitre(False))
		self.btn_knot.clicked.connect(lambda: self.cornerMitre(True))

		# - Edit fields
		self.edt_time = QtGui.QLineEdit('0.5')
		self.edt_radius = QtGui.QLineEdit('5')

		self.edt_time.setToolTip('Insertion Time.')
		self.edt_radius.setToolTip('Mitre size/Overlap or Round Radius.')

		# -- Build: Basic Ops
		self.addWidget(self.btn_insert, 0, 0)
		self.addWidget(QtGui.QLabel('T:'), 0, 1)
		self.addWidget(self.edt_time, 0, 2)
		self.addWidget(self.btn_remove, 0, 3)

		self.addWidget(self.btn_mitre,1,0)
		self.addWidget(QtGui.QLabel('X:'), 1, 1)
		self.addWidget(self.edt_radius,1,2)
		self.addWidget(self.btn_knot,1,3)

	def insertNode(self):
		glyph = eGlyph()
		selection = glyph.selectedAtContours(True)
		wLayers = glyph._prepareLayers(pLayers)

		for layer in wLayers:
			nodeMap = glyph._mapOn(layer)
			
			for cID, nID in reversed(selection):
				glyph.insertNodeAt(cID, nodeMap[cID][nID] + float(self.edt_time.text), layer)

		glyph.updateObject(glyph.fl, 'Insert Node @ %s.' %'; '.join(wLayers))
		glyph.update()

	def removeNode(self):
		glyph = eGlyph()
		wLayers = glyph._prepareLayers(pLayers)

		'''
		selection = glyph.selectedAtContours()
		for layer in wLayers:
			for cID, nID in reversed(selection):
				glyph.removeNodeAt(cID, nID, layer)
				glyph.contours(layer)[cID].updateIndices()

				#glyph.contours()[cID].clearNodes()
		'''
		
		# Kind of working
		for layer in wLayers:
			selection = glyph.selectedAtContours(False, layer)

			for contour, node in reversed(selection):
				prevNode, nextNode = node.getPrev(), node.getNext()
				
				if not prevNode.isOn:
					contour.removeOne(prevNode)
			
				if not nextNode.isOn:
					contour.removeOne(nextNode)

				contour.removeOne(node)	
				contour.updateIndices()
		
		'''
		# - Not Working Again!
		from typerig.utils import groupConsecutives		
		selection = glyph.selectedAtContours()
		tempDict = {}

		for cID, nID in selection:
			tempDict.setdefault(cID, []).append(nID)

		for layer in wLayers:
			for cID, nIDlist in tempDict.iteritems():
				nidList = groupConsecutives(nIDlist)

				for pair in reversed(nidList):
					
					nodeA = eNode(glyph.contours(layer)[cID].nodes()[pair[-1] if len(pair) > 1 else pair[0]]).getNextOn()
					nodeB = eNode(glyph.contours(layer)[cID].nodes()[pair[0]]).getPrevOn()

					glyph.contours(layer)[cID].removeNodesBetween(nodeB, nodeA)
									
		'''
		glyph.updateObject(glyph.fl, 'Delete Node @ %s.' %'; '.join(wLayers))
		glyph.update()

	def cornerMitre(self, doKnot=False):
		from typerig.node import eNode
		glyph = eGlyph()
		wLayers = glyph._prepareLayers(pLayers)
		
		for layer in wLayers:
			selection = [eNode(node) for node in glyph.selectedNodes(layer, True)]
			
			for node in reversed(selection):
				if not doKnot:
					node.cornerMitre(float(self.edt_radius.text))
				else:
					node.cornerMitre(-float(self.edt_radius.text), True)


		action = 'Mitre Corner' if not doKnot else 'Overlap Corner'
		glyph.updateObject(glyph.fl, '%s @ %s.' %(action, '; '.join(wLayers)))
		glyph.update()


class alignNodes(QtGui.QGridLayout):
	# - Basic Node operations
	def __init__(self):
		super(alignNodes, self).__init__()
		
		# - Buttons
		self.btn_left = QtGui.QPushButton('Left')
		self.btn_right = QtGui.QPushButton('Right')
		self.btn_top = QtGui.QPushButton('Top')
		self.btn_bottom = QtGui.QPushButton('Bottom')
		self.btn_solveY = QtGui.QPushButton('Lineup Min/Max Y')
		self.btn_solveX = QtGui.QPushButton('Lineup Min/Max X')

		self.btn_solveY.setToolTip('Channel Process selected nodes according to Y values')
		self.btn_solveX.setToolTip('Channel Process selected nodes according to X values')

		self.btn_left.setMinimumWidth(40)
		self.btn_right.setMinimumWidth(40)
		self.btn_top.setMinimumWidth(40)
		self.btn_bottom.setMinimumWidth(40)
		
		self.btn_left.clicked.connect(lambda: self.alignNodes('L'))
		self.btn_right.clicked.connect(lambda: self.alignNodes('R'))
		self.btn_top.clicked.connect(lambda: self.alignNodes('T'))
		self.btn_bottom.clicked.connect(lambda: self.alignNodes('B'))
		self.btn_solveY.clicked.connect(lambda: self.alignNodes('Y'))
		self.btn_solveX.clicked.connect(lambda: self.alignNodes('X'))
				
		self.addWidget(self.btn_left, 0,0)
		self.addWidget(self.btn_right, 0,1)
		self.addWidget(self.btn_top, 0,2)
		self.addWidget(self.btn_bottom, 0,3)
		self.addWidget(self.btn_solveY, 1,0,1,2)
		self.addWidget(self.btn_solveX, 1,2,1,2)

	def alignNodes(self, mode):
		from typerig.brain import Line

		glyph = eGlyph()
		wLayers = glyph._prepareLayers(pLayers)
		
		for layer in wLayers:
			selection = [eNode(node) for node in glyph.selectedNodes(layer)]
			
			if mode == 'L':
				target = min(selection, key=lambda item: item.x)
				control = (True, False)

			elif mode == 'R':
				target = max(selection, key=lambda item: item.x)
				control = (True, False)
			
			elif mode == 'T':
				target = max(selection, key=lambda item: item.y)
				control = (False, True)
			
			elif mode == 'B':
				target = min(selection, key=lambda item: item.y)
				control = (False, True)
			
			elif mode == 'Y':
				target = Line(min(selection, key=lambda item: item.y).fl, max(selection, key=lambda item: item.y).fl)
				control = (True, False)

			elif mode == 'X':
				target = Line(min(selection, key=lambda item: item.x).fl, max(selection, key=lambda item: item.x).fl)
				control = (False, True)

			for node in selection:
				node.alignTo(target, control)

		glyph.updateObject(glyph.fl, 'Align Nodes @ %s.' %'; '.join(wLayers))
		glyph.update()


class breakContour(QtGui.QGridLayout):
	# - Split/Break contour 
	def __init__(self):
		super(breakContour, self).__init__()
			 
		# -- Split button
		self.btn_splitContour = QtGui.QPushButton('&Break')
		self.btn_splitContourClose = QtGui.QPushButton('&Break && Close')
		
		self.btn_splitContour.clicked.connect(self.splitContour)
		self.btn_splitContourClose.clicked.connect(self.splitContourClose)
		
		self.btn_splitContour.setMinimumWidth(80)
		self.btn_splitContourClose.setMinimumWidth(80)

		self.btn_splitContour.setToolTip('Break contour at selected Node(s).')
		self.btn_splitContourClose.setToolTip('Break contour and close open contours!\nUseful for cutting stems and etc.')

		# -- Extrapolate value
		self.edt_expand = QtGui.QLineEdit('0.0')
		#self.edt_expand.setMinimumWidth(30)

		self.edt_expand.setToolTip('Extrapolate endings.')
								
		# -- Build: Split/Break contour
		self.addWidget(self.btn_splitContour, 0, 0)
		self.addWidget(QtGui.QLabel('E:'), 0, 1)
		self.addWidget(self.edt_expand, 0, 2)
		self.addWidget(self.btn_splitContourClose, 0, 3)
				
	def splitContour(self):
		glyph = eGlyph()
		glyph.splitContour(layers=pLayers, expand=float(self.edt_expand.text), close=False)
		glyph.updateObject(glyph.fl, 'Break Contour @ %s.' %'; '.join(glyph._prepareLayers(pLayers)))
		glyph.update()

	def splitContourClose(self):
		glyph = eGlyph()
		glyph.splitContour(layers=pLayers, expand=float(self.edt_expand.text), close=True)
		glyph.updateObject(glyph.fl, 'Break Contour & Close @ %s.' %'; '.join(glyph._prepareLayers(pLayers)))
		glyph.update()        

class basicContour(QtGui.QGridLayout):
	# - Split/Break contour 
	def __init__(self):
		super(basicContour, self).__init__()
		self.btn_BL = QtGui.QPushButton('B L')
		self.btn_TL = QtGui.QPushButton('T L')
		self.btn_BR = QtGui.QPushButton('B R')
		self.btn_TR = QtGui.QPushButton('T R')
		self.btn_close= QtGui.QPushButton('C&lose contour')

		self.btn_BL.setMinimumWidth(40)
		self.btn_TL.setMinimumWidth(40)
		self.btn_BR.setMinimumWidth(40)
		self.btn_TR.setMinimumWidth(40)

		self.btn_close.setToolTip('Close selected contour')
		self.btn_BL.setToolTip('Set start point:\nBottom Left Node') 
		self.btn_TL.setToolTip('Set start point:\nTop Left Node') 
		self.btn_BR.setToolTip('Set start point:\nBottom Right Node') 
		self.btn_TR.setToolTip('Set start point:\nTop Right Node') 

		
		self.btn_BL.clicked.connect(lambda : self.setStart((0,0)))
		self.btn_TL.clicked.connect(lambda : self.setStart((0,1)))
		self.btn_BR.clicked.connect(lambda : self.setStart((1,0)))
		self.btn_TR.clicked.connect(lambda : self.setStart((1,1)))


		self.btn_close.clicked.connect(self.closeContour)

		self.addWidget(self.btn_BL, 0, 0, 1, 1)
		self.addWidget(self.btn_TL, 0, 1, 1, 1)
		self.addWidget(self.btn_BR, 0, 2, 1, 1)
		self.addWidget(self.btn_TR, 0, 3, 1, 1)
		self.addWidget(self.btn_close, 1, 0, 1, 4)

	def closeContour(self):
		glyph = eGlyph()
		wLayers = glyph._prepareLayers(pLayers)
		selection = glyph.selectedAtContours()

		for layerName in wLayers:
			contours = glyph.contours(layerName)

			for cID, nID in reversed(selection):
				if not contours[cID].closed: contours[cID].closed = True

		glyph.updateObject(glyph.fl, 'Close Contour @ %s.' %'; '.join(wLayers))
		glyph.update()

	def setStart(self, control=(0,0)):
		glyph = eGlyph()
		wLayers = glyph._prepareLayers(pLayers)
		
		for layerName in wLayers:
			contours = glyph.contours(layerName)

			for contour in contours:
				onNodes = [node for node in contour.nodes() if node.isOn]
				newFirstNode = sorted(onNodes, key=lambda node: ([node.x, -node.x][control[0]], [node.y, -node.y][control[1]]))[0]
				contour.setStartPoint(newFirstNode.index)

		glyph.updateObject(glyph.fl, 'Set Start Points @ %s.' %'; '.join(wLayers))
		glyph.update()



class convertHobby(QtGui.QHBoxLayout):
	# - Split/Break contour 
	def __init__(self):
		super(convertHobby, self).__init__()

		# -- Convert button
		self.btn_convertNode = QtGui.QPushButton('C&onvert')
		self.btn_convertNode.setToolTip('Convert/Unconvert selected curve node to Hobby Knot')
		self.btn_convertNode.clicked.connect(self.convertHobby)

		#self.btn_convertNode.setFixedWidth(80)

		# -- Close contour checkbox
		#self.chk_Safe = QtGui.QCheckBox('Safe')

		# -- Tension value (not implemented yet)
		#self.edt_tension = QtGui.QLineEdit('0.0')
		#self.edt_tension.setDisabled(True)    
				
		# -- Build
		self.addWidget(self.btn_convertNode)
		#self.addWidget(QtGui.QLabel('T:'), 1, 1)
		#self.addWidget(self.edt_tension, 1, 2)
		#self.addWidget(self.chk_Safe, 1, 3)

	def convertHobby(self):
		glyph = eGlyph()
		wLayers = glyph._prepareLayers(pLayers)
		selection = glyph.selected()

		for layerName in wLayers:
			pNodes = [glyph.nodes(layerName)[nID] for nID in selection]
			
			for node in pNodes:
				if not node.hobby:
					node.hobby = True
				else:
					node.hobby = False
				node.update()

		glyph.updateObject(glyph.fl, 'Convert to Hobby @ %s.' %'; '.join(wLayers))
		glyph.update()
		
		#fl6.Update(fl6.CurrentGlyph())

class advMovement(QtGui.QVBoxLayout):
	def __init__(self):
		super(advMovement, self).__init__()

		# - Init
		self.methodList = ['Move', 'Interpolated Move', 'Slanted Grid Move']
		
		# - Methods
		self.cmb_methodSelector = QtGui.QComboBox()
		self.cmb_methodSelector.addItems(self.methodList)
		self.cmb_methodSelector.setToolTip('Select movement method')
		self.addWidget(self.cmb_methodSelector)

		# - Arrow buttons
		self.lay_btn = QtGui.QGridLayout()
		
		self.btn_up = QtGui.QPushButton('Up')
		self.btn_down = QtGui.QPushButton('Down')
		self.btn_left = QtGui.QPushButton('Left')
		self.btn_right = QtGui.QPushButton('Right')
		
		self.btn_up.setMinimumWidth(80)
		self.btn_down.setMinimumWidth(80)
		self.btn_left.setMinimumWidth(80)
		self.btn_right.setMinimumWidth(80)
		
		self.btn_up.clicked.connect(self.onUp)
		self.btn_down.clicked.connect(self.onDown)
		self.btn_left.clicked.connect(self.onLeft)
		self.btn_right.clicked.connect(self.onRight)
		
		self.edt_offX = QtGui.QLineEdit('1.0')
		self.edt_offY = QtGui.QLineEdit('1.0')
		self.edt_offX.setToolTip('X offset')
		self.edt_offY.setToolTip('Y offset')

		self.lay_btn.addWidget(QtGui.QLabel('X:'), 0, 0, 1, 1)
		self.lay_btn.addWidget(self.edt_offX, 0, 1, 1, 1)
		self.lay_btn.addWidget(self.btn_up, 0, 2, 1, 2)
		self.lay_btn.addWidget(QtGui.QLabel('Y:'), 0, 4, 1, 1)
		self.lay_btn.addWidget(self.edt_offY, 0, 5, 1, 1)

		self.lay_btn.addWidget(self.btn_left, 1, 0, 1, 2)
		self.lay_btn.addWidget(self.btn_down, 1, 2, 1, 2)
		self.lay_btn.addWidget(self.btn_right, 1, 4, 1, 2)

		self.addLayout(self.lay_btn)

		
	def moveNodes(self, offset_x, offset_y, method):
		'''
		import sys        
		sys.stdout = open(r'd:\\stdout.log', 'w')
		sys.stderr = open(r'd:\\stderr.log', 'w')
		'''
		# - Init
		glyph = eGlyph()
		font = pFont()
		selectedNodes = glyph.selectedNodes()
		italic_angle = font.getItalicAngle()

		# - Process
		if method == self.methodList[0]:
			for node in selectedNodes:
				if node.isOn:
					node.smartMove(QtCore.QPointF(offset_x, offset_y))

		elif method == self.methodList[1]:
			for node in selectedNodes:
				wNode = eNode(node)
				wNode.interpMove(offset_x, offset_y)

		elif method == self.methodList[2]:
			if italic_angle != 0:
				for node in selectedNodes:
					wNode = eNode(node)
					print wNode
					wNode.slantMove(offset_x, offset_y, italic_angle)
			else:
				for node in selectedNodes:
					if node.isOn:
						node.smartMove(QtCore.QPointF(offset_x, offset_y))

		# - Set Undo
		glyph.updateObject(glyph.activeLayer(), '%s @ %s.' %(method, glyph.activeLayer().name), verbose=False)

		# - Finish it
		glyph.update()

	def onUp(self):
		self.moveNodes(.0, float(self.edt_offY.text), method=str(self.cmb_methodSelector.currentText))

	def onDown(self):
		self.moveNodes(.0, -float(self.edt_offY.text), method=str(self.cmb_methodSelector.currentText))
			
	def onLeft(self):
		self.moveNodes(-float(self.edt_offX.text), .0, method=str(self.cmb_methodSelector.currentText))
			
	def onRight(self):
		self.moveNodes(float(self.edt_offX.text), .0, method=str(self.cmb_methodSelector.currentText))

# - Tabs -------------------------------
class tool_tab(QtGui.QWidget):
	def __init__(self):
		super(tool_tab, self).__init__()

		# - Init
		layoutV = QtGui.QVBoxLayout()
		self.KeyboardOverride = False
		
		# - Build		
		layoutV.addWidget(QtGui.QLabel('Basic Operations'))
		layoutV.addLayout(basicOps())

		layoutV.addWidget(QtGui.QLabel('Align nodes'))
		layoutV.addLayout(alignNodes())

		layoutV.addWidget(QtGui.QLabel('Break/Knot Contour'))
		layoutV.addLayout(breakContour())

		layoutV.addWidget(QtGui.QLabel('Basic Contour Operations'))
		layoutV.addLayout(basicContour())

		#layoutV.addWidget(QtGui.QLabel('Convert to Hobby'))
		#layoutV.addLayout(convertHobby())    

		layoutV.addWidget(QtGui.QLabel('Movement'))
		self.advMovement = advMovement()
		layoutV.addLayout(self.advMovement)  

		# - Capture Kyaboard
		self.btn_capture = QtGui.QPushButton('Capture Keyboard')
		self.btn_capture.setCheckable(True)
		self.btn_capture.setToolTip('Click here to capture keyboard arrows input.\nNote:\n+10 SHIFT\n+100 CTRL\n Exit ESC')
		self.btn_capture.clicked.connect(self.captureKeyaboard)

		layoutV.addWidget(self.btn_capture)

		# - Build ---------------------------
		layoutV.addStretch()
		self.setLayout(layoutV)


	def keyPressEvent(self, eventQKeyEvent):
		
		
		#self.setFocus()
		key = eventQKeyEvent.key()
		modifier = int(eventQKeyEvent.modifiers())
		addon = .0
		
		if key == QtCore.Qt.Key_Escape:
			#self.close()
			self.releaseKeyboard()
			self.KeyboardOverride = False
			self.btn_capture.setChecked(False)
			self.btn_capture.setText('Capture Keyboard')
			
		# - Keyboard listener
		# -- Modifier addon
		if modifier == QtCore.Qt.ShiftModifier:
			addon = 10.0
		elif modifier == QtCore.Qt.ControlModifier:
			addon = 100.0
		else:
			addon = .0
		
		# -- Standard movement keys				
		if key == QtCore.Qt.Key_Up:
			shiftXY = (.0, float(self.advMovement.edt_offY.text) + addon)
		
		elif key == QtCore.Qt.Key_Down:
			shiftXY = (.0, -float(self.advMovement.edt_offY.text) - addon)
		
		elif key == QtCore.Qt.Key_Left:
			shiftXY = (-float(self.advMovement.edt_offX.text) - addon, .0)
		
		elif key == QtCore.Qt.Key_Right:
			shiftXY = (float(self.advMovement.edt_offX.text) + addon, .0)
		
		else:
			shiftXY = (.0,.0)

		# - Move
		self.advMovement.moveNodes(*shiftXY, method=str(self.advMovement.cmb_methodSelector.currentText))

	def captureKeyaboard(self):
		if not self.KeyboardOverride:
			self.KeyboardOverride = True
			self.btn_capture.setChecked(True)
			self.btn_capture.setText('Keyboard Capture Active. [ESC] Exit')
			self.grabKeyboard()
		else:
			self.KeyboardOverride = False
			self.btn_capture.setChecked(False)
			self.btn_capture.setText('Capture Keyboard')
			self.releaseKeyboard()
	

# - Test ----------------------
if __name__ == '__main__':
	test = tool_tab()
	test.setWindowTitle('%s %s' %(app_name, app_version))
	test.setGeometry(300, 300, 200, 400)
	test.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # Always on top!!
	
	test.show()