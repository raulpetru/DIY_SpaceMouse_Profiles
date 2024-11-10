import os
import sys
import json
import time
import psutil
import serial
import serial.tools.list_ports
import win32gui
import win32process
from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt, QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpacerItem, QSizePolicy, QSlider, QSystemTrayIcon, QMenu,
)
from serial.serialutil import SerialException
from MainWindow import Ui_MainWindow

basedir = os.path.dirname(__file__)

def get_mouse_settings(selected_port):
    mouse_settings = None

    # Open serial
    try_counter = 0
    while not mouse_settings:
        try:
            ser = serial.Serial(selected_port, 2500, timeout=1)
            ser.write('GET_UI'.encode('utf-8'))
            time.sleep(1)
            mouse_settings = ser.readlines()
            ser.close()
        except SerialException:
            pass
        if try_counter == 3:
            sys.exit()
        try_counter += 1

    dict_mouse_settings = dict()
    for i in mouse_settings:
        line = list(filter(None, i.decode("utf-8").strip().split(';')))
        key_value = dict()

        for i in line:
            key, value = i.split('=')
            key_value[key] = value

        setting_name = line[0].split('=')[1]
        dict_mouse_settings[setting_name] = key_value

    return dict_mouse_settings


def load_json():
    try:
        with open("profiles.json", "r") as profiles:
            return json.load(profiles)
    except FileNotFoundError:
        # If there is no json file, make one
        with open('profiles.json', 'w') as profiles:
            json.dump({}, profiles)
            return {}


def save_json(profiles_to_save):
    with open("profiles.json", "w") as profiles:
        json.dump(profiles_to_save, profiles)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.loaded_profiles = dict()
        self.last_window = str()
        self.active_window = str()
        self.mouse_settings = dict()

        self.setupUi(self)
        ports = [p.device for p in list(serial.tools.list_ports.comports())]
        self.comboBox.addItems(ports)
        self.mouse_settings = get_mouse_settings(self.comboBox.currentText())
        self.show()

        self.loaded_profiles = load_json()
        if not self.loaded_profiles:
            self.loaded_profiles = dict()

        # Check opened window and update the UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_active_window)
        self.timer.start(20)  # time in milliseconds.

        # Add widgets
        self.list_of_widgets = list()
        i = 0
        for widget in self.mouse_settings:
            self.list_of_widgets.append(QLabel(self.page))
            self.list_of_widgets[i].setObjectName(f'label-{widget}')
            label_string = f'{widget} (values:{self.mouse_settings[widget]["min"]}-{self.mouse_settings[widget]["max"]}, default:{self.mouse_settings[widget]["default"]})'
            self.list_of_widgets[i].original_label = label_string
            self.verticalLayout_4.addWidget(self.list_of_widgets[i])

            self.list_of_widgets.append(QSlider(self.page))
            self.list_of_widgets[i + 1].setObjectName(f"{widget}")
            self.list_of_widgets[i + 1].setOrientation(Qt.Orientation.Horizontal)
            self.list_of_widgets[i + 1].setMinimum(int(self.mouse_settings[widget]['min']))
            self.list_of_widgets[i + 1].setMaximum(int(self.mouse_settings[widget]['max']))
            self.list_of_widgets[i + 1].setValue(int(self.mouse_settings[widget]['default']))
            self.list_of_widgets[i + 1].setTickInterval(5)
            self.list_of_widgets[i + 1].setTickPosition(QSlider.TicksAbove)
            self.verticalLayout_4.addWidget(self.list_of_widgets[i + 1])

            # Connect slider to label
            self.list_of_widgets[i + 1].valueChanged.connect(self.update_label)

            # Change label string after creating slider
            self.list_of_widgets[i].setText(f'{label_string} = {self.list_of_widgets[i + 1].value()}')

            # Increment counter
            i = i + 2

        # Overwrite the vertical spacer
        self.verticalLayout_4.removeItem(self.verticalSpacer_2)
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        # Apply and Save button
        self.saveButton = QPushButton('Apply and Save', self.page)
        self.verticalLayout_4.addWidget(self.saveButton)
        self.saveButton.released.connect(self.apply_and_save)

    def apply_and_save(self):
        for slider in self.list_of_widgets:
            if isinstance(slider, QSlider):
                if self.active_window != '' and self.active_window != 'None':
                    if self.active_window in self.loaded_profiles:
                        self.loaded_profiles[self.active_window][slider.objectName()] = slider.value()
                    else:
                        self.loaded_profiles[self.active_window] = {slider.objectName(): slider.value()}
        save_json(self.loaded_profiles)
        self.send_values_to_mouse()

    def update_label(self):
        slider = self.sender()
        if isinstance(slider, QSlider):
            label = self.findChild(QLabel, f'label-{slider.objectName()}')
            label.setText(f'{label.original_label} = {slider.value()}')

    def get_active_window(self):
        current_window = win32gui.GetForegroundWindow()
        if current_window != self.last_window:
            _, pid = win32process.GetWindowThreadProcessId(current_window)
            # Sometimes can't get the process PID so we continue and try again
            try:
                process = psutil.Process(pid)
                if process.name() in (
                        'DIY SpaceMouse Profiles.exe', 'WindowsTerminal.exe', 'explorer.exe', 'cmd.exe', 'python.exe'):
                    if self.last_window == 'None':
                        self.active_window = 'None'
                else:
                    self.active_window = process.name()
                    self.last_window = current_window
                    self.send_values_to_mouse()
            except:
                pass
            self.label_3.setText(f'Active window: {self.active_window}')

    def send_values_to_mouse(self):
        # Open serial
        ser = serial.Serial(self.comboBox.currentText(), 25000, timeout=1)
        send_list = []
        for widget in self.list_of_widgets:
            if self.active_window in self.loaded_profiles:
                if isinstance(widget, QSlider) and widget.objectName() in self.loaded_profiles[self.active_window]:
                    value = self.loaded_profiles[self.active_window][widget.objectName()]
                    widget.setValue(value)
                    send_list.append(f'{widget.objectName()}={widget.value()},')
            else:
                if isinstance(widget, QSlider):
                    value = int(self.mouse_settings[widget.objectName()]['default'])
                    widget.setValue(value)
                    send_list.append(f'{widget.objectName()}={widget.value()},')
        # Remove last comma
        send_list[-1] = send_list[-1][:-1]
        send_list.append('\n')
        message = ''.join(send_list)
        ser.write(message.encode('utf-8'))
        # Close serial
        ser.close()

    def open_app(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(os.path.join(basedir, 'icon.ico')))

    # Create the window
    window = MainWindow()

    # Create the tray
    icon = QIcon(os.path.join(basedir, 'icon.ico'))
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.setToolTip('DIY SpaceMouse Profiles')

    # Add a Quit option to the menu.
    menu = QMenu()

    show_app = QAction("Show")
    show_app.triggered.connect(window.show)
    menu.addAction(show_app)

    quit_app = QAction("Quit")
    quit_app.triggered.connect(app.quit)
    menu.addAction(quit_app)

    # Add the menu to the tray
    tray.setContextMenu(menu)

    # Apply the event to open the window by double-clicking the tray icon if the window is closed
    tray.activated.connect(window.open_app)
    window.show()
    app.exec()
