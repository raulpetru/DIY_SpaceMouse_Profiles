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
    QSpacerItem, QSizePolicy, QSlider, QSystemTrayIcon, QMenu, QTabWidget, QWidget, QVBoxLayout, QCheckBox,
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
            ser = serial.Serial(selected_port, 250000, timeout=1)
            ser.write('GET_UI\n'.encode('utf-8'))
            time.sleep(1)
            mouse_settings = ser.readlines()
            ser.close()
        except SerialException:
            pass
        if try_counter == 3:
            return 0
        try_counter += 1

    dict_mouse_settings = dict()
    for i in mouse_settings:
        line = list(filter(None, i.decode("utf-8").strip().split(';')))
        key_value = dict()

        for i in line:
            key, value = i.split('=')
            key_value[key] = value
            if key == 'send_name':
                setting_name = value

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
        # Find serial port that responds to 'GET_UI' instruction
        for port in [(i, self.comboBox.itemText(i)) for i in range(self.comboBox.count())]:
            self.mouse_settings = get_mouse_settings(port[1])
            if self.mouse_settings != 0:
                self.comboBox.setCurrentIndex(port[0])
                break
        else:
            sys.exit()
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

        # Create the tab widget
        self.tab_widget = QTabWidget(self.page)
        self.tab_widget.setObjectName('tabWidget')
        # Keep a set of tabs and add widgets to existing tabs if they exist
        set_of_tabs = set()
        list_of_tabs_layouts = []
        for widget in self.mouse_settings.values():
            tab_name = widget['tab']
            if tab_name in set_of_tabs:
                tab_layout = self.findChild(QVBoxLayout, f'tab_layout-{tab_name}')
            else:
                tab = QWidget(self.tab_widget)
                tab.setObjectName(f'tab-{tab_name}')
                tab_layout = QVBoxLayout(tab)
                tab_layout.setObjectName(f'tab_layout-{tab_name}')
                self.tab_widget.addTab(tab, f'{tab_name}')
                set_of_tabs.add(tab_name)
                list_of_tabs_layouts.append(tab_layout)

            self.list_of_widgets.append(QLabel(tab))
            self.list_of_widgets[i].setObjectName(f'label-{widget["send_name"]}')
            if widget['type'] == 'slider':
                label_string = f'{widget['name']} (values:{widget["min"]}-{widget["max"]}, default:{widget["default"]})'
                self.list_of_widgets.append(QSlider(tab))
                self.list_of_widgets[i + 1].setObjectName(f'{widget["send_name"]}')
                self.list_of_widgets[i + 1].setOrientation(Qt.Orientation.Horizontal)
                self.list_of_widgets[i + 1].setMinimum(int(widget['min']))
                self.list_of_widgets[i + 1].setMaximum(int(widget['max']))
                self.list_of_widgets[i + 1].setValue(int(widget['default']))
                self.list_of_widgets[i + 1].setTickInterval(5)
                self.list_of_widgets[i + 1].setTickPosition(QSlider.TicksAbove)
                self.list_of_widgets[i + 1].setSingleStep(1)
                tab_layout.addWidget(self.list_of_widgets[i])
                tab_layout.addWidget(self.list_of_widgets[i + 1])
            elif widget['type'] == 'bool':
                label_string = f'{widget['name']} (values: false/true, default:{widget["default"]})'
                self.list_of_widgets.append(QCheckBox(tab))
                self.list_of_widgets[i + 1].setObjectName(f'{widget["send_name"]}')
                check_value = int(widget['default'])
                if check_value:
                    check_value = Qt.Checked
                else:
                    check_value = Qt.Unchecked
                self.list_of_widgets[i + 1].setCheckState(check_value)
                tab_layout.addWidget(self.list_of_widgets[i])
                tab_layout.addWidget(self.list_of_widgets[i + 1])
            self.list_of_widgets[i].original_label = label_string

            # Connect slider to label and change label string after creating slider
            if widget['type'] == 'slider':
                self.list_of_widgets[i + 1].valueChanged.connect(self.update_label)
                self.list_of_widgets[i].setText(f'{label_string} = {self.list_of_widgets[i + 1].value()}')
            elif widget['type'] == 'bool':
                self.list_of_widgets[i + 1].checkStateChanged.connect(self.update_label)
                self.list_of_widgets[i].setText(f'{label_string} = {self.list_of_widgets[i + 1].isChecked()}')

            # Increment counter
            i = i + 2

        self.verticalLayout_4.addWidget(self.tab_widget)
        self.tab_widget.setCurrentIndex(0)
        for tab_page in list_of_tabs_layouts:
            tab_page.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        # Overwrite the vertical spacer
        self.verticalLayout_4.removeItem(self.verticalSpacer_2)

        # Apply and Save button
        self.saveButton = QPushButton('Apply and Save', self.page)
        self.verticalLayout_4.addWidget(self.saveButton)
        self.saveButton.released.connect(self.apply_and_save)

    def apply_and_save(self):
        for widget in self.list_of_widgets:
            if isinstance(widget, QSlider):
                if self.active_window != '' and self.active_window != 'None':
                    if self.active_window in self.loaded_profiles:
                        self.loaded_profiles[self.active_window][widget.objectName()] = widget.value()
                    else:
                        self.loaded_profiles[self.active_window] = {widget.objectName(): widget.value()}
            elif isinstance(widget, QCheckBox):
                if self.active_window != '' and self.active_window != 'None':
                    # Save values as 0/1 instead of false/true
                    if widget.isChecked():
                        value = 1
                    else:
                        value = 0
                    if self.active_window in self.loaded_profiles:
                        self.loaded_profiles[self.active_window][widget.objectName()] = value
                    else:
                        self.loaded_profiles[self.active_window] = {widget.objectName(): value}
        save_json(self.loaded_profiles)
        self.send_values_to_mouse()

    def update_label(self):
        sender = self.sender()
        if isinstance(sender, QSlider):
            label = self.findChild(QLabel, f'label-{sender.objectName()}')
            label.setText(f'{label.original_label} = {sender.value()}')
        elif isinstance(sender, QCheckBox):
            label = self.findChild(QLabel, f'label-{sender.objectName()}')
            label.setText(f'{label.original_label} = {sender.isChecked()}')

    def get_active_window(self):
        current_window = win32gui.GetForegroundWindow()
        if current_window != self.last_window:
            _, pid = win32process.GetWindowThreadProcessId(current_window)
            # Sometimes can't get the process PID so we continue and try again
            try:
                process = psutil.Process(pid)
                if process.name() in (
                        'DIY_SpaceMouse_Profiles.exe', 'WindowsTerminal.exe', 'explorer.exe', 'cmd.exe', 'python.exe'):
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
                if (isinstance(widget, QSlider) or isinstance(widget, QCheckBox)) and widget.objectName() in self.loaded_profiles[self.active_window]:
                    if isinstance(widget, QSlider):
                        value = self.loaded_profiles[self.active_window][widget.objectName()]
                        widget.setValue(value)
                        send_list.append(f'{widget.objectName()}={widget.value()},')
                    elif isinstance(widget, QCheckBox):
                        value = int(self.loaded_profiles[self.active_window][widget.objectName()])
                        if value:
                            set_value = Qt.Checked
                        else:
                            set_value = Qt.Unchecked
                        widget.setCheckState(set_value)
                        send_list.append(f'{widget.objectName()}={value},')
            else:
                if isinstance(widget, QSlider):
                    value = int(self.mouse_settings[widget.objectName()]['default'])
                    widget.setValue(value)
                    send_list.append(f'{widget.objectName()}={widget.value()},')
                if isinstance(widget, QCheckBox):
                    value = int(self.mouse_settings[widget.objectName()]['default'])
                    if value:
                        set_value = Qt.Checked
                    else:
                        set_value = Qt.Unchecked
                    widget.setCheckState(set_value)
                    send_list.append(f'{widget.objectName()}={value},')
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
