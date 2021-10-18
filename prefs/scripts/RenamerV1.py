"""
Asset Validation tool
Made By Alex Pototskyi

Tool was inpired by multiple issues that I strogle when was working as Techical Artist,
each time with new project we was needed to create anouther tool that will help to fix project needs with names, pivots, uv sets and etc.

Tool was designed as Flexible and Reusable, everyone who wants to improve it can do that.
You can implement your own ValidationRule and apply 'special case' to object.
All you have to do is to inherite from ValidationRule class implement 'apply_rule' function that takes Maya object as input.
See NameRule or UVSetRule as example.
"""
# pyMel imports
import pymel.core as pm

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

	def __init__(self, columns_names, window_parent = None):
		super(MainWindow, self).__init__(window_parent)
		self.setWindowFlags(QtCore.Qt.Tool)
		self.__build_ui(columns_names)

	def __build_ui(self, columns_names):
		#setting title
		self.setWindowTitle("Asset Validator")
		
		# main windoww grp
		app_layout = QtWidgets.QVBoxLayout(self)
		
		# creating validation layout
		validation_layout = QtWidgets.QVBoxLayout()
		self.__validate_bttn = QtWidgets.QPushButton("Validate")
		self.__validate_bttn.clicked.connect(self.__validate_bttn_slot)
		self.__log_table = QtWidgets.QTableWidget()
		
		self.__log_table.setColumnCount(len(columns_names))
		self.__log_table.setHorizontalHeaderLabels(columns_names)

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
		data = {}
		data = log.get_log_dict()
		
		self.__log_table.setRowCount(len(data))
		
		row = 0
		for itemKey in data:

			# fill first column with object name
			self.__log_table.setItem(row, 0, QtWidgets.QTableWidgetItem(itemKey))
		
			# fill status columns
			column = 1
			statuses = data[itemKey]
			for status in statuses:
				self.__log_table.setItem(row, column, QtWidgets.QTableWidgetItem(status.status_msg))
				column += 1
			
			# go to next row
			row += 1
			
		self.__log_table.resizeRowsToContents()
	

# Core Data Classes
# Validation log data class
class ValidationLog():
	def __init__(self):
		self.__current_log = {}
	
	# adding log item
	def add_log_item(self, key, value):
		self.__current_log[key] = value
	
	# get all log data
	def get_log_dict(self):
		return self.__current_log


# Core Tool Configuration provider
# Loading and Storing tool settings
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
# Validate given assets with different validation rules
class AssetValidator():
	
	def __init__(self, configuration_getter):
		
		self.__configuration_getter = configuration_getter
		self.__configuration = self.__read_config_file()		
		
		self.__output_listners = {}
		self.__register_rules()


	# TODO: think how to register different rules in validator
	def __register_rules(self):
		self.__rules = []
		# create rules
		names_rule = NameRule(self.__configuration)
		uvSet_rule = UVSetRule("")

		# add rules to rules list
		self.__rules.append(names_rule)
		self.__rules.append(uvSet_rule)
	
	
	def get_rules(self):
		return self.__rules

	def do_validation(self):
		# get current scene objects
		current_scene_objects = pm.ls(geometry=True)
		
		# shape_suffix to remove from shape node
		shape_suffix = "Shape"
		
		# current geometry list
		filtred_objects = []
		
		# removing suffix
		for scene_object in current_scene_objects:
			filtred_objects.append(scene_object.replace(shape_suffix, ''))
		
		# validating
		validation_data = self.__validate(filtred_objects, self.__configuration)
		self.__notify_listners(validation_data)
	
	# read external configuration file
	def __read_config_file(self):
		return self.__configuration_getter()

	# validate given object base on configuration
	def __validate(self, scene_objects, configuration):
		
		data = ValidationLog()
		# apply rules for each scene object
		for s in scene_objects:
			statuses = []
			for rule in self.__rules:
				statuses.append(rule.apply_rule(s))
				data.add_log_item(s, statuses)
				
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


# Validation Status Data Class
# it tells what current status, is test passed and etc.
class ValidationRuleStatus():
	def __init__(self, status_msg, is_passed):
		self.status_msg = status_msg
		self.is_passed = is_passed

# Names Validation Rule
class NameRule():
	def __init__(self, config):
		self.NAME = "Name Status"
		self.set_configuration(config)
	
	def set_configuration(self, config):
		self.__names = config
		
	def apply_rule(self, object_name):
		if object_name not in self.__names:
			return ValidationRuleStatus("Wrong Name", False)
		return ValidationRuleStatus("Ok", True)

# UV Set Validation Rules
class UVSetRule():
	def __init__(self, config):
		self.NAME = "UVSets Status"
		self.set_configuration(config)
	
	def set_configuration(self, config):
		self.__settings = config
	
	def apply_rule(self, maya_object):
		return ValidationRuleStatus("To Much UV Sets", False)



# Core ReNaming Logic
# Main entry point of Renamer
def rename_by_name(new_name):
	
	current_selected_list = pm.ls(selection=True)
	
	if len(current_selected_list) < 1:
		print("No Selection, please select at least one object to rename")
		return
	
	for selected_object in current_selected_list:
		print("{0} -> {1}".format("current_test_name", new_name))
		pm.rename(selected_object, new_name)


# Connect UI with logical part and Run Tool
if __name__ == "__main__":

	# main configuration
	configuration_provider = ToolConfigurationProvider()
	configuration_provider.reload()
	
	# main validator class
	validator = AssetValidator(configuration_provider.get_configuration)
	
	# construct columns for UI
	# TODO: move this part to configuration file
	# user must select what he dont want to validate
	columns = ["Object Name"]
	for r in validator.get_rules():
		columns.append(r.NAME)
		
	# crating window instance with Maya Window as Parent
	window = MainWindow(columns, get_main_window())
		
	# connection ui inputs and validation logic
	window.ON_VALIDATION_BTTN_CLICK.connect(validator.do_validation)
	window.ON_RENAME_BTTN_CLICK.connect(rename_by_name)
	
	validator.add_listener(window.fill_ui_validation_log)
	
	# starting tool
	window.show()