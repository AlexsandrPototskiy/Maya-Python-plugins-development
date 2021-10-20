"""
Asset Validation tool
Made By Alex Pototskyi

Tool was inpired by multiple issues that I strogle when was working as Techical Artist,
each time with new project we was needed to create anouther tool that will help to fix project needs with names, pivots, uv sets and etc.

Tool was designed as Flexible and Reusable, everyone who wants to improve it can do that.
You can implement your own ValidationRule and apply 'special case' to object.
All you have to do is to inherite from ValidationRule class implement 'apply_rule' function that takes Maya object as input.
See NameRule or UVSetRule as example.
Each Rule takes own data type NameRule takes list with names from data file, UVSetRule takes list of UV Set names etc.
"""
import json
import pymel.core as pm


# Main QT imports
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets, QtGui
import maya.OpenMayaUI as omui


'''
UI
'''
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
        content = self.__names_box.currentText()
        self.ON_RENAME_BTTN_CLICK.emit(content)

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
            name_item.setFlags(QtCore.Qt.ItemIsEnabled)

            self.__log_table.setItem(row, 0, name_item)
        
            # fill status columns
            column = 1
            statuses = data[itemKey]
            for status in statuses:

                widget_item = QtWidgets.QTableWidgetItem(status.status_msg)
                widget_item.setFlags(QtCore.Qt.ItemIsEnabled)

                if status.is_passed == False:
                    widget_item.setBackgroundColor(QtGui.QColor(128, 0 ,0))

                self.__log_table.setItem(row, column, widget_item)
                column += 1
            
            # go to next row
            row += 1
            
        self.__log_table.resizeColumnsToContents()

    def populate_rename_list(self, names):
        self.__names_box.clear()
        self.__names_box.addItems(names)


# Settings UI
class SettingsWindow(QtWidgets.QDialog):

    def __init__(self, window_parent):
        super(SettingsWindow, self).__init__(window_parent)

        self.setWindowTitle("Settings")
        self.setWindowFlags(QtCore.Qt.Tool)

        self.names_txt = QtWidgets.QPlainTextEdit("Intern, Break, Tire_FR, Bumper_L, Door_L, Door_R")
        self.uvs_text = QtWidgets.QPlainTextEdit("UVChannel_1, UVChannel_2")
        self.filters_txt = QtWidgets.QPlainTextEdit("camera, locator")
        self.save_bttn = QtWidgets.QPushButton("Save")

        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(self.names_txt)
        vlayout.addWidget(self.uvs_text)
        vlayout.addWidget(self.filters_txt)
        vlayout.addWidget(self.save_bttn)


'''
VALIDATION CONTROLLER
'''
# Validate given assets with different validation rules
class AssetValidator():
    
    def __init__(self, rules):
        self.__output_listners = {}
        self.__rules = rules
        self.__ignorable_types = []

    def set_filter(self, ignorable_types):
        self.__ignorable_types = ignorable_types

    def update_rules(self, rules):
        self.__rules = rules

    def do_validation(self):
        # check if any objects selected
        current_scene_objects = pm.selected()

        if len(current_scene_objects) < 1:
            # get current scene objects
            current_scene_objects = pm.ls(transforms=True)

        filtred_objects = []

        # filtering maya scene objects
        for scene_object in current_scene_objects:
            first_relative = pm.listRelatives(scene_object, ad = True)[0]
            if first_relative.nodeType() not in self.__ignorable_types:
                filtred_objects.append(scene_object)
        
        # do not validate anything if no objects is filtered
        if len(filtred_objects) < 1:
            print("[AssetValidator] No Objects in Scene")
            return

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
        self.__output_listners[listener_id] = listener


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


'''
VALIDATION RULES
'''
# Main Register function for validation logic
def get_validation_rules(configuration):
    rules = []
    rules.append(NameRule(configuration.get_names_configuration()))
    rules.append(UVSetRule(configuration.get_uv_configuration()))
    return rules


# Loading and Storing tool settings
class ToolConfigurationProvider():

    def __init__(self):
        self.__rules_configuration = RuleConfiguration()
        self.__filters = []
    
    def reload(self):
        # TODO: read data from .json file

        self.__rules_configuration.set_name_configuration([
        "Intern",
        "Break",
        "Tire_FR",
        "Bumper_L", 
        "Door_L",
        "Door_R"
        ])

        self.__rules_configuration.set_uv_sets_configuration(["UVChannel_1", "UVChannel_2"])

        self.__filters = ["camera"]
    
    def get_rules_configuration(self):
        return self.__rules_configuration

    def get_filters(self):
        return self.__filters

    def store_settings(self, names, uvs, filters):
        self.__rules_configuration.set_name_configuration(names)
        self.__rules_configuration.set_uv_sets_configuration(uvs)
        self.__filters = filters


# Rules Configuration Data Class
class RuleConfiguration():

    def __init__(self):
        self.__names = []
        self.__uvs = []

    def set_name_configuration(self, names):
        self.__names = names

    def set_uv_sets_configuration(self, uv_sets):
        self.__uvs = uv_sets

    def get_names_configuration(self):
        return self.__names

    def get_uv_configuration(self):
        return self.__uvs


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
        self.__names = config
           
    def apply_rule(self, scene_object):
        if scene_object.name() not in self.__names:
            return ValidationRuleStatus("Wrong Name", False)
        return ValidationRuleStatus("Ok", True)


# UV Set Validation Rules
class UVSetRule(object):

    def __init__(self, config):
        self.NAME = "UVSets Status"
        self.__settings = config
      
    def apply_rule(self, scene_object):

        all_relatives = pm.listRelatives(scene_object)
        shape = all_relatives[0]
        if shape.nodeType() != "mesh":
            print("Not Mesh: {0}".format(scene_object.name()))
            return ValidationRuleStatus("Not Mesh", True)
            
        object_uv_data = pm.polyUVSet(shape, query=True, allUVSets = True)

        if len(object_uv_data) > len(self.__settings):
            return ValidationRuleStatus("To Much UV Sets: {0}".format(len(object_uv_data)), False)
        
        count = 0
        for uv_set in object_uv_data:
            uv_name = self.__settings[count]
            if uv_set != uv_name:
                return ValidationRuleStatus('"{0}" not matching "{1}"'.format(uv_set, uv_name),False)
            count += 1

        return ValidationRuleStatus("Ok", True)


'''
ASSET VALIDATOR TOOL
'''
# Main Tool Logic
class AssetValidatorTool():

    # constucting and connecting all dependencies for tool
    def __init__(self):
        configuration_provider = ToolConfigurationProvider()
        configuration_provider.reload()
        
        rules_configuration = configuration_provider.get_rules_configuration()
        rules = get_validation_rules(rules_configuration)

        # main validator controller class
        validator = AssetValidator(rules)

        # pass validation filters to validator
        filters = configuration_provider.get_filters()
        validator.set_filter(filters)

        # creating window instance with Maya Window as Parent
        window = MainWindow(self.__create_columns(rules), get_main_window())

        # add names to ui drop box
        window.populate_rename_list(rules_configuration.get_names_configuration())

        # connection ui inputs and validation logic
        window.ON_VALIDATION_BTTN_CLICK.connect(validator.do_validation)
        window.ON_RENAME_BTTN_CLICK.connect(self.__rename)
        window.ON_SETTINGS_BTTN_CLICK.connect(self.__show_settings)
        window.ON_SELECT_ITEM_CLICK.connect(self.__select_item)

        # add listeners to validation logic output
        validator.add_listener(window.fill_ui_validation_log)

        # setup setting menu
        settings_ui = SettingsWindow(window)
        settings_ui.save_bttn.clicked.connect(self.__save_settings)
        settings_ui.names_txt.setPlainText(self.__list_to_string(rules_configuration.get_names_configuration()))
        settings_ui.uvs_text.setPlainText(self.__list_to_string(rules_configuration.get_uv_configuration()))
        settings_ui.filters_txt.setPlainText(self.__list_to_string(filters))

        self.__validator = validator
        self.__configuration_provider = configuration_provider
        self.__main_ui = window
        self.__settings_ui = settings_ui

    # main entering point
    def run(self):
        self.__main_ui.show()

    # construct string from list for setting menu
    def __list_to_string(self, input_list):
        string = ""

        for i in range(0, len(input_list)):
            string += input_list[i]
            if i + 1 < len(input_list):
               string += ", "

        return string

    # select given maya object by name
    def __select_item(self, object_name):
        print("[AssetValidator] Selecting {0}".format(object_name))
        pm.select(object_name)

    # rename seleted objects by given name
    def __rename(self, new_name):
        current_selected_list = pm.ls(selection=True)
        if len(current_selected_list) < 1:
            print("[AssetValidator] No Selection, please select at least one object to rename")
            return
        for selected_object in current_selected_list:
            selected_object.rename(new_name)

    # showing settings UI
    def __show_settings(self):
        self.__settings_ui.show()

    # tying to save new settings
    def __save_settings(self):
        names_input = self.__settings_ui.names_txt.toPlainText()
        uvs_input = self.__settings_ui.uvs_text.toPlainText()
        filters_input = self.__settings_ui.filters_txt.toPlainText()

        if self.__validate_string(names_input) == False:
            print("[AssetValidator] setting names has wrong syntax: {0}".format(names_input))
            return

        if self.__validate_string(uvs_input) == False:
            print("[AssetValidator] setting uvs has wrong syntax: {0}".format(uvs_input))
            return

        names = self.__construct_list_from_string(names_input)
        uvs = self.__construct_list_from_string(uvs_input)

        filters = []
        if self.__validate_string(filters_input):
            filters = self.__construct_list_from_string(filters_input)

        # storing new settings to config file
        self.__configuration_provider.store_settings(names, uvs, filters)

        # configuring rules
        rules_config = self.__configuration_provider.get_rules_configuration()
        rules = get_validation_rules(rules_config)

        # updating UI, Validator
        self.__validator.update_rules(rules)
        self.__validator.set_filter(self.__configuration_provider.get_filters())
        self.__main_ui.populate_rename_list(rules_config.get_names_configuration())

        # closing setting window
        self.__settings_ui.close()

    # convert string to list[]
    def __construct_list_from_string(self, input_str):
        return input_str.split(', ')

    # validate given string for errors
    def __validate_string(self, string):
        if not string:
            return False

        for symbal in string:
            if symbal in ["#", "*", "!", "$", "%"]:
                return False

        return True

    # create column names list from rules
    def __create_columns(self, rules):
        columns = ["Object Name"]
        for r in rules:
            columns.append(r.NAME)
        return columns


if __name__ == "__main__":
    tool = AssetValidatorTool()
    tool.run()
