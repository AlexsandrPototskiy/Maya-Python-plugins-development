import maya.cmds as cmds
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets
import maya.OpenMayaUI as omui


# get instance of Maya main window via  wrapInstance and Maya API
def get_main_window():
	main = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main), QtWidgets.QWidget)


# base main UI
class MainWindow(QtWidgets.QDialog):
	
	def __init__(self, window_parent = None):
		super(MainWindow, self).__init__(window_parent)


# main entry point of validation
def validate_scene_objects():
	# reading configuration 
	configuration = read_config_file()
		
	# get current scene objects
	current_scene_objects = cmds.ls(geometry=True)
	
	# shape_suffix to remove from shape node
	shape_suffix = "Shape"
	
	# current geometry list
	filtred_objects = []
	
	# removing suffix
	for scene_object in current_scene_objects:
		filtred_objects.append(scene_object.replace(shape_suffix, ''))
	
	# validating
	validate(filtred_objects, configuration)
	

# read external configuration file
def read_config_file():
	return ["Intern", "Break", "Apple"]
	

# validate given object base on configuration
def validate(scene_objects, configuration):
	not_founded_objects = []
	strange_objects = []
	
	for c in configuration:
		if c not in scene_objects:
			not_founded_objects.append(c)
		
		for o in scene_objects:
			if o not in configuration:
				strange_objects.append(o)
	
	if len(not_founded_objects) > 0:
		print "Not Founded Objects in scene"
		for n in not_founded_objects:
			print n
			
	if len(strange_objects) > 0:
		print "Other Objects was located - consider to delete them from scene"
		for o in strange_objects:
			print o
	
			
validate_scene_objects()
w = MainWindow(get_main_window())
w.show()
