import os
import sys
import subprocess
from PySide2 import QtWidgets


# TODO:
# 1: implement base layout [DONE]
# 2: implement base functionality with slots and basic error checking [DONE]
# 3: implement basic transcoding logic [DONE]

# 4: ffmpeg console output to ui and user notification when task is done []
# 5: implement depth error checking and cmd construction []
# 6: implement different os selection for ffmpeg []
# 7: try to investigate how to make install for this tool []
# 8: document code and put to portfolio []


def is_path_valid(path):
    if not path:
        return False
    if not os.path.exists(path):
        return False
    return True


FFMPEG_ROOT = os.getcwd() + '/ffmpeg-5.0.0/'


def transcode_video(input_path, output_path, ctr, preset, file_name):
    print(input_path)
    print(output_path)
    print("Settings: {0}, {1}, {2}".format(ctr, preset, file_name))

    exec_path = FFMPEG_ROOT + 'ffmpeg'

    if not os.path.exists(exec_path):
        print("Executable does not exist, please check path {0}".format(exec_path))
        return

    ffmpeg_cmd = '{0}'.format(exec_path)
    ffmpeg_cmd += ' -y'
    ffmpeg_cmd += ' -i {0}'.format(input_path)
    ffmpeg_cmd += " -c:v libx264 -crf {0} -preset {1}".format(ctr, preset)
    ffmpeg_cmd += ' {0}'.format("{0}/{1}".format(output_path, file_name))

    print(ffmpeg_cmd)
    subprocess.call(ffmpeg_cmd, shell=True)


class ConverterWindow(QtWidgets.QWidget):

    # ctr settings
    QUALITY = {'lossless': 17, 'high': 21, 'medium': 30, 'low': 40}
    QUALITY_DEFAULT = 'medium'

    # presets settings
    PRESETS = ['slow', 'medium', 'fast']
    PRESET_DEFAULT = 'medium'

    # file extension
    EXTENSIONS = ['.mp4']
    EXTENSION_DEFAULT = '.mp4'

    def __init__(self):
        super(ConverterWindow, self).__init__(parent=None)
        self._create_widgets()
        self._create_ui()
        self._create_connections()

    # Create widgets instances
    def _create_widgets(self):
        self._input_le = QtWidgets.QLineEdit()
        self._input_btn = QtWidgets.QPushButton('...')

        self._output_le = QtWidgets.QLineEdit()
        self._output_btn = QtWidgets.QPushButton('...')

        self._quality_cmb = QtWidgets.QComboBox()
        for key, value in self.QUALITY.items():
            self._quality_cmb.addItem(key, value)
        self._quality_cmb.setCurrentText(self.QUALITY_DEFAULT)

        self._preset_cmd = QtWidgets.QComboBox()
        for value in self.PRESETS:
            self._preset_cmd.addItem(value, value)
        self._preset_cmd.setCurrentText(self.PRESET_DEFAULT)

        self._file_name_le = QtWidgets.QLineEdit()
        self._file_name_le.setText('output')

        self._format_cmb = QtWidgets.QComboBox()
        for value in self.EXTENSIONS:
            self._format_cmb.addItem(value, value)
        self._format_cmb.setCurrentText(self.EXTENSION_DEFAULT)

        self._transcode_btn = QtWidgets.QPushButton('Transcode')

    # Create ui layout
    def _create_ui(self):
        self.setWindowTitle('To MP4 Converter')
        size = (300, 400)
        self.setMinimumSize(size[0], size[1])
        self.setMaximumSize(size[0], size[1])

        input_grp = QtWidgets.QGroupBox('Input:')
        input_grp_layout = QtWidgets.QHBoxLayout()
        input_grp_layout.addWidget(self._input_le)
        self._input_btn.setFixedWidth(45)
        input_grp_layout.addWidget(self._input_btn)
        input_grp.setLayout(input_grp_layout)

        output_grp = QtWidgets.QGroupBox('Output path:')
        output_grp_layout = QtWidgets.QHBoxLayout()
        output_grp_layout.addWidget(self._output_le)
        self._output_btn.setFixedWidth(45)
        output_grp_layout.addWidget(self._output_btn)
        output_grp.setLayout(output_grp_layout)

        # settings
        settings_grp = QtWidgets.QGroupBox('Settings:')

        quality_grp_layout = QtWidgets.QHBoxLayout()
        quality_grp_layout.addWidget(QtWidgets.QLabel('Quality:'))
        self._quality_cmb.setFixedWidth(180)
        quality_grp_layout.addWidget(self._quality_cmb)

        presets_grp_layout = QtWidgets.QHBoxLayout()
        presets_grp_layout.addWidget(QtWidgets.QLabel('Preset:'))
        self._preset_cmd.setFixedWidth(180)
        presets_grp_layout.addWidget(self._preset_cmd)

        settings_grp_layout = QtWidgets.QVBoxLayout()
        settings_grp_layout.addLayout(quality_grp_layout)
        settings_grp_layout.addLayout(presets_grp_layout)
        settings_grp.setLayout(settings_grp_layout)

        save_grp = QtWidgets.QGroupBox('Output file')
        save_grp_layout = QtWidgets.QHBoxLayout()
        save_grp_layout.addWidget(self._file_name_le)
        save_grp_layout.addWidget(self._format_cmb)
        save_grp.setLayout(save_grp_layout)

        self._transcode_btn.setFixedHeight(60)

        # add to main window
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(input_grp)
        main_layout.addWidget(output_grp)
        main_layout.addWidget(settings_grp)
        main_layout.addWidget(save_grp)
        main_layout.addWidget(self._transcode_btn)

    # Create widgets connections
    def _create_connections(self):
        self._input_btn.clicked.connect(self._input_btn_slot)
        self._output_btn.clicked.connect(self._output_btn_slot)
        self._transcode_btn.clicked.connect(self._transcode_btn_slot)

    def _input_btn_slot(self):
        input_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Input file')
        if input_path[0]:
            self._input_le.setText(input_path[0])

    def _output_btn_slot(self):
        input_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save File As')
        if input_path:
            self._output_le.setText(input_path)

    def _transcode_btn_slot(self):
        # validating input
        input_path = self._input_le.text()
        if not is_path_valid(input_path):
            QtWidgets.QMessageBox.critical(self, 'Error', 'Input File is not set or Path is Not Valid!')
            return

        # validate output
        output_path = self._output_le.text()
        if not is_path_valid(output_path):
            QtWidgets.QMessageBox.critical(self, 'Error', 'Output File is not set or Path is Not Valid!')
            return

        ctr = self._quality_cmb.currentData()
        preset = self._preset_cmd.currentData()

        file_name = self._file_name_le.text()
        if not file_name:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please check output file name!')
            return

        extension = self._format_cmb.currentData()
        file = "{0}{1}".format(file_name, extension)
        transcode_video(input_path, output_path, ctr, preset, file)


def run():
    # Temporary solution for BigSur macOS
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    window = ConverterWindow()
    window.show()
    app.exec_()
