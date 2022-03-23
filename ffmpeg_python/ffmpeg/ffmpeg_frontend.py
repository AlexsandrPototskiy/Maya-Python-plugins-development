import os
import sys
from PySide2 import QtGui
from PySide2 import QtWidgets

# 1: implement base layout
# 2: implement base functionality with slots
# 3: implement interaction with ffmpeg_helpers.py


class FFmpegWindow(QtWidgets.QWidget):

    def __init__(self):
        super(FFmpegWindow, self).__init__(parent=None)
        self._create_widgets()
        self._create_ui()
        self._create_connections()

    # Create widgets instances
    def _create_widgets(self):
        self._input_le = QtWidgets.QLineEdit()
        self._input_btn = QtWidgets.QPushButton('...')

        self._output_le = QtWidgets.QLineEdit()
        self._output_btn = QtWidgets.QPushButton('...')

    # Create ui layout
    def _create_ui(self):
        self.setWindowTitle('FFmpeg Transcoder')
        self.setMinimumSize(512, 300)
        self.setMaximumSize(512, 300)

        input_grp = QtWidgets.QGroupBox('Input')
        input_grp_layout = QtWidgets.QHBoxLayout()
        input_grp_layout.addWidget(self._input_le)
        input_grp_layout.addWidget(self._input_btn)
        input_grp.setLayout(input_grp_layout)

        output_grp = QtWidgets.QGroupBox('Output')
        output_grp_layout = QtWidgets.QHBoxLayout()
        output_grp_layout.addWidget(self._output_le)
        output_grp_layout.addWidget(self._output_btn)
        output_grp.setLayout(output_grp_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(input_grp)
        main_layout.addWidget(output_grp)

    # Create widgets connections
    def _create_connections(self):
        pass


if __name__ == '__main__':

    # Temporary solution for BigSur
    os.environ["QT_MAC_WANTS_LAYER"] = "1"

    app = QtWidgets.QApplication(sys.argv)

    window = FFmpegWindow()
    window.show()

    app.exec_()
