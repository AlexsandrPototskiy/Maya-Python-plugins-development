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

	def __init__(self, columns_names, window_parent = None):
		super(MainWindow, self).__init__(window_parent)
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
			# fill first row
			self.__log_table.setItem(row, 0, QtWidgets.QTableWidgetItem(itemKey))
			
			statuses = data[itemKey]
			self.__log_table.setColumnCount(len(statuses) + 1)
			# fill other rows
			for status in statuses:
				self.__log_table.setItem(row, 1, QtWidgets.QTableWidgetItem(status.status_msg))
			
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


class ValidationRuleStatus():
	def __init__(self, status_msg, is_passed):
		self.status_msg = status_msg
		self.is_passed = is_passed


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
		
		self.__configuration_getter = configuration_getter
		self.__configuration = self.__read_config_file()		
		
		self.__output_listners = {}
		
		# setup validation rules
		self.__rules = []
		self.__rules.append(NameRule(self.__configuration))
	
	
	def get_rules(self):
		return self.__rules


	def do_validation(self):
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
			for rule in self.__rules:
				statuses = []
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


# base validation rule		
class ValidationRule():
	NAME = "Abstract Rule"
	def apply_rule(self, object_for_validation):
		pass


# names validation
class NameRule(ValidationRule):
	
	def __init__(self, names_from_configuration):
		self.NAME = "Name Status"
		self.__names = names_from_configuration
		
	def apply_rule(self, object_name):
		
		satus_mgs = ""
		is_passed = False
		
		if object_name not in self.__names:
			satus_mgs = "Wrong Name"
			is_passed = False
		
		satus_mgs = "OK!"
		is_passed = True
		
		status = ValidationRuleStatus(satus_mgs, is_passed)
		return status


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



# Connect UI with logical part and Run Tool
if __name__ == "__main__":
	
	# main configuration
	configuration_provider = ToolConfigurationProvider()
	configuration_provider.reload()
	
	validator = AssetValidator(configuration_provider.get_configuration)
	
	# construct columns
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
