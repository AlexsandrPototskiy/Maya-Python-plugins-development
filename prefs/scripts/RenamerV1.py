import maya.cmds as cmds

# Main QT imports
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets
import maya.OpenMayaUI as omui


# Core UI Implementation
# Get instance of Maya main window via  wrapInstance and Maya API
def get_main_window():
	main = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main), QtWidgets.QWidget)

# UI
class MainWindow(QtWidgets.QDialog):
	
	ON_VALIDATION_BTTN_CLICK = QtCore.Signal()
	ON_RENAME_BTTN_CLICK = QtCore.Signal(str)

	
	def __init__(self, window_parent = None):
		super(MainWindow, self).__init__(window_parent)
		self.__build_ui()

	
	def __build_ui(self):
		#setting title
		self.setWindowTitle("Asset Validator")
		
		# main windoww grp
		app_layout = QtWidgets.QVBoxLayout(self)
		
		# creating validation layout
		validation_layout = QtWidgets.QHBoxLayout()
		self.__validate_bttn = QtWidgets.QPushButton("Validate Scene")
		self.__validate_bttn.clicked.connect(self.__validate_btton_slot)
		validation_layout.addWidget(self.__validate_bttn)
		
		# adding to main grp
		app_layout.addLayout(validation_layout)
		
		# creating renamer layout
		renamer_layout = QtWidgets.QVBoxLayout()
		renamer_layout.addWidget(QtWidgets.QLabel("Rename Selected Object With Name:"))
		self.__names_box = QtWidgets.QComboBox()
		self.__rename_btn = QtWidgets.QPushButton("Rename Selected")
		self.__rename_btn.clicked.connect(self.__rename_bttn_slot)
		renamer_layout.addWidget(self.__names_box)
		renamer_layout.addWidget(self.__rename_btn)
		
		# adding to main grp
		app_layout.addLayout(renamer_layout)
		
	def __validate_btton_slot(self):
		self.ON_VALIDATION_BTTN_CLICK.emit()
	
	def __rename_bttn_slot(self):
		self.ON_RENAME_BTTN_CLICK.emit("test_name_from_combo_box")
	
	def fix_ui_validation_log(log):
		print(log)
		


# Core validation logic
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
	not_fount_objects = []
	other_objects = []
	
	for c in configuration:
		# adding to log objects that was not fount in scene
		if c not in scene_objects:
			not_fount_objects.append(c)
		
		# adding to log objects that are not listed in configuration
		for o in scene_objects:
			if o not in configuration:
				other_objects.append(o)
	
	# printing log list for not fount objects
	if len(not_fount_objects) > 0:
		print "Not Founded Objects in scene"
		for n in not_fount_objects:
			print n
	
	# printing log list for other objects
	if len(other_objects) > 0:
		print "Other Objects was located - consider to delete them from scene"
		for o in other_objects:
			print o



# Core ReNaming Logic
# Main entry point of Renamer
def rename_by_name(new_name):
	print("{0} -> {1}".format("current_test_name", new_name))



# Connect UI with logical part and run Tool
if __name__ == "__main__":
	# crating window instance with Maya Window as Parent
	w = MainWindow(get_main_window())
	
	# connection ui inputs and validation logic
	w.ON_VALIDATION_BTTN_CLICK.connect(validate_scene_objects)
	w.ON_RENAME_BTTN_CLICK.connect(rename_by_name)
	
	# starting tool
	w.show()
