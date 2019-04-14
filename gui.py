from io import StringIO
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import os
import logging
import sys

from gui.main_window import Ui_MainWindow
from gui.device_dialog import Ui_Dialog
from gui.qjsonmodel import QJsonModel
import controller

logger = logging.getLogger("gui")


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, q_plain_text_edit):
        super().__init__()
        self.widget = q_plain_text_edit

    def emit(self, record):
        msg = self.format(record)
        self.widget.textCursor().insertText(msg + '\n')


class DeviceDialog(QtWidgets.QDialog):

    def __init__(self, parent=None, file_path="", file=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.file_path = file_path
        self.file = file
        self.load_file()
        self.accepted.connect(self.accept_click)

    def load_file(self):
        if self.file:
            device_conf = controller.load_device(os.path.join(self.file_path, self.file))
        else:
            device_conf = controller.load_device(None)
        self.ui.nameLineEdit.setText(device_conf.name)
        self.ui.mainClockdoubleSpinBox.setValue(float(device_conf.clk_freq))
        combo_box_position = self.ui.controlTypeComboBox.findText(device_conf.pmu_type)
        self.ui.controlTypeComboBox.setCurrentIndex(combo_box_position)
        self.ui.synchronizeControlCheckBox.setChecked(device_conf.sync_control)
        self.ui.usePLLCheckBox.setChecked(device_conf.use_pll)
        self.ui.useDividerCheckBox.setChecked(device_conf.divide_clock)
        self.ui.generateByFreqCheckBox.setChecked(not device_conf.strict_freq)
        self.ui.assignAllFreqCheckBox.setChecked(device_conf.all_freq)
        self.ui.freqThresholdSpinBox.setValue(float(device_conf.accepted_freq))
        self.ui.checkBox_1.setChecked(device_conf.ice40_confs[0])
        self.ui.checkBox_2.setChecked(device_conf.ice40_confs[1])
        self.ui.checkBox_3.setChecked(device_conf.ice40_confs[2])
        self.ui.checkBox_4.setChecked(device_conf.ice40_confs[3])

    def accept_click(self):
        if self.file:
            filename = os.path.join(self.file_path, self.file)
        else:
            filename = os.path.join(self.file_path, self.ui.nameLineEdit.text() + ".json")
        if self.ui.checkBox_1.isChecked() or self.ui.checkBox_2.isChecked() or self.ui.checkBox_3.isChecked() or \
                self.ui.checkBox_4.isChecked():
            reconfiguration = True
            reconf_list = [self.ui.checkBox_1.isChecked(), self.ui.checkBox_2.isChecked(),
                           self.ui.checkBox_3.isChecked(), self.ui.checkBox_4.isChecked()]
        else:
            reconfiguration = False
            reconf_list = [False, False, False, False]
        controller.update_device(filename,
                                 clk_freq=self.ui.mainClockdoubleSpinBox.value(),
                                 pmu_type=self.ui.controlTypeComboBox.currentText(),
                                 sync_control=self.ui.synchronizeControlCheckBox.isChecked(),
                                 use_pll=self.ui.usePLLCheckBox.isChecked(),
                                 divide_clock=self.ui.useDividerCheckBox.isChecked(),
                                 strict_freq=not self.ui.generateByFreqCheckBox.isChecked(),
                                 all_freq=self.ui.assignAllFreqCheckBox.isChecked(),
                                 accepted_freq=self.ui.freqThresholdSpinBox.value(),
                                 ice40_reconfiguration=reconfiguration,
                                 ice40_confs=reconf_list)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.source = None
        self.template = None
        self.output = None
        self.device_path = os.path.join("gui", "devices")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # calling helper functions
        self.import_device_jsons(self.device_path)
        self.qt_handler = QPlainTextEditLogger(self.ui.messagesPlainTextEdit)
        self.set_logger()
        self.monospaced_text()

        self.ui.sourcePushButton.clicked.connect(self.source_browse)
        self.ui.destinationPushButton.clicked.connect(self.destination_browse)
        self.ui.templatePushButton.clicked.connect(self.template_browse)
        self.ui.addPushButton.clicked.connect(self.add_device)
        self.ui.changePushButton.clicked.connect(self.change_device)
        self.ui.analyzePushButton.clicked.connect(self.analyze)
        self.ui.generatePushButton.clicked.connect(self.run)
        self.ui.loggingComboBox.currentTextChanged.connect(self.change_logger)

    def import_device_jsons(self, path):
        if os.path.isdir(path):
            self.ui.deviceComboBox.clear()
            if len(os.listdir(path)) > 0:
                self.ui.deviceComboBox.addItems(os.listdir(path))
            else:
                # create first device config
                controller.create_default_device(os.path.join(path, "auto_ice40.json"))
                self.import_device_jsons(path)

    def set_logger(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        # get the logging level and destination
        numeric_level = getattr(logging, self.ui.loggingComboBox.currentText().upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % self.ui.loggingComboBox.currentText())
        self.qt_handler.setLevel(numeric_level)
        self.qt_handler.setFormatter(formatter)
        root_logger.addHandler(self.qt_handler)

    def change_logger(self, logger_level):
        numeric_level = getattr(logging, logger_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % self.ui.loggingComboBox.currentText())
        self.qt_handler.setLevel(numeric_level)

    def monospaced_text(self):
        # font = QtGui.QFont()
        font = self.ui.messagesPlainTextEdit.document().defaultFont()
        font.setFamily("Courier New")
        font.setStyleHint(QtGui.QFont.Monospace)
        self.ui.messagesPlainTextEdit.setFont(font)
        # self.ui.outputTextEdit.setFont(font)
        self.ui.outputTextEdit.setTabStopWidth(4)

    def source_browse(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        dialog = QtWidgets.QFileDialog(self)
        if self.ui.sourceCheckBox.isChecked():
            dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        else:
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setWindowTitle("Select source")
        dialog.setNameFilter("All Files (*);;SystemC Files (*.cpp)")
        dialog.setOptions(options)
        if dialog.exec():
            files = dialog.selectedFiles()
            if files:
                self.source = files[0]
                self.ui.sourceLineEdit.setText(self.source)

    def template_browse(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select template", "",
                                                  "All Files (*);;Verilog Files (*.v)", options=options)
        if fileName:
            self.template = fileName
            self.ui.templateLineEdit.setText(self.template)

    def destination_browse(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Select/ Create destination", "",
                                                  "All Files (*);;Verilog Files (*.v)", options=options)
        if fileName:
            self.output = fileName
            self.ui.destinationLineEdit.setText(self.output)

    def add_device(self):
        add_device_dialog = DeviceDialog(self, self.device_path)
        add_device_dialog.exec_()
        self.import_device_jsons(self.device_path)

    def change_device(self):
        file = self.ui.deviceComboBox.currentText()
        add_device_dialog = DeviceDialog(self, self.device_path, file)
        add_device_dialog.exec_()

    # todo functions for GUI buttons
    def analyze(self):
        if not self.source:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Missing source file')
            error_dialog.exec_()
            return
        if self.ui.outputCheckBox.isChecked():
            sio = StringIO()
            pms_structure = controller.analyze(self.source, sio)
            self.ui.outputTextEdit.setText(sio.getvalue())
        else:
            if not self.output:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Missing output file')
                error_dialog.exec_()
                return
            pms_structure = controller.analyze(self.source, self.output)

        if pms_structure:
            model = QJsonModel()
            self.ui.structureTreeView.setModel(model)
            self.ui.structureTreeView.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            self.ui.structureTreeView.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

            model.load(pms_structure.__dict__)

    def run(self):
        if not self.source:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Missing source file')
            error_dialog.exec_()
            return
        if not self.template:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Missing template file')
            error_dialog.exec_()
            return

        device_file = self.ui.deviceComboBox.currentText()

        if self.ui.outputCheckBox.isChecked():
            sio = StringIO()
            pms_structure = controller.run(self.source, sio, self.template, os.path.join(self.device_path, device_file))
            self.ui.outputTextEdit.setText(sio.getvalue())
        else:
            if not self.output:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Missing output file')
                error_dialog.exec_()
                return
            pms_structure = controller.run(self.source, self.output, self.template, os.path.join(self.device_path, device_file))

        if pms_structure:
            model = QJsonModel()
            self.ui.structureTreeView.setModel(model)
            self.ui.structureTreeView.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            self.ui.structureTreeView.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

            model.load(pms_structure.__dict__)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = MainWindow()
    application.show()
    sys.exit(app.exec())