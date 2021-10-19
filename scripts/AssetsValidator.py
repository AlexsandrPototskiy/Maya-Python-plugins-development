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


# Main UI
class MainWindow(QtWidgets.QDialog):
    
    ON_VALIDATION_BTTN_CLICK = QtCore.Signal()
    ON_RENAME_BTTN_CLICK = QtCore.Signal(str)
    ON_SELECT_ITEM_CLICK = QtCore.Signal(str)
    ON_SETTINGS_BTTN_CLICK = QtCore.Signal(QtWidgets.QDialog)

    def __init__(self, columns_names, window_parent = None):
        super(MainWindow, self).__init__(window_parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.__build_ui(columns_names)

    def __build_ui(self, columns_names):
        #setting title
        self.setWindowTitle("Asset Validator")
        
        # main windoww grp
        app_layout = QtWidgets.QVBoxLayout(self)

        # creating settings layout
        settings_layout = QtWidgets.QVBoxLayout()
        self.__settings_bttn = QtWidgets.QPushButton("Settings")
        self.__settings_bttn.clicked.connect(self.__settings_bttn_slot)
        settings_layout.addWidget(self.__settings_bttn)
        app_layout.addLayout(settings_layout)

        # creating validation layout
        validation_layout = QtWidgets.QVBoxLayout()
        self.__validate_bttn = QtWidgets.QPushButton("Validate")
        self.__validate_bttn.clicked.connect(self.__validate_bttn_slot)
        self.__log_table = QtWidgets.QTableWidget()
        self.__log_table.setColumnCount(len(columns_names))
        self.__log_table.setHorizontalHeaderLabels(columns_names)
        self.__log_table.clicked.connect(self.__on_item_clicked)

        validation_layout.addWidget(QtWidgets.QLabel("Validate Objects Names:"))
        validation_layout.addWidget(self.__validate_bttn)
        validation_layout.addWidget(QtWidgets.QLabel("Status Log:"))
        validation_layout.addWidget(self.__log_table)
        app_layout.addLayout(validation_layout)
        
        # creating renamer layout
        renamer_layout = QtWidgets.QVBoxLayout()
        renamer_layout.addWidget(QtWidgets.QLabel("Rename Selected Object With Name:"))
        self.__names_box = QtWidgets.QComboBox()
        self.__rename_btn = QtWidgets.QPushButton("Rename Selected")
        self.__rename_btn.clicked.connect(self.__rename_bttn_slot)
        renamer_layout.addWidget(self.__names_box)
        renamer_layout.addWidget(self.__rename_btn)
        app_layout.addLayout(renamer_layout)

    def __validate_bttn_slot(self):
        self.ON_VALIDATION_BTTN_CLICK.emit()
    
    def __rename_bttn_slot(self):
        self.ON_RENAME_BTTN_CLICK.emit("test_name_from_combo_box")

    def __settings_bttn_slot(self):
        self.ON_SETTINGS_BTTN_CLICK.emit(self)

    def __on_item_clicked(self, item):

        currentItem = self.__log_table.item(item.row(), 0)
        data = currentItem.data(0)

        print(data)
        self.ON_SELECT_ITEM_CLICK.emit(data)
    
    # fill ui log with given ValidationLog
    def fill_ui_validation_log(self, log):
        data = {}
        data = log.get_log_dict()
        
        self.__log_table.setRowCount(len(data))
        
        row = 0
        for itemKey in data:

            # fill first column with object name
            name_item = QtWidgets.QTableWidgetItem(itemKey)
            # name_item.setFlags(QtCore.Qt.ItemIsSelectable)
            name_item.setFlags(QtCore.Qt.ItemIsEnabled)

            self.__log_table.setItem(row, 0, name_item)
        
            # fill status columns
            column = 1
            statuses = data[itemKey]
            for status in statuses:

                widget_item = QtWidgets.QTableWidgetItem(status.status_msg)
                widget_item.setFlags(QtCore.Qt.ItemIsSelectable)

                self.__log_table.setItem(row, column, widget_item)
                column += 1
            
            # go to next row
            row += 1
            
        self.__log_table.resizeColumnsToContents()

    def populate_rename_list(self, names):
        self.__names_box.addItems(names)


# Settings UI
class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, window_parent):
        super(SettingsWindow, self).__init__(window_parent)
        self.setWindowFlags(QtCore.Qt.Tool)
    

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
        self.__cached_configuration = [
        "Intern",
        "Break",
        "Tire_FR",
        "Bumper_L"]
    
    # get cached configuration
    def get_configuration(self):
        return self.__cached_configuration


# Core validation logic
# Validate given assets with different validation rules
class AssetValidator():
    
    def __init__(self, rules):
        self.__output_listners = {}
        self.__rules = rules

    def do_validation(self):
        # get current scene objects
        current_scene_objects = pm.ls(transforms=True)

        ignorable_types = ["camera"]

        filtred_objects = []

        # filtering maya scene objects
        for scene_object in current_scene_objects:
            first_relative = pm.listRelatives(scene_object, ad = True)[0]
            if pm.nodeType(first_relative, q=True) not in ignorable_types:
                filtred_objects.append(scene_object)
                
        print(filtred_objects)
        # validating
        validation_data = self.__validate(filtred_objects)
        self.__notify_listners(validation_data)
    
    # validate given object
    def __validate(self, scene_objects):
        
        data = ValidationLog()
        # apply rules for each scene object
        for s in scene_objects:
            statuses = []
            for rule in self.__rules:
                statuses.append(rule.apply_rule(s))
                data.add_log_item(s.name(), statuses)
                
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


# Main Register function for validation logic
def get_validation_rules(configuration):
    print("[Validation Rules] Registering Rules")
    rules = []
    rules.append(NameRule(configuration))
    rules.append(UVSetRule(configuration))
    return rules


# Validation Status Data Class
# it tells what current status, is test passed and etc.
class ValidationRuleStatus():
    def __init__(self, status_msg, is_passed):
        self.status_msg = status_msg
        self.is_passed = is_passed


# Names Validation Rule
class NameRule(object):

    def __init__(self, config):
        self.NAME = "Name Status"
        self.set_configuration(config)
    
    def set_configuration(self, config):
        self.__names = config
        
    def apply_rule(self, scene_object):
        if scene_object.name() not in self.__names:
            return ValidationRuleStatus("Wrong Name", False)
        return ValidationRuleStatus("Ok", True)


# UV Set Validation Rules
class UVSetRule(object):
    def __init__(self, config):
        self.NAME = "UVSets Status"
        self.set_configuration(config)
    
    def set_configuration(self, config):
        self.__settings = config
    
    def apply_rule(self, scene_object):

        all_relatives = pm.listRelatives(scene_object)
        shape = all_relatives[0]
        if pm.nodeType(shape, q = True) != "mesh":
            print("Not Mesh: {0}".format(scene_object.name()))
            return ValidationRuleStatus("Not Mesh", True)
            
        object_uv_data = pm.polyUVSet(shape, query=True, allUVSets = True)

        #TODO: take this variables from settings
        uv_name = "UVChannel_"
        uv_sets_max_amount = 2
        starts_from = 1

        if len(object_uv_data) > uv_sets_max_amount:
            return ValidationRuleStatus("To Much UV Sets {0}".format(len(object_uv_data)), False)
        
        count = starts_from
        for uv_set in object_uv_data:
            tmp_name = uv_name + str(count)
            if uv_set != tmp_name:
                return ValidationRuleStatus("UV Set: {0} dont Match Settings Rule {1}".format(uv_set, tmp_name),False)
            count += 1

        return ValidationRuleStatus("Ok", True)


# Core ReNaming Logic
# Main entry point of Renamer
def rename_by_name(new_name):
    current_selected_list = pm.ls(selection=True)
    if len(current_selected_list) < 1:
        print("No Selection, please select at least one object to rename")
        return

    for selected_object in current_selected_list:
        print("{0} -> {1}".format("current_test_name", new_name))
        selected_object.rename(new_name)


def create_settings_window(settings_parent):
    ui = SettingsWindow(settings_parent)
    ui.show()


# select object in scene
def select_item(object_name):
    print("Selecting {0}".format(object_name))
    pm.select(object_name)


# construct UI columns base on rules name
def get_columns(rules):
    columns = ["Object Name"]
    for r in rules:
        columns.append(r.NAME)
    return columns


# Connect UI with logical part and Run Tool
if __name__ == "__main__":

    # main configuration
    configuration_provider = ToolConfigurationProvider()
    configuration_provider.reload()
    
    configuration = configuration_provider.get_configuration()
    rules = get_validation_rules(configuration)

    # main validator controller class
    validator = AssetValidator(rules)
        
    # crating window instance with Maya Window as Parent
    window = MainWindow(get_columns(rules), get_main_window())

    # connection ui inputs and validation logic
    window.ON_VALIDATION_BTTN_CLICK.connect(validator.do_validation)
    window.ON_RENAME_BTTN_CLICK.connect(rename_by_name)
    window.ON_SETTINGS_BTTN_CLICK.connect(create_settings_window)
    window.ON_SELECT_ITEM_CLICK.connect(select_item)

    validator.add_listener(window.fill_ui_validation_log)

    window.populate_rename_list(configuration)

    # starting tool
    window.show()
