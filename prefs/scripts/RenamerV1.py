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
		validation_layout = QtWidgets.QVBoxLayout()
		self.__validate_bttn = QtWidgets.QPushButton("Validate")
		self.__validate_bttn.clicked.connect(self.__validate_bttn_slot)
		self.__log_table = QtWidgets.QTableWidget()
		self.__log_table.setColumnCount(2)
		self.__log_table.setHorizontalHeaderLabels(["Object Name", "Validation Status"])

		validation_layout.addWidget(QtWidgets.QLabel("Validate Objects Names:"))
		validation_layout.addWidget(self.__validate_bttn)
		validation_layout.addWidget(QtWidgets.QLabel("Status Log:"))
		validation_layout.addWidget(self.__log_table)
		
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

	def __validate_bttn_slot(self):
		self.ON_VALIDATION_BTTN_CLICK.emit()
	
	def __rename_bttn_slot(self):
		self.ON_RENAME_BTTN_CLICK.emit("test_name_from_combo_box")
	
	# fill ui log with given ValidationLog
	def fill_ui_validation_log(self, log):
		data = log.get_log_dict()
		
		self.__log_table.setRowCount(len(data))	
		
		row = 0
		for itemKey in data:
			self.__log_table.setItem(row, 0, QtWidgets.QTableWidgetItem(itemKey))
			self.__log_table.setItem(row, 1, QtWidgets.QTableWidgetItem(data[itemKey]))
			row += 1
		
		self.__log_table.resizeRowsToContents()

	

# Core Data Classes
# Validation log data class
class ValidationLog():
	def __init__(self):
		self.__current_log = {}
	
	# adding log item
	def add_log_item(self, key, value):
		print("Adding Log: {0} -> {1}".format(key, value))
		# TODO: add validation for exsiting keys
		self.__current_log[key] = value
	
	# get all log data
	def get_log_dict(self):
		return self.__current_log


# Core Tool Configuration provider
class ToolConfigurationProvider():
	def __init__(self):
		self.__cached_configuration = []
	
	def reload(self):
		# TODO: read data from file
		self.__cached_configuration = ["Intern", "Break", "Apple", "Tire_FR", "Banana"]
	
	# get cached configuration
	def get_configuration(self):
		return self.__cached_configuration


# Core validation logic
class AssetValidator():
	
	def __init__(self, configuration_getter):
		self.__output_listners = {}
		self.__configuration_getter = configuration_getter

	def validate_names(self):
		# reading configuration 
		configuration = self.__read_config_file()
			
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
		validation_data = self.__validate(filtred_objects, configuration)
		
		self.__notify_listners(validation_data)
	
	# read external configuration file
	def __read_config_file(self):
		return self.__configuration_getter()

	# validate given object base on configuration
	def __validate(self, scene_objects, configuration):
		
		data = ValidationLog()
		
		for c in configuration:
			# adding to log objects that was not fount in scene
			if c not in scene_objects:
				validation_status = "Missing"
			else:
				validation_status = "OK!"
			
			data.add_log_item(c, validation_status)
				
		return data
	
	# notify all listners with current log
	def __notify_listners(self, log):
		for listenerKey in self.__output_listners:
			self.__output_listners[listenerKey](log)
	
	# add log output listner
	def add_listener(self, listener):
		listener_id = id(listener)
		print("Adding Listner with ID: {0}".format(listener_id))
		self.__output_listners[listener_id] = listener


# Core ReNaming Logic
# Main entry point of Renamer
def rename_by_name(new_name):
	current_selected_list = cmds.ls(selection=True)
	
	if len(current_selected_list) < 1:
		print("No Selection, please select at least one object to rename")
		return
	
	for selected_object in current_selected_list:
		print("{0} -> {1}".format("current_test_name", new_name))
		cmds.rename(selected_object, new_name)


# Connect UI with logical part and run Tool
if __name__ == "__main__":
	# crating window instance with Maya Window as Parent
	w = MainWindow(get_main_window())
	
	# main configuration
	configuration_provider = ToolConfigurationProvider()
	configuration_provider.reload()
	
	validator = AssetValidator(configuration_provider.get_configuration)
	
	# connection ui inputs and validation logic
	w.ON_VALIDATION_BTTN_CLICK.connect(validator.validate_names)
	w.ON_RENAME_BTTN_CLICK.connect(rename_by_name)
	
	validator.add_listener(w.fill_ui_validation_log)
	
	# starting tool
	w.show()
