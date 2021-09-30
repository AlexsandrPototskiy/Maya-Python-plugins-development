import os
import json
import sys
from maya import cmds
import maya.OpenMayaUI as opui
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

data_name = 'library_data'
main_key = 'library'
creating_key = 'creation_date'
name_key = 'name'
path_key = 'path'


def create_directory(directory):
    print 'Directory -- %s' % directory
    if not os.path.exists(directory):
        os.mkdir(directory)
        print "Created directory"
        print directory
    else:
        print "Directory is already exist"


def get_maya_main_window():
    main_window = opui.MQtUtil_mainWindow()
    return wrapInstance(long(main_window), QWidget)


def get_info_file(directory):
    return os.path.join(directory, '%s.json' % data_name)


class Model(object):
    def __init__(self, name, path, icon):
        self.name = name
        self.path = path
        self.icon = icon


class UiModel(object):
    def __init__(self):
        self.__models = []

    def add_item(self, name, path, icon):
        m = Model(name, path, icon)
        self.__models.append(m)

    def get_items(self):
        return self.__models


class MainWindowUI(QDialog):
    on_path_changed = Signal(str)
    on_save_notification = Signal(str)
    on_content_populate = Signal()
    on_refresh_notification = Signal()

    save_item_slot = Slot(str)

    __icon_size = 64
    __icon_padding = 12
    __current_selection_key = ""
    __default_icon = ""

    def __init__(self, parent, default_icon):
        super(MainWindowUI, self).__init__(parent)
        self.__default_icon = default_icon
        self.__build_ui()
        self.__bind_user_inputs()

    def __build_ui(self):
        self.setWindowTitle("Content Provider")

        # create main vertical parent
        vertical_layout = QVBoxLayout(self)

        # select path ui
        select_path_widget = QWidget()
        path_layout = QHBoxLayout(select_path_widget)
        path_description = QLabel('Path:')

        self.__path_field = QLabel("empty directory")

        self.__select_path_button = QPushButton('Select Catalog Path')
        path_layout.addWidget(path_description)
        path_layout.addWidget(self.__path_field)
        path_layout.addWidget(self.__select_path_button)
        vertical_layout.addWidget(select_path_widget)

        # build save UI
        save_widget = QWidget()
        save_layout = QHBoxLayout(save_widget)
        self.__save_name_box = QLineEdit()
        save_layout.addWidget(self.__save_name_box)
        self.__save_button = QPushButton("Save Item")
        save_layout.addWidget(self.__save_button)
        vertical_layout.addWidget(save_widget)

        # build list UI
        self.__list_widget = QListWidget()
        vertical_layout.addWidget(self.__list_widget)

        # setup list ui appearance
        self.__list_widget.setViewMode(QListWidget.IconMode)
        self.__list_widget.setIconSize(QSize(self.__icon_size, self.__icon_size))
        self.__list_widget.setResizeMode(QListWidget.Adjust)
        size_with_padding = self.__icon_size + self.__icon_padding
        self.__list_widget.setGridSize(QSize(size_with_padding, size_with_padding))

        # build load UI
        load_widget = QWidget()
        load_layout = QHBoxLayout(load_widget)
        self.__import_button = QPushButton("Import Selected!")
        load_layout.addWidget(self.__import_button)
        self.__refresh_button = QPushButton("Refresh Content")
        load_layout.addWidget(self.__refresh_button)
        vertical_layout.addWidget(load_widget)

    def __bind_user_inputs(self):
        self.__import_button.clicked.connect(self.__on_import_clicked)
        self.__refresh_button.clicked.connect(self.__on_refresh_clicked)
        self.__save_button.clicked.connect(self.__save)
        self.__list_widget.itemClicked.connect(self.__set_selection)
        self.__select_path_button.clicked.connect(self.__on_path_selection_press)

    def __on_import_clicked(self):
        if self.__current_selection_key == "":
            print "Please select item"
            return

        print "Import Button Clicked %s" % self.__current_selection_key
        # self.__library.load(self.__current_selection_key)

    def __on_refresh_clicked(self):
        print "Refresh Button Clicked"
        self.on_refresh_notification.emit()

    def __save(self):
        item_name = self.__save_name_box.text()
        self.on_save_notification.emit(item_name)

    def __set_selection(self, item):
        self.__current_selection_key = item.text()
        print '%s was selected' % self.__current_selection_key

    def __on_path_selection_press(self):
        path = QFileDialog().getExistingDirectory()
        self.on_path_changed.emit(path)
        self.__path_field.setText(path)

    def fill_content(self, model):
        self.__list_widget.clear()
        data = model.get_items()
        for i in range(0, len(data)):
            list_item = QListWidgetItem(data[i].name)
            icon = QIcon(data[i].icon)
            list_item.setIcon(icon)
            self.__list_widget.addItem(list_item)


class Controller:
    def __init__(self, directory):
        self._library = {main_key: [], creating_key: []}
        self._directory = directory

    def is_item_exist(self, item_name):
        print "Doing Check {}".format(item_name)
        self.load_all_data()
        data = self.get_content_data()
        models = data.get_items()
        for m in models:
            if m.name == item_name:
                return True
        return False

    def save(self, name):
        create_directory(self._directory)
        file_name = '%s.ma' % name
        path = os.path.join(self._directory, file_name)
        #  check if any object selected
        is_any_selection = cmds.ls(selection=True)
        # if any object selected do  export selection, if no do save scene
        cmds.file(rename=path)
        if is_any_selection:
            print "Do Save Selection"
            cmds.file(exportSelected=True, type='mayaAscii', force=True)
        else:
            print "Save all Scene"
            cmds.file(save=True, type='mayaAscii', force=True)
        self.__write_to_data(name, path)
        self.__read_data()

    def load(self, name):
        info_file = os.path.join(self._directory, '%s.json' % data_name)
        if not os.path.exists(info_file):
            print "File does not exist"
            return
        self.__read_data()
        objects_library = [self._library[main_key]]
        has_match = False
        for collection in objects_library:
            # validate type of collection
            if not isinstance(collection, list):
                print 'wrong data type'
                print type(collection)
                continue
            for item in collection:
                # validate type of item
                if not isinstance(item, dict):
                    print 'wrong data type'
                    print type(item)
                    continue
                # check if json contains 'name' key
                if name_key not in item:
                    continue
                # check if json contains record for requested name
                if item[name_key] == name:
                    has_match = True
                    path = item[path_key]
                    cmds.file(path, i=True, usingNamespaces=False)
                    break
        if not has_match:
            print "No Data for key: %s" % name
            return

    def load_all_data(self):
        self.__read_data()

    def get_content_data(self):
        model = UiModel()
        for items in self._library[main_key]:
            model.add_item(items[name_key], items[path_key], "")
        return model

    def change_current_directory(self, directory):
        self._directory = directory

    def __create_empty_file(self, path):
        empty_data = {
            main_key: [],
            creating_key: []
        }
        with open(path, 'w') as f:
            json.dump(empty_data, f, indent=2)

    def __write_to_data(self, name, path):
        info_file = get_info_file(self._directory)
        # create an empty file if current doesnt exist
        if not os.path.exists(info_file):
            self.__create_empty_file(info_file)
        else:
            self.__read_data()
        info = {name_key: name,
                path_key: path}
        library = self._library[main_key]
        if info in library:
            print "Data already stored"
            return
        self._library[main_key].append(info)
        with open(info_file, 'w') as f:
            json.dump(self._library, f, indent=4)

    def __read_data(self):
        info_file = get_info_file(self._directory)
        with open(info_file, 'r') as f:
            current_data = json.load(f)
            if current_data is None:
                return
            if main_key in current_data and creating_key in current_data:
                self._library[main_key] = current_data[main_key]
                self._library[creating_key] = current_data[creating_key]


class ContentProvider:
    def __init__(self):
        user_app_dir = cmds.internalVar(userAppDir=True)
        directory = os.path.join(user_app_dir, 'ControllerLibrary')
        icon = os.path.join(user_app_dir, 'default_icon.jpg')
        self.__controller = Controller(directory)
        self.__main_ui = MainWindowUI(get_maya_main_window(), icon)

        # to avoid losing reference and make sure all functionality working with signals
        self.__main_ui.save_item_slot = self.save_selected_item

        self.populate_content()

        # bind to ui Signals
        self.__main_ui.on_path_changed.connect(self.get_new_path)
        self.__main_ui.on_save_notification.connect(self.save_selected_item)
        self.__main_ui.on_refresh_notification.connect(self.populate_content)

    def get_new_path(self, path):
        self.__controller.change_current_directory(path)
        print "Receive path from signal %s" % path

    def populate_content(self):
        self.__controller.load_all_data()
        data = self.__controller.get_content_data()
        self.__main_ui.fill_content(data)
        print "Populating UI"

    def save_selected_item(self, item_name):
        if self.__controller.is_item_exist(item_name):
            print "Current Item With name {} exist!".format(item_name)
            return
        print "Start from signal {}".format(item_name)
        # self.__controller.save(item_name)
        # self.__populate_content()

    def run(self):
        self.__main_ui.show()


# main entry point of the Content Provider tool
def run():
    print "Starting Maya Content Library Tool"
    runner = ContentProvider()
    runner.run()
