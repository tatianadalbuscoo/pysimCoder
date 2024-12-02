import os
import sys
import shutil
from numpy import nonzero, ones, asmatrix, size, array, zeros
import json
from supsisim.qtvers import *


""" The following commands are provided:
TO DO:
    - Create a valid project for CCS
        - This script works on linux environment and on wsl.
        - If you press Settings -> Settings -> Configure in the pysimCoder menu you can configure the paths of the working folders (ti and C2000Ware_4_01_00_00), creating a config.json file.
            - Without the config.json file it is not possible to generate the code to generate the project for CCS.
            - If it does not find the paths necessary in the paths entered, which CCS uses, the project is not created and everything is cleaned.
            - If it does not find the src files in the paths, it asks if you want to keep the config.json file or delete it. 
            - Paths can be entered for both windows and wsl (Selectable from the browser button where to insert the path) eg:
                - C:\ti\c2000\C2000Ware_4_01_00_00
                - /mnt/c/ti/c2000/C2000Ware_4_01_00_00
        - Save these paths to a config.json file for future runs
        - Organize all files in a hierarchy and create .project .cproject and .ccsproject files with user-entered paths.
        - Generates the main file (cpu_timers_cpu01.c) that calls the functions that PysimCoder creates, changing their name.
        - Include only files that use blocks in your project e.g.:
            - If {model}.c contains the word inputGPIOblk includes: inputGPIOblk.c, button.c and button.h
        
"""

# Global variables

# Saved if it is a linux environment or wsl
isInWSL = False


class ConfigFile:

    """
    Class to represent a generic configuration file.
    """

    def __init__(self, name, extension="json"):

        """
        Initializes a configuration file with name and extension.
        """

        self.name = name
        self.extension = extension
        self.path = f"{self.name}.{self.extension}"

    def get_name(self, with_extension=True):

        """
        Returns file name with/without extension.
        """
        return self.path if with_extension else self.name

    def exists(self):

        """
        Check if the configuration file exists.
        """

        return os.path.isfile(self.path)

    def load(self):

        """
        Loads the contents of the configuration file, if it exists.
        """

        if self.exists():
            with open(self.path, "r") as file:
                return json.load(file)
        return {}

    def save(self, data):

        """
        Save the data in JSON format in the configuration file.
        """

        with open(self.path, "w") as file:
            json.dump(data, file, indent=4)

    def delete(self):

        """
        Delete the configuration file, if it exists.
        """

        if self.exists():
            os.remove(self.path)

    def __str__(self):

        """
        Textual representation of the configuration file.
        """

        return f"ConfigFile(name={self.name}, path={self.path})"


class ProjectConfigWindow(QDialog):
    
    """
    This class represents a project configuration window. It provides a user interface to select modes, 
    configure settings, and save them to a JSON configuration file.
    """

    def __init__(self, model):
        
        """
        Initializes the project configuration window, loading the configuration 
        file and setting up the user interface.
        """

        super().__init__()
        self.setWindowTitle(f"Project Configuration: {model}")
        self.resize(800, 300)
        self.model = model

        # Path to the configuration file
        self.config_file_path = os.path.join(f"./{model}_project", f"{model}_configuration.json")

        # Load configuration file data (if exists)
        self.config_data = self.load_config_file()

        # Initialize the interface
        self.init_ui()
        self.set_initial_values()

    def load_config_file(self):

        """
        Loads the {model}_configuration.json configuration file if it exists.
        """

        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, "r") as file:
                return json.load(file)
        return {}

    def set_initial_values(self):

        """
        Sets the initial interface values ​​based on the loaded configuration.
        """

        mode = self.config_data.get("mode")
        self.mode_combo.setCurrentText(mode if mode else "-")

        # Show fields consistent with the loaded mode
        if mode == "1":
            peripheral = self.config_data.get("peripheral", "-")
            self.peripheral_combo.setCurrentText(peripheral)
            self.peripheral_label.show()
            self.peripheral_combo.show()

            # Timer period is only shown if Peripheral is Timer
            if peripheral == "Timer":
                timer_period = self.config_data.get("timer_period", "")
                self.timer_period_input.setText(timer_period)
                self.timer_period_label.show()
                self.timer_period_input.show()
            else:
                self.timer_period_input.setText("")
                self.timer_period_label.hide()
                self.timer_period_input.hide()

        elif mode == "2":
            trigger_adc = self.config_data.get("trigger_adc", "-")
            self.trigger_adc_combo.setCurrentText(trigger_adc)
            self.trigger_adc_label.show()
            self.trigger_adc_combo.show()

            # Timer period is only shown if Trigger ADC is Timer
            if trigger_adc == "Timer":
                timer_period = self.config_data.get("timer_period", "")
                self.timer_period_input.setText(timer_period)
                self.timer_period_label.show()
                self.timer_period_input.show()
            else:
                self.timer_period_input.setText("")
                self.timer_period_label.hide()
                self.timer_period_input.hide()

        else:  # No mode selected.
            self.peripheral_label.hide()
            self.peripheral_combo.hide()
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            self.trigger_adc_label.hide()
            self.trigger_adc_combo.hide()


    def init_ui(self):

        """
        Sets up the user interface components and layout for the configuration window.
        """

        # Main layout
        layout = QVBoxLayout()

        # Explanation of the modes
        explanation_label = QLabel(
            "Mode 1: Each module works independently. A peripheral (Timer or ePWM) provides the time base via interrupt.\n"
            "Mode 2: A peripheral (Timer or ePWM) triggers ADC conversion, and the ADC generates an interrupt when conversion is done.\n"
        )
        explanation_label.setWordWrap(True)
        layout.addWidget(explanation_label)

        # Drop-down menu to select the mode
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["-", "1", "2"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)

        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Layout to select device type (ePWM or Timer) for mode 1
        self.peripheral_layout = QHBoxLayout()
        self.peripheral_label = QLabel("Interrupt Peripheral:")
        self.peripheral_combo = QComboBox()
        self.peripheral_combo.addItems(["-"])
        self.peripheral_combo.currentTextChanged.connect(self.on_peripheral_changed)
        self.peripheral_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.peripheral_layout.addWidget(self.peripheral_label)
        self.peripheral_layout.addWidget(self.peripheral_combo)

        # Hide the device layout at the beginning
        self.peripheral_label.hide()
        self.peripheral_combo.hide()
        layout.addLayout(self.peripheral_layout)

        # Drop-down menu for ADC Trigger - visible for mode 2 only
        self.trigger_adc_layout = QHBoxLayout()
        self.trigger_adc_label = QLabel("Trigger ADC:")
        self.trigger_adc_combo = QComboBox()
        self.trigger_adc_combo.addItems(["-"])
        self.trigger_adc_combo.currentTextChanged.connect(self.on_trigger_adc_changed)
        self.trigger_adc_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.trigger_adc_layout.addWidget(self.trigger_adc_label)
        self.trigger_adc_layout.addWidget(self.trigger_adc_combo)

        # Hide the ADC Trigger layout at the beginning
        self.trigger_adc_label.hide()
        self.trigger_adc_combo.hide()
        layout.addLayout(self.trigger_adc_layout)

        # Timer period field (shared between modes 1 and 2)
        self.timer_period_layout = QHBoxLayout()
        self.timer_period_label = QLabel("Period Timer [micro seconds]:")
        self.timer_period_input = QLineEdit()
        self.timer_period_input.setPlaceholderText("Enter timer period")
        self.timer_period_input.textChanged.connect(self.update_save_button_state)
        self.timer_period_layout.addWidget(self.timer_period_label)
        self.timer_period_layout.addWidget(self.timer_period_input)

        # Hide the timer period layout at the beginning
        self.timer_period_label.hide()
        self.timer_period_input.hide()
        layout.addLayout(self.timer_period_layout)

        # Spacer to push buttons down
        layout.addStretch()

        # Layout for buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_and_close)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_and_close)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def on_mode_changed(self, mode):

        """
        Show or hide fields based on the chosen mode.
        """

        if mode == "-":
            self.peripheral_label.hide()
            self.peripheral_combo.hide()
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            self.trigger_adc_label.hide()
            self.trigger_adc_combo.hide()
            return

        if "-" in self.mode_combo.itemText(0):

            # Remove the "-" option from the mode after the first selection
            self.mode_combo.removeItem(0)

        if mode == "1":
            self.peripheral_combo.clear()
            self.peripheral_combo.addItems(["-", "ePWM", "Timer"])
            self.peripheral_label.show()
            self.peripheral_combo.show()

            self.trigger_adc_label.hide()
            self.trigger_adc_combo.hide()
            self.timer_period_label.hide()
            self.timer_period_input.hide()

        elif mode == "2":
            self.trigger_adc_combo.clear()
            self.trigger_adc_combo.addItems(["-", "ePWM", "Timer"])
            self.trigger_adc_label.show()
            self.trigger_adc_combo.show()

            self.timer_period_label.hide()
            self.timer_period_input.hide()

            self.peripheral_label.hide()
            self.peripheral_combo.hide()

        self.update_save_button_state()

    def on_peripheral_changed(self, peripheral):

        """
        Show or hide the timer period field based on the selected device (mode 1 only).
        """

        if peripheral == "-":
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            return

        if "-" in self.peripheral_combo.itemText(0):

            # Remove the "-" option after the first selection
            self.peripheral_combo.removeItem(0)

        if peripheral == "Timer":
            self.timer_period_label.show()
            self.timer_period_input.show()
        else:
            self.timer_period_label.hide()
            self.timer_period_input.hide()

        self.update_save_button_state()

    def on_trigger_adc_changed(self, trigger):

        """
        Show or hide the timer period field based on the chosen ADC trigger (mode 2 only).
        """

        if trigger == "-":
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            return

        if "-" in self.trigger_adc_combo.itemText(0):

            # Remove the "-" option after the first selection
            self.trigger_adc_combo.removeItem(0)

        if trigger == "Timer":
            self.timer_period_label.show()
            self.timer_period_input.show()
        else:
            self.timer_period_label.hide()
            self.timer_period_input.hide()

        self.update_save_button_state()


    def update_save_button_state(self):

        """
        Enable or disable the Save button based on the current state of the fields.
        Conditions to enable:
        Mode 1 + ePWM
        Mode 1 + Timer + valid period (positive number)
        Mode 2 + ePWM 
        Mode 2 + Timer + valid period (positive number)
        """

        mode = self.mode_combo.currentText()
        peripheral = self.peripheral_combo.currentText()
        trigger_adc = self.trigger_adc_combo.currentText()
        timer_period = self.timer_period_input.text()

        if mode == "1":
            if peripheral == "ePWM":
                self.save_button.setEnabled(True)
                return
            elif peripheral == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                self.save_button.setEnabled(True)
                return

        elif mode == "2":
            if trigger_adc == "ePWM":
                self.save_button.setEnabled(True)
                return
            elif trigger_adc == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                self.save_button.setEnabled(True)
                return

        # Disable the button if no conditions are met
        self.save_button.setEnabled(False)

    def get_current_state(self):
        
        """
        Returns the current state based on the selected fields.
        Possible states:
        - 1: Mode 1 + Timer + valid period (positive number)
        - 2: Mode 1 + ePWM
        - 3 : Mode 2 + Timer + valid period (positive number)
        - 4: Mode 2 + ePWM 
        """
        
        mode = self.mode_combo.currentText()
        peripheral = self.peripheral_combo.currentText()
        trigger_adc = self.trigger_adc_combo.currentText()
        timer_period = self.timer_period_input.text()

        if mode == "1":
            if peripheral == "ePWM":
                return 2
            elif peripheral == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                return 1

        elif mode == "2":
            if trigger_adc == "ePWM":
                return 4
            elif trigger_adc == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                return 3

        # No valid status
        return None

    def cancel_and_close(self):

        """
        Delete the project
        """
        
        project_dir = f"./{self.model}_project"
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)      

        self.reject()

    def closeEvent(self, event):

        """
        Performs the same logic as `cancel_and_close` when the `X` is pressed.
        """

        self.cancel_and_close()
        event.accept()  # Close the window

    def save_and_close(self):

        """
        Save the selected configuration to a JSON file.
        """

        selected_mode = self.mode_combo.currentText()
        selected_peripheral = None
        selected_trigger_adc = None
        timer_period = None

        if selected_mode == "1":
            selected_peripheral = self.peripheral_combo.currentText()
            if selected_peripheral == "Timer":
                timer_period = self.timer_period_input.text()
        elif selected_mode == "2":
            selected_trigger_adc = self.trigger_adc_combo.currentText()
            if selected_trigger_adc == "Timer":
                timer_period = self.timer_period_input.text()

        config_data = {
            "mode": selected_mode,
            "peripheral": selected_peripheral,
            "trigger_adc": selected_trigger_adc,
            "timer_period": timer_period,
        }

        # Save to project configuration file
        save_project_config_file(self.model, config_data)

        # Closes with status "Accepted"
        self.accept()


class ConfigWindow(QDialog):
    
    """
    Represents a configuration window for setting and saving TI and C2000Ware paths.
    Allows browsing directories and saving changes to the general configuration.
    """

    def __init__(self):

        """
        Initializes the configuration window, loading existing paths and setting up the UI.
        """

        super().__init__()
        self.setWindowTitle("Configuration")
        self.resize(800, 200)

        # Load existing configuration
        config = general_config.load()
        self.ti_path = config.get('ti_path', '')
        self.c2000Ware_path = config.get('c2000Ware_path', '')

        self.init_ui()

    def init_ui(self):

        """
        Sets up the user interface with fields for TI and C2000Ware paths and Save/Cancel buttons.
        """

        layout = QVBoxLayout()

        # Field for the TI path
        ti_layout = QHBoxLayout()
        ti_label = QLabel("TI folder path:")
        self.ti_input = QLineEdit(self.ti_path)
        ti_browse = QPushButton("Browse")
        ti_browse.clicked.connect(self.browse_ti_path)
        ti_layout.addWidget(ti_label)
        ti_layout.addWidget(self.ti_input)
        ti_layout.addWidget(ti_browse)

        # Field for the C2000Ware path
        c2000_layout = QHBoxLayout()
        c2000_label = QLabel("C2000Ware_4_01_00_00 folder path:")
        self.c2000_input = QLineEdit(self.c2000Ware_path)
        c2000_browse = QPushButton("Browse")
        c2000_browse.clicked.connect(self.browse_c2000_path)
        c2000_layout.addWidget(c2000_label)
        c2000_layout.addWidget(self.c2000_input)
        c2000_layout.addWidget(c2000_browse)

        # Save button
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_close)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_and_close)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # Adds everything to the layout
        layout.addLayout(ti_layout)
        layout.addLayout(c2000_layout)
        layout.addLayout(button_layout)

        # Set the main layout
        self.setLayout(layout)

    def browse_ti_path(self):

        """
        Allows the user to select and set the TI folder path via a file dialog.
        """

        path = QFileDialog.getExistingDirectory(self, "Select TI folder path")
        if path:
            self.ti_input.setText(path)

    def browse_c2000_path(self):

        """
        Allows the user to select and set the C2000Ware folder path via a file dialog.
        """

        path = QFileDialog.getExistingDirectory(self, "Select C2000Ware folder path")
        if path:
            self.c2000_input.setText(path)

    def cancel_and_close(self):
        
        """
        Closes the dialog with a "Rejected" status.
        """

        self.reject()

    def save_and_close(self):

        """
        Saves the configuration and closes the dialog with an "Accepted" status.
        """

        save_general_config_file(general_config, self.ti_input.text(), self.c2000_input.text())
        self.accept()

    def closeEvent(self, event):

        """
        Ensures that the "Rejected" state is set if closed with the 'x'
        """

        self.reject()


# File name where to save the paths
general_config = ConfigFile("general_config")


def save_general_config_file(config_file: ConfigFile, ti_path, c2000Ware_path):

    """
    Saves the general configuration file with specified paths.

    This function updates the configuration file with the provided `ti_path` 
    and `c2000Ware_path`, and displays a confirmation message upon successful save.

    Example Call:
    -------------
    save_general_config_file(config_file, "path/to/TI", "path/to/C2000Ware")

    Parameters
    ----------
    config_file     : The configuration file object to update.
    ti_path         : Path to the TI folder.
    c2000Ware_path  : Path to the C2000Ware folder.

    Returns
    -------
    - 

    """

    config_data = {
        "ti_path": ti_path,
        "c2000Ware_path": c2000Ware_path,
    }
    config_file.save(config_data)
    QMessageBox.information(None, "General configs Saved", "Paths saved successfully!")


def save_project_config_file(model, config_data):

    """
    Saves the project configuration file for a specific project.

    This function creates or updates the configuration file for a project 
    based on the given model name and configuration data.

    Example Call:
    -------------
    save_project_config_file("model_name", {"key": "value"})

    Parameters
    ----------
    model       : The name of the project.
    config_data : The configuration data to be saved in the JSON file.

    Returns
    -------
    -

    """

    project_dir = f"./{model}_project"
    config_file_path = os.path.join(project_dir, f"{model}_configuration.json")
    config_file = ConfigFile(name=f"{model}_configuration", extension="json")
    config_file.path = config_file_path

    config_file.save(config_data)


def open_config_window():
    """
    Opens the configuration window for user input.

    Example Call:
    -------------
    open_config_window()

    Parameters
    ----------
    -

    Returns
    -------
    bool    : True if the configuration was saved (Accepted), False otherwise (Rejected).
    """

    app = QApplication.instance() or QApplication([])
    config_window = ConfigWindow()
    result = config_window.exec()  # Return QDialog.Accepted or QDialog.Rejected
    return result == QDialog.Accepted


def open_project_config_window(model):

    """
    Opens the project configuration window for a specific project.
    It collects and returns the configuration data if the user saves their changes.

    Example Call:
    -------------
    open_project_config_window("example_model")

    Parameters
    ----------
    model : The name of the project to configure.

    Returns
    -------
    dict or None    : A dictionary containing the configuration data if saved, or `None` if the operation was canceled.
    """

    app = QApplication.instance() or QApplication([])
    project_config_window = ProjectConfigWindow(model)
    result = project_config_window.exec()  # Returns QDialog.Accepted or QDialog.Rejected

    if result == QDialog.Accepted:

        config_data = {
            "mode": project_config_window.mode_combo.currentText(),
            "peripheral": project_config_window.peripheral_combo.currentText() if project_config_window.mode_combo.currentText() == "1" else None,
            "trigger_adc": project_config_window.trigger_adc_combo.currentText() if project_config_window.mode_combo.currentText() == "2" else None,
            "timer_period": project_config_window.timer_period_input.text() or None,
        }
        return config_data

    return None


def check_wsl_environment():

    """ Detects if the environment is running within Windows Subsystem for Linux (WSL).

    This function determines whether the current environment is WSL or a native Linux
    installation by inspecting the system's release name. It sets the global variable 
    `isInWSL` to `True` if WSL is detected, otherwise `False`.

    Example Call:
    -------------
    check_wsl_environment()

    Parameters
    ----------
    -

    Returns
    -------
    -

    """

    global isInWSL
    isInWSL = 'microsoft' in os.uname().release.lower()


def convert_path_for_wsl(path):

    """ Converts a Windows path to a WSL-compatible path.

    This function takes a Windows-style file path and converts it to a format 
    that can be used within WSL. The function 
    checks if the current environment is WSL before performing the conversion.

    Example Call:
    -------------
    new_path = convert_path_for_wsl(path)

    Parameters:
    -----------
    path       : The file path in Windows format (e.g., "C:\\Users\\user\\path").

    Returns:
    --------
    str     : The converted WSL-compatible path. If the path is already compatible or the conditions are not met, returns the original path unchanged.

    Example:
    --------
    Input: "C:\\Users\\user\\path"
    Output: "/mnt/c/Users/user/path"

    """

    # Check if path isn't empty, and if the code is running in a WSL environment
    if path and isInWSL:
        if '\\' in path or (len(path) > 1 and path[1] == ':'):
            path = path.replace('\\', '/')

            # Check if the path is something like C:\...
            if path[1] == ':':
                drive_letter = path[0].lower()
                path = f"/mnt/{drive_letter}{path[2:]}"

    return path


def convert_path_for_windows(path):

    """ Converts a WSL path to a Windows-compatible path while maintaining slashes ('/').

    This function takes a path formatted for WSL and converts it to a Windows path format, preserving the use of forward slashes ('/')
    instead of backslashes ('\\'). The function checks if the path is a WSL path and 
    if it is running in a WSL environment before performing the conversion.

    Example Call:
    -------------
    new_path = convert_path_for_windows(path)

    Parameters:
    -----------
    path       : The file path in WSL format (e.g., "/mnt/c/Users/user/path").

    Returns:
    --------
    str        : The converted Windows-compatible path. If the path is not a WSL path or we aren't in a wsl envoirment the original path is returned.

    Example:
    --------
    Input: "/mnt/c/Users/user/path"
    Output: "C:/Users/user/path"

    """

    # Check if starts with /mnt/, and if the code is running in a WSL environment
    if path.startswith('/mnt/') and isInWSL:
        parts = path.split('/')
        drive_letter = parts[2].upper() + ':'
        windows_path = drive_letter + '/' + '/'.join(parts[3:])
        return windows_path
    return path 


def create_ccsproject_file(model):

    """ Creates a .ccsproject file in XML format for a given project.

    This function generates a `.ccsproject` file within a project-specific directory.
    The file is created in XML format and includes basic project options. The function ensures that the 
    directory exists before writing the file.

    Example Call:
    -------------
    create_ccsproject_file("exampleModel")

    Parameters:
    -----------
    model      : The name of the project for which the `.ccsproject` file is being created.

    Returns:
    --------
    -

    Example:
    --------
    Input:
        model = "exampleModel"

    Output:
        Creates a file `./exampleModel_project/.ccsproject` with the specified XML content.

    """
    
    project_dir = f"./{model}_project"
    ccsproject_file = os.path.join(project_dir, ".ccsproject")

    # Content of .ccsproject file
    ccsproject_content = (
        '<?xml version="1.0" encoding="UTF-8" ?>\n'
        '<?ccsproject version="1.0"?>\n'
        '<projectOptions>\n'
        '    <!-- Specifica il tipo di dispositivo che stai usando -->\n'
        '    <deviceVariant value="com.ti.ccstudio.deviceModel.C2000.GenericC28xxDevice"/>\n'
        '    <deviceFamily value="C2000"/>\n'
        '    <codegenToolVersion value="22.6.1.LTS"/>\n'
        '    <!-- Specifica il formato di output (non ELF in questo caso) -->\n'
        '    <isElfFormat value="false"/>\n\n'
        '    <connection value=""/>\n'
        '    <!-- Indica la libreria di runtime standard -->\n'
        '    <rts value="libc.a"/>\n\n'
        '    <templateProperties value="id=com.ti.common.project.core.emptyProjectTemplate,"/>\n'
        '    <isTargetManual value="false"/>\n'
        '</projectOptions>\n'
    )

    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Write the content in the .ccsproject file
    with open(ccsproject_file, 'w', encoding='utf-8') as file:
        file.write(ccsproject_content)


def create_project_file(model, c2000_path):

    """ Creates a .project file in XML format for a given project.

    This function generates a `.project` file in a project-specific directory.
    The file is formatted as XML and includes project settings.

    Example Call:
    -------------
    create_project_file("exampleModel", "C:/ti/c2000/C2000Ware_4_01_00_00")

    Parameters:
    -----------
    model      : The name of the project for which the `.project` file is being created.
    c2000_path : The path where the C2000Ware_4_01_00_00 folder is located.

    Returns:
    --------
    -

    Example:
    --------
    Input:
        model = "exampleModel"
        c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00""

    Output:
        Creates a file `./exampleModel_project/.project` with the specified XML content.

    """

    first_path = c2000_path + '/device_support/f2837xd/headers/source'
    second_path = c2000_path + '/device_support/f2837xd/common/source'

    # In windows it needs an extra '/' on a linux environment no
    if isInWSL:
         first_path = '/' + first_path
         second_path = '/' + second_path
        
    project_dir = f"./{model}_project"
    project_file = os.path.join(project_dir, ".project")

    # Build content of .project file
    project_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<projectDescription>\n'
        f'    <name>{model}</name>\n'
        '    <comment></comment>\n'
        '    <projects>\n'
        '    </projects>\n'
        '    <buildSpec>\n'
        '        <buildCommand>\n'
        '            <name>org.eclipse.cdt.managedbuilder.core.genmakebuilder</name>\n'
        '            <arguments>\n'
        '            </arguments>\n'
        '        </buildCommand>\n'
        '        <buildCommand>\n'
        '            <name>org.eclipse.cdt.managedbuilder.core.ScannerConfigBuilder</name>\n'
        '            <triggers>full,incremental,</triggers>\n'
        '            <arguments>\n'
        '            </arguments>\n'
        '        </buildCommand>\n'
        '    </buildSpec>\n'
        '    <natures>\n'
        '        <nature>com.ti.ccstudio.core.ccsNature</nature>\n'
        '        <nature>org.eclipse.cdt.core.cnature</nature>\n'
        '        <nature>org.eclipse.cdt.managedbuilder.core.managedBuildNature</nature>\n'
        '        <nature>org.eclipse.cdt.core.ccnature</nature>\n'
        '        <nature>org.eclipse.cdt.managedbuilder.core.ScannerConfigNature</nature>\n'
        '    </natures>\n'
        '    <linkedResources>\n'
        '        <link>\n'
        '            <name>F2837xD_CpuTimers.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_CpuTimers.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_Adc.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_Adc.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_CodeStartBranch.asm</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_CodeStartBranch.asm</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_DefaultISR.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_DefaultISR.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_GlobalVariableDefs.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{first_path}/F2837xD_GlobalVariableDefs.c</locationURI>\n'                
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_Gpio.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_Gpio.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_Ipc.c</name>\n'
        '            <type>1</type>\n'
        f'           <locationURI>file:{second_path}/F2837xD_Ipc.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_PieCtrl.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_PieCtrl.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_PieVect.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_PieVect.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_SysCtrl.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_SysCtrl.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_usDelay.asm</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:{second_path}/F2837xD_usDelay.asm</locationURI>\n'
        '        </link>\n'
        '    </linkedResources>\n'
        '    <variableList>\n'
        '        <variable>\n'
        '            <name>INSTALLROOT_F2837XD</name>\n'
        '            <value>$%7BPARENT-4-PROJECT_LOC%7D</value>\n'
        '        </variable>\n'
        '    </variableList>\n'
        '</projectDescription>\n'
    )

    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Write the content in the .project file
    with open(project_file, 'w', encoding='utf-8') as file:
        file.write(project_content)


def create_cproject_file(model, ti_path, c2000_path, include):

    """ Creates a .cproject file in XML format for a given project.

    This function generates a `.cproject` file in a project-specific directory.
    The file is created in XML format and includes detailed configuration settings. 

    Example Call:
    -------------
    create_cproject_file("exampleModel", "C:/ti", "C:/ti/c2000/C2000Ware_4_01_00_00", "C:/Users/name/Desktop/untitled_gen/untitled_project/include")

    Parameters:
    -----------
    model      : The name of the project for which the `.cproject` file is being created.
    ti_path    : The path where the ti folder is located.
    c2000_path : The path where the C2000Ware_4_01_00_00 folder is located.
    include    : The include directory of the project.

    Returns:
    --------
    -

    Example:
    --------
    Input:
        model = "exampleModel"
        ti_path = "C:/ti"
        c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"
        include = "C:/Users/name/Desktop/untitled_gen/untitled_project/include"

    Output:
        Creates a file `./exampleModel_project/.cproject` with the specified XML content.

    """

    project_dir = f"./{model}_project"
    cproject_file = os.path.join(project_dir, ".cproject")

    include_path = include
    linker_path1 = c2000_path + '/device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd'
    linker_path2 = c2000_path + '/device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd'

    first_headers_path = c2000_path + '/device_support/f2837xd/headers/include'
    second_headers_path = c2000_path + '/device_support/f2837xd/common/include'
    third_headers_path = ti_path + '/ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include'

    # Content of .cproject file
    cproject_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <?fileVersion 4.0.0?>
    <cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
        <storageModule configRelations="2" moduleId="org.eclipse.cdt.core.settings">
            <cconfiguration id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750">
                <storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750" moduleId="org.eclipse.cdt.core.settings" name="CPU1_RAM">
                    <macros>
                        <stringMacro name="INSTALLROOT_F2837XD" type="VALUE_PATH_DIR" value="${{PROJECT_ROOT}}/../../../../.."/>
                    </macros>
                    <externalSettings/>
                    <extensions>
                        <extension id="com.ti.ccstudio.binaryparser.CoffParser" point="org.eclipse.cdt.core.BinaryParser"/>
                        <extension id="com.ti.ccstudio.errorparser.CoffErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                        <extension id="com.ti.ccstudio.errorparser.LinkErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                        <extension id="com.ti.ccstudio.errorparser.AsmErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                        <extension id="org.eclipse.cdt.core.GmakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                    </extensions>
                </storageModule>
                <storageModule moduleId="cdtBuildSystem" version="4.0.0">
                    <configuration artifactExtension="out" artifactName="${{ProjName}}" buildProperties="" cleanCommand="${{CG_CLEAN_CMD}}" description="RAM Build Configuration w/Debugger Support for CPU1" id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750" name="CPU1_RAM" parent="com.ti.ccstudio.buildDefinitions.C2000.Debug">
                        <folderInfo id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750." name="/" resourcePath="">
                            <toolChain id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.DebugToolchain.1936615022" name="TI Build Tools" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.DebugToolchain" targetTool="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.linkerDebug.1604840405">
                                <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.core.OPT_TAGS.1614280783" superClass="com.ti.ccstudio.buildDefinitions.core.OPT_TAGS" valueType="stringList">
                                    <listOptionValue builtIn="false" value="DEVICE_CONFIGURATION_ID=com.ti.ccstudio.deviceModel.C2000.GenericC28xxDevice"/>
                                    <listOptionValue builtIn="false" value="DEVICE_CORE_ID="/>
                                    <listOptionValue builtIn="false" value="DEVICE_ENDIANNESS=little"/>
                                    <listOptionValue builtIn="false" value="OUTPUT_FORMAT=COFF"/>
                                    <listOptionValue builtIn="false" value="RUNTIME_SUPPORT_LIBRARY=libc.a"/>
                                    <listOptionValue builtIn="false" value="CCS_MBS_VERSION=6.1.3"/>
                                    <listOptionValue builtIn="false" value="OUTPUT_TYPE=executable"/>
                                    <listOptionValue builtIn="false" value="PRODUCTS="/>
                                    <listOptionValue builtIn="false" value="PRODUCT_MACRO_IMPORTS={{}}"/>
                                </option>
                                <option id="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION.1659874217" superClass="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION" value="22.6.1.LTS" valueType="string"/>
                                <targetPlatform id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.targetPlatformDebug.872252835" name="Platform" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.targetPlatformDebug"/>
                                <builder buildPath="${{BuildDirectory}}" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.builderDebug.523509514" name="GNU Make.CPU1_RAM" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.builderDebug"/>
                                <tool id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.compilerDebug.1225049945" name="C2000 Compiler" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.compilerDebug">
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.SILICON_VERSION.76848770" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.SILICON_VERSION" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.SILICON_VERSION.28" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.LARGE_MEMORY_MODEL.1426538618" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.LARGE_MEMORY_MODEL" value="true" valueType="boolean"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.UNIFIED_MEMORY.1204196634" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.UNIFIED_MEMORY" value="true" valueType="boolean"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.FLOAT_SUPPORT.912837455" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.FLOAT_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.FLOAT_SUPPORT.fpu32" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.CLA_SUPPORT.467689498" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.CLA_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.CLA_SUPPORT.cla1" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.TMU_SUPPORT.484008760" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.TMU_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.TMU_SUPPORT.tmu0" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.VCU_SUPPORT.1379050903" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.VCU_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.VCU_SUPPORT.vcu2" valueType="enumerated"/>

                                    <!-- Sezione Include Path -->
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.INCLUDE_PATH.1816198112" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.INCLUDE_PATH" valueType="includePath">
                                        <listOptionValue builtIn="false" value="{first_headers_path}"/>
                                        <listOptionValue builtIn="false" value="{second_headers_path}"/>
                                        <listOptionValue builtIn="false" value="{third_headers_path}"/>
                                        <listOptionValue builtIn="false" value="{include_path}"/>
                                    </option>

                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEBUGGING_MODEL.2023058995" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEBUGGING_MODEL" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEBUGGING_MODEL.SYMDEBUG__DWARF" valueType="enumerated"/>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEFINE.928837016" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEFINE" valueType="definedSymbols">
                                        <listOptionValue builtIn="false" value="CPU1"/>
                                    </option>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DISPLAY_ERROR_NUMBER.1888790822" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DISPLAY_ERROR_NUMBER" value="true" valueType="boolean"/>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DIAG_WARNING.1826112291" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DIAG_WARNING" valueType="stringList">
                                        <listOptionValue builtIn="false" value="225"/>
                                    </option>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.ABI.1734084811" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.ABI" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.ABI.coffabi" valueType="enumerated"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__C_SRCS.935175564" name="C Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__C_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__CPP_SRCS.1754916874" name="C++ Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__CPP_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__ASM_SRCS.966474163" name="Assembly Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__ASM_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__ASM2_SRCS.1331774997" name="Assembly Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compiler.inputType__ASM2_SRCS"/>
                                </tool>

                                <!-- Sezione Linker Config -->
                                <tool id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.linkerDebug.1604840405" name="C2000 Linker" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.linkerDebug">
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.MAP_FILE.150192862" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.MAP_FILE" value="&quot;${{ProjName}}.map&quot;" valueType="string"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.OUTPUT_FILE.508871516" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.OUTPUT_FILE" value="${{ProjName}}.out" valueType="string"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.STACK_SIZE.794155856" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.STACK_SIZE" value="0x100" valueType="string"/>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.LIBRARY.779473277" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.LIBRARY" valueType="libs">
                                        <listOptionValue builtIn="false" value="rts2800_fpu32.lib"/>
                                        <listOptionValue builtIn="false" value="{linker_path1}"/>
                                        <listOptionValue builtIn="false" value="{linker_path2}"/>
                                        <listOptionValue builtIn="false" value="libc.a"/>
                                    </option>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.SEARCH_PATH.1443810135" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.SEARCH_PATH" valueType="libPaths">
                                        <listOptionValue builtIn="false" value="${{CG_TOOL_ROOT}}/lib"/>
                                    </option>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.DISPLAY_ERROR_NUMBER.96471687" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.DISPLAY_ERROR_NUMBER" value="true" valueType="boolean"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.XML_LINK_INFO.1957298402" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.XML_LINK_INFO" value="&quot;${{ProjName}}_linkInfo.xml&quot;" valueType="string"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exeLinker.inputType__CMD_SRCS.1799253343" name="Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exeLinker.inputType__CMD_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exeLinker.inputType__CMD2_SRCS.478843577" name="Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exeLinker.inputType__CMD2_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exeLinker.inputType__GEN_CMDS.1897434562" name="Generated Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exeLinker.inputType__GEN_CMDS"/>
                                </tool>
                            </toolChain>
                        </folderInfo>
                    </configuration>
                </storageModule>
                <storageModule moduleId="org.eclipse.cdt.core.externalSettings"/>
            </cconfiguration>
        </storageModule>
        <storageModule moduleId="org.eclipse.cdt.core.LanguageSettingsProviders"/>
        <storageModule moduleId="cdtBuildSystem" version="4.0.0">
            <project id="adc_soc_software_dc_cpu01.com.ti.ccstudio.buildDefinitions.C2000.ProjectType.253935156" name="C2000" projectType="com.ti.ccstudio.buildDefinitions.C2000.ProjectType"/>
        </storageModule>
        <storageModule moduleId="scannerConfiguration"/>
        <storageModule moduleId="org.eclipse.cdt.core.language.mapping">
            <project-mappings>
                <content-type-mapping configuration="" content-type="org.eclipse.cdt.core.asmSource" language="com.ti.ccstudio.core.TIASMLanguage"/>
                <content-type-mapping configuration="" content-type="org.eclipse.cdt.core.cHeader" language="com.ti.ccstudio.core.TIGCCLanguage"/>
                <content-type-mapping configuration="" content-type="org.eclipse.cdt.core.cSource" language="com.ti.ccstudio.core.TIGCCLanguage"/>
                <content-type-mapping configuration="" content-type="org.eclipse.cdt.core.cxxHeader" language="com.ti.ccstudio.core.TIGPPLanguage"/>
                <content-type-mapping configuration="" content-type="org.eclipse.cdt.core.cxxSource" language="com.ti.ccstudio.core.TIGPPLanguage"/>
            </project-mappings>
        </storageModule>
        <storageModule moduleId="null.endianPreference"/>
        <storageModule moduleId="cpuFamily"/>
        <storageModule moduleId="org.eclipse.cdt.make.core.buildtargets"/>
    </cproject>
    '''

    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Write the content in the .cproject file
    with open(cproject_file, 'w', encoding='utf-8') as file:
        file.write(cproject_content)


def advise(title, message):

    """
    Displays a customizable confirmation dialog with a scrollable message and "Yes"/"No" buttons.

    This function creates a modal dialog using PyQt, allowing users to read a detailed message
    and make a choice between "Yes" and "No." The dialog includes a scrollable text area for long messages
    and a title to provide context.

    Parameters
    ----------
    title   : The title of the dialog window.
    message : The message to display inside the scrollable text area.

    Returns
    -------
    bool    : True if the user clicks "Yes," False if the user clicks "No."
    """

    app = QApplication.instance() or QApplication([])
    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.resize(600, 400)

    layout = QVBoxLayout()

    label = QLabel(title)
    label.setStyleSheet("font-weight: bold; font-size: 16px;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    text_widget = QTextEdit()
    text_widget.setPlainText(message)
    text_widget.setReadOnly(True)
    scroll_area.setWidget(text_widget)

    button_layout = QHBoxLayout()
    yes_button = QPushButton("Yes")
    no_button = QPushButton("No")

    response = []

    yes_button.clicked.connect(lambda: (response.append(True), dialog.accept()))
    no_button.clicked.connect(lambda: (response.append(False), dialog.reject()))

    button_layout.addWidget(yes_button)
    button_layout.addWidget(no_button)

    layout.addWidget(label)
    layout.addWidget(scroll_area)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.exec()
    return response[0] if response else False


def update_paths(ti_path, c2000_path):

    """ Updates paths based on the new values of `ti_path` and `c2000_path`.

    This function creates a dictionary with updated paths using the provided
    `ti_path` and `c2000_path` values. The paths are constructed for 
    specific project files and directories, including linker, headers, and 
    source files.

    Example Call:
    -------------
    paths = update_paths("C:/ti","C:/ti/c2000/C2000Ware_4_01_00_00")

    Parameters:
    -----------
    ti_path    : The path where the ti folder is located.
    c2000_path : The path where the C2000Ware_4_01_00_00 folder is located.

    Returns:
    --------
    dict       : A dictionary containing updated paths.

    """
    
    paths_to_check = {
        "linker_path1": os.path.join(c2000_path, 'device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd'),
        "linker_path2": os.path.join(c2000_path, 'device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd'),
        "first_headers_path": os.path.join(c2000_path, 'device_support/f2837xd/headers/include'),
        "second_headers_path": os.path.join(c2000_path, 'device_support/f2837xd/common/include'),
        "third_headers_path": os.path.join(ti_path, 'ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include'),
        "first_source_path": os.path.join(c2000_path, 'device_support/f2837xd/headers/source'),
        "second_source_path": os.path.join(c2000_path, 'device_support/f2837xd/common/source')
    }
    return paths_to_check


def check_paths(ti_path, c2000_path):
    
    """ Verifies and updates required paths and files for the project configuration.

    This function checks if essential paths and files, based on `ti_path` and `c2000_path`,
    are accessible. If the environment is WSL, paths are converted accordingly.
    Missing paths or files trigger user prompts to either update paths or delete the
    configuration file. The function loops until all paths and files are verified.

    Example Call:
    -------------
    check_paths("C:/ti","C:/ti/c2000/C2000Ware_4_01_00_00")

    Parameters:
    -----------
    ti_path    : The path where the ti folder is located.
    c2000_path : The path where the C2000Ware_4_01_00_00 folder is located.

    Returns:
    --------
    -
     
    """

    if isInWSL:
        ti_path = convert_path_for_wsl(ti_path)
        c2000_path = convert_path_for_wsl(c2000_path)

    def update_paths(ti_path, c2000_path):
        return {
            "linker_path1": os.path.join(c2000_path, 'device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd'),
            "linker_path2": os.path.join(c2000_path, 'device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd'),
            "first_headers_path": os.path.join(c2000_path, 'device_support/f2837xd/headers/include'),
            "second_headers_path": os.path.join(c2000_path, 'device_support/f2837xd/common/include'),
            "third_headers_path": os.path.join(ti_path, 'ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include'),
            "first_source_path": os.path.join(c2000_path, 'device_support/f2837xd/headers/source'),
            "second_source_path": os.path.join(c2000_path, 'device_support/f2837xd/common/source')
        }

    paths_to_check = update_paths(ti_path, c2000_path)

    # Check if the paths exist.
    while True:
        
        missing_paths = [f"{path_name}: {path}" for path_name, path in paths_to_check.items() if not os.path.exists(path)]

        # If there are missing paths, ask to update them or delete the config.json file
        if missing_paths:
            missing_paths_str = "\n\n".join(missing_paths)
            response = advise(
                "The following paths are missing:",
                f"{missing_paths_str}\n\nDo you want to change paths (Yes) or delete the {general_config.get_name()} file (No)"
            )
            if response:
                open_config_window()

                # Reload updated paths from new configuration
                config = general_config.load()
                ti_path_update = config.get('ti_path', '')
                c2000_path_update = config.get('c2000Ware_path', '')

                if isInWSL:
                    ti_path_update = convert_path_for_wsl(ti_path_update)
                    c2000_path_update = convert_path_for_wsl(c2000_path_update)

                # Update the paths to check with the new values
                paths_to_check = update_paths(ti_path_update, c2000_path_update)
            else:
                general_config.delete()
                QMessageBox.information(None, "Configuration", f"{general_config.get_name()} has been deleted.")
                return
        else:
            file_name = 'F2837xD_GlobalVariableDefs.c'
            file_path = os.path.join(paths_to_check["first_source_path"], file_name)
            missing_files = []
            if not os.path.isfile(file_path):
                missing_files.append(file_name)

            required_files = [
                'F2837xD_CpuTimers.c', 'F2837xD_CodeStartBranch.asm', 'F2837xD_DefaultISR.c',
                'F2837xD_Gpio.c', 'F2837xD_Ipc.c', 'F2837xD_PieCtrl.c', 'F2837xD_PieVect.c',
                'F2837xD_SysCtrl.c', 'F2837xD_usDelay.asm'
            ]

            # Add any other missing files to the list
            missing_files += [
                file for file in required_files
                if not os.path.isfile(os.path.join(paths_to_check["second_source_path"], file))
            ]

            if missing_files:
                missing_message = "The following files are missing:\n\n"
                for file in missing_files:
                    if "GlobalVariable" in file:

                        # Specific path for F2837xD_GlobalVariableDefs.c
                        missing_message += f"{file} in {paths_to_check['first_source_path']}\n\n"
                    else:

                        # Path to other files in second_source_path
                        missing_message += f"{file} in {paths_to_check['second_source_path']}\n\n"
                missing_message += "\n\n"

                response = advise(
                    "Missing Files",
                    f"{missing_message}Do you want to delete the {general_config.get_name()} file (Yes) or not (No)"
                )

                if response:
                    delete_config_file()
                    return 
                else:
                    return
            else:
                QMessageBox.information(None, "Paths and Files Check", "All required paths and files are present.")
                break


def press_configure_button():
    
    """
    Handles the configuration setup triggered by the configure button.

    This function checks the environment (e.g., WSL detection) and opens a configuration 
    window for the user to set or adjust settings. If the configuration is saved, it 
    proceeds to validate paths for necessary resources.
    
    Example Call:
    -------------
    press_configure_button()

    Parameters:
    -----------
    -

    Returns:
    --------
    -
    """

    check_wsl_environment()
    app = QApplication.instance() or QApplication([])

    # Open the configuration window
    if not open_config_window():
        return

    # Continue only if the configuration has been saved
    config = general_config.load()
    ti_path = config.get('ti_path', '')
    c2000Ware_path = config.get('c2000Ware_path', '')

    check_paths(ti_path, c2000Ware_path)


def check_blocks_set(blocks):

    """
    Analyzes blocks and returns a set of functions used.

    This function iterates through a list of blocks, extracts their associated 
    functions (if available), and returns them as a set.

    Example Call:
    -------------
    result = check_blocks_set(blocks)

    Parameters:
    -----------
    blocks : List of blocks.

    Returns:
    --------
    set    : Set of functions associated with the provided blocks.
    """

    block_functions = set()

    for block in blocks:
        block_function = getattr(block, 'fcn', 'N/A')

        if block_function != 'N/A':
            block_functions.add(block_function)

    return block_functions


def check_blocks_list(blocks):

    """
    Analyzes blocks and returns a list of functions used, including duplicates.

    This function iterates through a list of blocks, extracts their associated 
    functions (if available), and returns them as a list, preserving duplicates.

    Example Call:
    -------------
    result = check_blocks_list(blocks)

    Parameters:
    -----------
    blocks  : List of blocks.

    Returns:
    --------
    list    : List of functions associated with the provided blocks, including duplicates.
    """

    block_functions = []

    for block in blocks:
        block_function = getattr(block, 'fcn', 'N/A')

        if block_function != 'N/A':
            block_functions.append(block_function)

    return block_functions


def find_and_copy_files(function_names, CodeGen_path, dest_c_dir, dest_h_dir):
    
    """
    Finds and copies required source and header files for specified functions.

    This function scans the given `CodeGen_path` directory for source (`.c`) 
    and header (`.h`) files related to the provided `function_names`. It applies 
    special rules for certain functions and copies the matched files to the 
    specified destination directories for source and header files.

    Example Call:
    -------------
    files = find_and_copy_files(function_names, CodeGen_path, dest_c_dir, dest_h_dir)

    Parameters:
    -----------
    function_names : List of function names for which files need to be located and copied.
    CodeGen_path   : Path to the directory where the source and header files are located.
    dest_c_dir     : Destination directory for `.c` files.
    dest_h_dir     : Destination directory for `.h` files.

    Returns:
    --------
    dict           : A dictionary where each function is mapped to its associated `.c` and `.h` file paths (if found).

    Example:
        {
            "adcblk": {"c_file": "/path/to/adcblk.c", "h_file": "/path/to/adc.h"},
            "step": {"c_file": "/path/to/input.c", "h_file": None},
        }
    """

    print(f"Function names to process: {function_names}")    

    found_files = {}
    os.makedirs(dest_c_dir, exist_ok=True)
    os.makedirs(dest_h_dir, exist_ok=True)

    # Special rules for specific functions
    special_cases = {
        "adcblk": ["adcblk.c", "adc.c", "adc.h"],
        "inputGPIOblk": ["inputGPIOblk.c", "button.c", "button.h"],
        "outputGPIOblk": ["outputGPIOblk.c", "ledDelfino.c", "led.h"],
        "epwmblk": ["epwmblk.c", "epwm.c", "epwm.h"],
        "step": ["input.c"],
        "sinus": ["input.c"],
        "squareSignal": ["input.c"],
        "constant": ["input.c"],
        "absV":["nonlinear.c"],
        "lut":["nonlinear.c"],
        "saturation":["nonlinear.c"],
        "switcher":["switch.c"],
        "trigo":["nonlinear.c"],
        "print":["output.c"]
    }

    for function in function_names:
        found_files[function] = {"c_file": None, "h_file": None}

        # Determine which files to search (special or standard)
        files_to_search = special_cases.get(function, [f"{function}.c"])

        # Search and copy files
        for file_name in files_to_search:
            dest_dir = dest_c_dir if file_name.endswith(".c") else dest_h_dir
            for root, _, files in os.walk(CodeGen_path):
                if file_name in files:
                    source_path = os.path.join(root, file_name)
                    dest_path = os.path.join(dest_dir, file_name)
                    shutil.copy(source_path, dest_path)
                    key = "c_file" if file_name.endswith(".c") else "h_file"
                    found_files[function][key] = dest_path
                    break

    return found_files


def dispatch_main_generation(state, path_main, model, timer_period, tbprd, pwm_output):
    """
    Dispatches the generation of `main.c` based on the provided state.

    This function selects the appropriate generation routine for `main.c` 
    depending on the given state and configuration parameters.

    Example Call:
    -------------
    dispatch_main_generation(1, "path/to/main.c", "model_name", 100, 1500, "PWM1")

    Parameters:
    -----------
    state         : int
        Current configuration state:
        - 1: Mode 1 with Timer
        - 2: Mode 1 with ePWM
        - 3: Mode 2 with Timer
        - 4: Mode 2 with ePWM

    path_main    : Full path to the `main.c` file to be generated.
    model        : Name of the model being used for generation.
    timer_period : Timer period in microseconds (used in Timer-based modes).
    tbprd        : value of register tbprd (for pwm period).
    pwm_output   : Identifier of the PWM output (e.g., "PWM1", "PWM2").

    Returns:
    --------
    -
    """

    if state == 1:
        generate_main_mode1_timer(path_main, model, timer_period)
    elif state == 2:
        generate_main_mode1_epwm(path_main, model, tbprd, pwm_output)
    elif state == 3:
        generate_main_mode2_timer(path_main, model, timer_period)
    elif state == 4:
        generate_main_mode2_epwm(path_main, model, tbprd, pwm_output)


 # state 1
def generate_main_mode1_timer(path_main, model, timer_period):
    
    """
    Generates the main.c file for Mode 1 using Timer interrupts.

    Example Call:
    -------------
    generate_main_mode1_timer("path/to/main.c", "model_name", 1000)

    Parameters:
    -----------
    path_main    : Path to the output main.c file.
    model        : Name of the model to integrate into the main program.
    timer_period : Timer period in microseconds.

    Returns:
    --------
    -
    """

    Tsamp = float(timer_period)/1000000

    with open(path_main, 'w') as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   main.c\n")
        f.write("// TITLE:  CPU Timers Example for F2837xD.\n")
        f.write("//###########################################################################\n\n")
    
        f.write('#include "F28x_Project.h"\n\n')
    
        # Function prototypes
        f.write("__interrupt void cpu_timer0_isr(void);\n")
        f.write("void setup(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n\n")
    
        # Global variables
        f.write(f"static double Tsamp = {Tsamp};  // Intervallo temporale\n")
        f.write("static double T = 0.0;         // Tempo corrente\n\n")
    
        # Main function
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    while (1) {}\n")
        f.write(f"    {model}_end();\n")
        f.write("}\n\n")
    
        # ISR of Timer0
        f.write("__interrupt void cpu_timer0_isr(void)\n")
        f.write("{\n")
        f.write("    CpuTimer0.InterruptCount++;\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")
    
        # Initial setup
        f.write("void setup(void)\n")
        f.write("{\n")
        f.write("    InitSysCtrl();\n")
        f.write("    InitGpio();\n")
        f.write(f"    {model}_init();\n\n")
        f.write("    DINT;\n")
        f.write("    InitPieCtrl();\n")
        f.write("    IER = 0x0000;\n")
        f.write("    IFR = 0x0000;\n")
        f.write("    InitPieVectTable();\n\n")
        f.write("    EALLOW;\n")
        f.write("    PieVectTable.TIMER0_INT = &cpu_timer0_isr;\n")
        f.write("    EDIS;\n\n")
        f.write("    InitCpuTimers();\n")
        f.write(f"    ConfigCpuTimer(&CpuTimer0, 100, {timer_period});\n")
        f.write("    CpuTimer0Regs.TCR.all = 0x4000;\n\n")
        f.write("    IER |= M_INT1;\n")
        f.write("    PieCtrlRegs.PIEIER1.bit.INTx7 = 1;\n\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n\n")
        f.write("    EALLOW;\n")
        f.write("    // Set EPWMCLKDIV to 0 to have the ePWM input clock run at full PLLSYSCLK (100 MHz).\n")
        f.write("    // Without this, the ePWM clock frequency is divided by 2 (resulting in 50 MHz).\n")
        f.write("    ClkCfgRegs.PERCLKDIVSEL.bit.EPWMCLKDIV = 0;\n")
        f.write("    EDIS;\n")
        f.write("}\n\n")
    
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
    
        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")


#state 2
def generate_main_mode1_epwm(path_main, model, tbprd, pwm_output):
    
    """
    Generates the main.c file for Mode 1 using an ePWM module.

    Example Call:
    -------------
    generate_main_mode1_epwm("path/to/main.c", "model_name", 5000, "out1a")

    Parameters:
    -----------
    path_main   : Path to the output main.c file.
    model       : Name of the model to integrate into the main program.
    tbprd       : Timer base period register value for ePWM.
    pwm_output  : Specifies the ePWM output channel (e.g., "out1a", "out1b").

    Returns:
    --------
    -
    """

    pwm_period = (2 * int(tbprd)) / 1e8

    if pwm_output == "out1a" or pwm_output == "out1b":
        number_epwm = "epwm1"
        number_epwm_capsLock = "EPWM1"
        number_epwm_digit = 1
        epwm_regs = "EPwm1Regs"

    elif pwm_output == "out2a" or pwm_output == "out2b":
        number_epwm = "epwm2"
        number_epwm_capsLock = "EPWM2"
        number_epwm_digit = 2
        epwm_regs = "EPwm2Regs"

    elif pwm_output == "out3a" or pwm_output == "out3b":
        number_epwm = "epwm3"
        number_epwm_capsLock = "EPWM3"
        number_epwm_digit = 3
        epwm_regs = "EPwm3Regs"    

    elif pwm_output == "out4a" or pwm_output == "out4b":
        number_epwm = "epwm4"
        number_epwm_capsLock = "EPWM4"
        number_epwm_digit = 4
        epwm_regs = "EPwm4Regs"

    elif pwm_output == "out5a" or pwm_output == "out5b":
        number_epwm = "epwm5"
        number_epwm_capsLock = "EPWM5"
        number_epwm_digit = 5
        epwm_regs = "EPwm5Regs"

    elif pwm_output == "out6a" or pwm_output == "out6b":
        number_epwm = "epwm6"
        number_epwm_capsLock = "EPWM6"
        number_epwm_digit = 6
        epwm_regs = "EPwm6Regs"

    elif pwm_output == "out7a" or pwm_output == "out7b":
        number_epwm = "epwm7"
        number_epwm_capsLock = "EPWM7"
        number_epwm_digit = 7
        epwm_regs = "EPwm7Regs"

    elif pwm_output == "out8a" or pwm_output == "out8b":
        number_epwm = "epwm8"
        number_epwm_capsLock = "EPWM8"
        number_epwm_digit = 8
        epwm_regs = "EPwm8Regs"

    elif pwm_output == "out9a" or pwm_output == "out9b":
        number_epwm = "epwm9"
        number_epwm_capsLock = "EPWM9"
        number_epwm_digit = 9
        epwm_regs = "EPwm9Regs"

    elif pwm_output == "out10a" or pwm_output == "out10b":
        number_epwm = "epwm10"
        number_epwm_capsLock = "EPWM10"
        number_epwm_digit = 10
        epwm_regs = "EPwm10Regs"

    elif pwm_output == "out11a" or pwm_output == "out11b":
        number_epwm = "epwm11"
        number_epwm_capsLock = "EPWM11"
        number_epwm_digit = 11
        epwm_regs = "EPwm11Regs"

    elif pwm_output == "out12a" or pwm_output == "out12b":
        number_epwm = "epwm12"
        number_epwm_capsLock = "EPWM12"
        number_epwm_digit = 12
        epwm_regs = "EPwm12Regs"

    with open(path_main, "w") as f:
        f.write('#include "F28x_Project.h"\n\n')

        # Function prototypes
        f.write(f"__interrupt void {number_epwm}_isr(void);\n")
        f.write("void setup(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n\n")

        # Global variables
        f.write(f"static double Tsamp = {pwm_period}; // Intervallo temporale\n")
        f.write("static double T = 0.0;         // Tempo corrente\n\n")

        # Main function
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    while (1) {}\n")
        f.write(f"    {model}_end();\n")
        f.write("}\n\n")

        # ISR for ePWM
        f.write(f"__interrupt void {number_epwm}_isr(void)\n")
        f.write("{\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n\n")
        f.write("    // Clear the interrupt flag for ePWM\n")
        f.write(f"    {epwm_regs}.ETCLR.bit.INT = 1;\n\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP3;\n")
        f.write("}\n\n")

        # Setup function
        f.write("void setup(void)\n")
        f.write("{\n")
        f.write("    InitSysCtrl();\n")
        f.write("    InitGpio();\n")
        f.write(f"    {model}_init();\n\n")
        f.write("    DINT;\n")
        f.write("    InitPieCtrl();\n")
        f.write("    IER = 0x0000;\n")
        f.write("    IFR = 0x0000;\n")
        f.write("    InitPieVectTable();\n\n")
        f.write("    // Link ISR to ePWM1 interrupt\n")
        f.write("    EALLOW;\n")
        f.write(f"    PieVectTable.{number_epwm_capsLock}_INT = &{number_epwm}_isr;\n")
        f.write("    EDIS;\n\n")

        # Interrupt configuration
        f.write("    // Enable ePWM interrupt in PIE group 3\n")
        f.write(f"    PieCtrlRegs.PIEIER3.bit.INTx{number_epwm_digit} = 1;\n\n")
        f.write("    // Enable CPU interrupt group 3\n")
        f.write("    IER |= M_INT3;\n\n")
        f.write("    // Enable global interrupts and real-time interrupts\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n\n")
        f.write("    // Interrupt Setup\n")
        f.write("    // l'interrupt viene generato una volta per ogni ciclo completo del periodo.\n")
        f.write(f"    {epwm_regs}.ETSEL.bit.INTSEL = ET_CTR_ZERO;    // Trigger interrupt a TBCTR = 0\n")
        f.write(f"    {epwm_regs}.ETSEL.bit.INTEN = 1;               // Abilita l'interrupt\n")
        f.write(f"    {epwm_regs}.ETPS.bit.INTPRD = ET_1ST;          // Genera interrupt ad ogni evento\n\n")

        # Clock configuration for ePWM
        f.write("    EALLOW;\n")
        f.write("    // Set EPWMCLKDIV to 0 to have the ePWM input clock run at full PLLSYSCLK (100 MHz).\n")
        f.write("    // Without this, the ePWM clock frequency is divided by 2 (resulting in 50 MHz).\n")
        f.write("    ClkCfgRegs.PERCLKDIVSEL.bit.EPWMCLKDIV = 0;\n")
        f.write("    EDIS;\n")
        f.write("}\n\n")

        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")


# state 3
def generate_main_mode2_timer(path_main, model, timer_period):

    """
    Generates the main.c file for Mode 2 with Timer-based ADC triggering.

    Example Call:
    -------------
    generate_main_mode2_timer(path_main="/path/to/main.c", model="exampleModel", timer_period=10000)

    Parameters:
    -----------
    path_main    : The file path where the main.c file will be generated.
    model        :  The name of the project for which the file is generated.
    timer_period : The timer period in microseconds for sampling intervals.

    Returns:
    --------
    -
    """

    Tsamp = float(timer_period)/1000000

    with open(path_main, 'w') as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   main.c\n")
        f.write("// TITLE:  CPU Timers Example for F2837xD.\n")
        f.write("//###########################################################################\n\n")
    
        f.write('#include "F28x_Project.h"\n\n')

        # Function Prototypes
        f.write("// Function Prototypes\n")
        f.write("void setup(void);\n")
        f.write("void ConfigureADC(void);\n")
        f.write("__interrupt void adca1_isr(void);\n")
        f.write("__interrupt void cpu_timer0_isr(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n\n")

        # Defines
        f.write("// Defines\n")
        f.write("#define RESULTS_BUFFER_SIZE 256\n\n")

        # Globals
        f.write("// Globals\n")
        f.write("Uint16 AdcaResults[RESULTS_BUFFER_SIZE];\n")
        f.write("Uint16 resultsIndex = 0;\n")
        f.write("volatile Uint16 bufferFull = 0;\n")
        f.write(f"static double Tsamp = {Tsamp};  // Sample interval\n")
        f.write("static double T = 0.0;       // Current time\n\n")

        # Main function
        f.write("void main(void)\n{\n")
        f.write("    setup();\n")
        f.write("    while (1)\n")
        f.write("    {\n")
        f.write("        if (bufferFull)\n")
        f.write("        {\n")
        f.write("            bufferFull = 0;\n")
        f.write('            asm("   ESTOP0"); // Breakpoint\n')
        f.write("        }\n")
        f.write("    }\n")
        f.write(f"    {model}_end(); // Clean-up from PySimCoder blocks\n")
        f.write("}\n\n")

        # Timer ISR
        f.write("__interrupt void cpu_timer0_isr(void)\n{\n")
        f.write("    CpuTimer0.InterruptCount++;\n")
        f.write("    AdcaRegs.ADCSOCFRC1.bit.SOC0 = 1; // Force start ADC conversion on SOC0\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1; // Acknowledge interrupt in PIE\n")
        f.write("}\n\n")

        # ADC ISR
        f.write("int cnt;\n")
        f.write("__interrupt void adca1_isr(void)\n{\n")
        f.write("    cnt++;\n")
        f.write("    AdcaResults[resultsIndex++] = AdcaResultRegs.ADCRESULT0;\n")
        f.write("    if (resultsIndex >= RESULTS_BUFFER_SIZE)\n")
        f.write("    {\n")
        f.write("        resultsIndex = 0;\n")
        f.write("        bufferFull = 1;\n")
        f.write("    }\n")
        f.write("    AdcaRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")

        # Setup Function
        f.write("void setup(void)\n{\n")
        f.write("    InitSysCtrl();\n")
        f.write("    InitGpio();\n")
        f.write(f"    {model}_init();\n\n")
        f.write("    DINT;\n")
        f.write("    InitPieCtrl();\n")
        f.write("    IER = 0x0000;\n")
        f.write("    IFR = 0x0000;\n")
        f.write("    InitPieVectTable();\n\n")
        f.write("    EALLOW;\n")
        f.write("    PieVectTable.TIMER0_INT = &cpu_timer0_isr;\n")
        f.write("    PieVectTable.ADCA1_INT = &adca1_isr;\n")
        f.write("    EDIS;\n\n")
        f.write("    ConfigureADC();\n\n")
        f.write("    InitCpuTimers();\n")
        f.write(f"    ConfigCpuTimer(&CpuTimer0, 100, {timer_period});\n")
        f.write("    CpuTimer0Regs.TCR.all = 0x4000;\n\n")
        f.write("    IER |= M_INT1;\n")
        f.write("    PieCtrlRegs.PIEIER1.bit.INTx7 = 1;\n")
        f.write("    PieCtrlRegs.PIEIER1.bit.INTx1 = 1;\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n\n")
        f.write("    EALLOW;\n")
        f.write("    // Set EPWMCLKDIV to 0 to have the ePWM input clock run at full PLLSYSCLK (100 MHz).\n")
        f.write("    // Without this, the ePWM clock frequency is divided by 2 (resulting in 50 MHz).\n")
        f.write("    ClkCfgRegs.PERCLKDIVSEL.bit.EPWMCLKDIV = 0;\n")
        f.write("    EDIS;\n")
        f.write("}\n\n")

        # ADC Configuration
        f.write("void ConfigureADC(void)\n{\n")
        f.write("    EALLOW;\n")
        f.write("    AdcaRegs.ADCCTL2.bit.PRESCALE = 6;\n")
        f.write("    AdcSetMode(ADC_ADCA, ADC_RESOLUTION_12BIT, ADC_SIGNALMODE_SINGLE);\n")
        f.write("    AdcaRegs.ADCCTL1.bit.INTPULSEPOS = 1;\n")
        f.write("    AdcaRegs.ADCCTL1.bit.ADCPWDNZ = 1;\n")
        f.write("    DELAY_US(1000);\n")
        f.write("    AdcaRegs.ADCSOC0CTL.bit.CHSEL = 0;\n")
        f.write("    AdcaRegs.ADCSOC0CTL.bit.ACQPS = 14;\n")
        f.write("    AdcaRegs.ADCSOC0CTL.bit.TRIGSEL = 0;\n")
        f.write("    AdcaRegs.ADCINTSEL1N2.bit.INT1SEL = 0;\n")
        f.write("    AdcaRegs.ADCINTSEL1N2.bit.INT1E = 1;\n")
        f.write("    AdcaRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;\n")
        f.write("    EDIS;\n")
        f.write("}\n\n")

        # Helper Functions
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")

        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")


# state 4
def generate_main_mode2_epwm(path_main, model, tbprd, pwm_output):

    """
    Generates the main.c file for Mode 2 with ePWM-based ADC triggering.

    Example Call:
    -------------
    generate_main_mode2_epwm(path_main="/path/to/main.c", model="exampleModel", tbprd=2000, pwm_output="out1a")

    Parameters:
    -----------
    path_main   : The file path where the main.c file will be generated.
    model       : The name of the project for which the file is generated.
    tbprd       : Time-base period for ePWM in clock cycles.
    pwm_output  : The ePWM output channel (e.g., "out1a", "out2b") used for ADC triggering.

    Returns:
    --------
    -
    """

    pwm_period = (2 * int(tbprd)) / 1e8
    
    if pwm_output == "out1a" or pwm_output == "out1b":
        epwmRegs = "EPwm1Regs"
        triggerOnePWM = 5

    elif pwm_output == "out2a" or pwm_output == "out2b":
        epwmRegs = "EPwm2Regs"
        triggerOnePWM = 7

    elif pwm_output == "out3a" or pwm_output == "out3b":
        epwmRegs = "EPwm3Regs"
        triggerOnePWM = 9

    elif pwm_output == "out4a" or pwm_output == "out4b":
        epwmRegs = "EPwm4Regs"
        triggerOnePWM = 11

    elif pwm_output == "out5a" or pwm_output == "out5b":
        epwmRegs = "EPwm5Regs"
        triggerOnePWM = 13

    elif pwm_output == "out6a" or pwm_output == "out6b":
        epwmRegs = "EPwm6Regs"
        triggerOnePWM = 15

    elif pwm_output == "out7a" or pwm_output == "out7b":
        epwmRegs = "EPwm7Regs"
        triggerOnePWM = 17

    elif pwm_output == "out8a" or pwm_output == "out8b":
        epwmRegs = "EPwm8Regs"
        triggerOnePWM = 19

    elif pwm_output == "out9a" or pwm_output == "out9b":
        epwmRegs = "EPwm9Regs"
        triggerOnePWM = 21

    elif pwm_output == "out10a" or pwm_output == "out10b":
        epwmRegs = "EPwm10Regs"
        triggerOnePWM = 23

    elif pwm_output == "out11a" or pwm_output == "out11b":
        epwmRegs = "EPwm11Regs"
        triggerOnePWM = 25

    elif pwm_output == "out12a" or pwm_output == "out12b":
        epwmRegs = "EPwm12Regs"
        triggerOnePWM = 27

    with open(path_main, "w") as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   adc_soc_epwm_cpu01.c\n")
        f.write("// TITLE:  CPU Timers Example for F2837xD.\n")
        f.write("//###########################################################################\n\n")
    
        # Included Files
        f.write("// Included Files\n")
        f.write('#include "F28x_Project.h"\n')
    
        # Function Prototypes
        f.write("// Function Prototypes\n")
        f.write("void ConfigureADC(void);\n")
        f.write("void SetupADCEpwm(Uint16 channel);\n")
        f.write("void setup(void);\n")
        f.write("void loop(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n\n")
        f.write("interrupt void adca1_isr(void);\n\n")
    
        # Defines and Globals
        f.write("// Defines\n")
        f.write("#define RESULTS_BUFFER_SIZE 256\n\n")
        f.write("// Globals\n")
        f.write("Uint16 AdcaResults[RESULTS_BUFFER_SIZE];\n")
        f.write("Uint16 resultsIndex;\n")
        f.write("volatile Uint16 bufferFull;\n")
        f.write(f"static double Tsamp = {pwm_period}; // Intervallo temporale\n")
        f.write("static double T = 0.0;         // Tempo corrente\n\n")
    
        # Main Function
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    loop();\n")
        f.write("}\n\n")
    
        # adca1_isr Function
        f.write("// adca1_isr - Read ADC Buffer in ISR\n")
        f.write("// Everytime ADC complete a conversion, the value is memorized in the AdcaResults buffer.\n")
        f.write("interrupt void adca1_isr(void)\n")
        f.write("{\n")
        f.write("    AdcaResults[resultsIndex++] = AdcaResultRegs.ADCRESULT0;\n")
        f.write("    if(RESULTS_BUFFER_SIZE <= resultsIndex)\n")
        f.write("    {\n")
        f.write("        resultsIndex = 0;\n")
        f.write("        bufferFull = 1;\n")
        f.write("    }\n\n")
        f.write("    AdcaRegs.ADCINTFLGCLR.bit.ADCINT1 = 1; //clear INT1 flag\n\n")
        f.write("    // Check if overflow has occurred\n")
        f.write("    if(1 == AdcaRegs.ADCINTOVF.bit.ADCINT1)\n")
        f.write("    {\n")
        f.write("        AdcaRegs.ADCINTOVFCLR.bit.ADCINT1 = 1; //clear INT1 overflow flag\n")
        f.write("        AdcaRegs.ADCINTFLGCLR.bit.ADCINT1 = 1; //clear INT1 flag\n")
        f.write("    }\n\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")

        # Setup Function
        f.write("void setup(void)\n")
        f.write("{\n")
        f.write("    InitSysCtrl();       // Initialize the CPU\n")
        f.write("    InitGpio();          // Initialize the GPIO\n\n")
        f.write("    DINT;                // Disable interrupts\n\n")
        f.write("    // Initialize the PIE control registers to their default state.\n")
        f.write("    InitPieCtrl();\n\n")
        f.write("    // Disable CPU interrupts and clear all CPU interrupt flags:\n")
        f.write("    IER = 0x0000;\n")
        f.write("    IFR = 0x0000;\n\n")
        f.write("    // Initialize the PIE vector table with pointers to the shell Interrupt\n")
        f.write("    InitPieVectTable();\n\n")
        f.write("    // Map ISR functions\n")
        f.write("    EALLOW;\n")
        f.write("    PieVectTable.ADCA1_INT = &adca1_isr;  // function for ADCA interrupt 1\n")
        f.write("    EDIS;\n\n")
        f.write("    ConfigureADC();\n\n")
        f.write("    EALLOW;\n")
        f.write(f"    {epwmRegs}.ETSEL.bit.SOCAEN = 0; // Disable SOC on A group\n")
        f.write(f"    {epwmRegs}.ETSEL.bit.SOCASEL = 4;// Select SOC on up-count\n")
        f.write(f"    {epwmRegs}.ETPS.bit.SOCAPRD = 1; // Generate pulse on 1st event\n")
        f.write("    EDIS;\n\n")
        f.write(f"    {model}_init();      // Initialize blocks generated by PySimCoder\n\n")
        f.write("    EALLOW;\n")
        f.write(f"    {epwmRegs}.TBCTL.bit.CTRMODE = 3; // freeze counter\n")
        f.write("    EDIS;\n\n")
        f.write("    // Setup the ADC for ePWM triggered conversions on channel 0\n")
        f.write("    SetupADCEpwm(0);\n\n")
        f.write("    // Enable global Interrupts and higher priority real-time debug events:\n")
        f.write("    IER |= M_INT1;     // Enable group 1 interrupts\n")
        f.write("    EINT;              // Enable Global interrupt INTM\n")
        f.write("    ERTM;              // Enable Global realtime interrupt DBGM\n\n")
        f.write("    // Initialize results buffer\n")
        f.write("    for(resultsIndex = 0; resultsIndex < RESULTS_BUFFER_SIZE; resultsIndex++)\n")
        f.write("    {\n")
        f.write("        AdcaResults[resultsIndex] = 0;\n")
        f.write("    }\n")
        f.write("    resultsIndex = 0;\n")
        f.write("    bufferFull = 0;\n\n")
        f.write("    // enable PIE interrupt\n")
        f.write("    PieCtrlRegs.PIEIER1.bit.INTx1 = 1;\n\n")
        f.write("    // sync ePWM\n")
        f.write("    EALLOW;\n")
        f.write("    CpuSysRegs.PCLKCR0.bit.TBCLKSYNC = 1;\n")
        f.write("    EDIS;\n\n")
        f.write("    EALLOW;\n")
        f.write("    // Set EPWMCLKDIV to 0 to have the ePWM input clock run at full PLLSYSCLK (100 MHz).\n")
        f.write("    // Without this, the ePWM clock frequency is divided by 2 (resulting in 50 MHz).\n")
        f.write("    ClkCfgRegs.PERCLKDIVSEL.bit.EPWMCLKDIV = 0;\n")
        f.write("    EDIS;\n")
        f.write("}\n\n")
    
        # Loop Function
        f.write("void loop(void)\n")
        f.write("{\n")
        f.write("    //take conversions indefinitely in loop\n")
        f.write("    do\n")
        f.write("    {\n")
        f.write("        //start ePWM\n")
        f.write(f"        {epwmRegs}.ETSEL.bit.SOCAEN = 1;\n")
        f.write(f"        {epwmRegs}.TBCTL.bit.CTRMODE = 0;\n\n")
        f.write("        //wait while ePWM causes ADC conversions, which then cause interrupts,\n")
        f.write("        while(!bufferFull);\n")
        f.write("        bufferFull = 0; //clear the buffer full flag\n\n")
        f.write("        //stop ePWM\n")
        f.write(f"        {epwmRegs}.ETSEL.bit.SOCAEN = 0;  //disable SOCA\n")
        f.write(f"        {epwmRegs}.TBCTL.bit.CTRMODE = 3; //freeze counter\n\n")
        f.write("        //at this point, AdcaResults[] contains a sequence of conversions from the selected channel\n")
        f.write("        //software breakpoint, hit run again to get updated conversions\n")
        f.write("        asm(\"   ESTOP0\");\n")
        f.write("    } while(1);\n")
        f.write("}\n\n")
    
        # ConfigureADC Function
        f.write("// ConfigureADC - Write ADC configurations and power up the ADC for both\n")
        f.write("//                ADC A and ADC B\n")
        f.write("void ConfigureADC(void)\n")
        f.write("{\n")
        f.write("    EALLOW;\n\n")
        f.write("    //write configurations\n")
        f.write("    AdcaRegs.ADCCTL2.bit.PRESCALE = 6; //set ADCCLK divider to /4\n")
        f.write("    AdcSetMode(ADC_ADCA, ADC_RESOLUTION_12BIT, ADC_SIGNALMODE_SINGLE);\n\n")
        f.write("    //Set pulse positions to late\n")
        f.write("    AdcaRegs.ADCCTL1.bit.INTPULSEPOS = 1;\n\n")
        f.write("    //power up the ADC\n")
        f.write("    AdcaRegs.ADCCTL1.bit.ADCPWDNZ = 1;\n\n")
        f.write("    //delay for 1ms to allow ADC time to power up\n")
        f.write("    DELAY_US(1000);\n\n")
        f.write("    EDIS;\n")
        f.write("}\n\n")
        
        # SetupADCEpwm Function
        f.write("// SetupADCEpwm - Setup ADC EPWM acquisition window\n")
        f.write("void SetupADCEpwm(Uint16 channel)\n")
        f.write("{\n")
        f.write("    Uint16 acqps;\n\n")
        f.write("    // Determine minimum acquisition window (in SYSCLKS) based on resolution\n")
        f.write("    if(ADC_RESOLUTION_12BIT == AdcaRegs.ADCCTL2.bit.RESOLUTION)\n")
        f.write("        acqps = 14; //75ns\n")
        f.write("    else //resolution is 16-bit\n")
        f.write("        acqps = 63; //320ns\n\n")
        f.write("    //Select the channels to convert and end of conversion flag\n")
        f.write("    EALLOW;\n")
        f.write("    AdcaRegs.ADCSOC0CTL.bit.CHSEL = channel;  //SOC0 will convert pin A0\n")
        f.write("    AdcaRegs.ADCSOC0CTL.bit.ACQPS = acqps;    //sample window is 100 SYSCLK cycles\n")
        f.write(f"    AdcaRegs.ADCSOC0CTL.bit.TRIGSEL = {triggerOnePWM};      //trigger on ePWM SOCA/C\n")
        f.write("    AdcaRegs.ADCINTSEL1N2.bit.INT1SEL = 0;    //end of SOC0 will set INT1 flag\n")
        f.write("    AdcaRegs.ADCINTSEL1N2.bit.INT1E = 1;      //enable INT1 flag\n")
        f.write("    AdcaRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;    //make sure INT1 flag is cleared\n")
        f.write("    EDIS;\n")
        f.write("}\n\n")
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")
    

def check_epwm_block(functions_present_schema):

    """
    Validates the presence of the 'epwmblk' function in the provided schema.

    This function checks the number of occurrences of the 'epwmblk' function in 
    the input list. It identifies errors if the function is missing or appears 
    multiple times, returning appropriate error codes or success status.

    Example Call:
    -------------
    result = check_epwm_block(functions_present_schema=["epwmblk", "adcblk"])

    Parameters:
    -----------
    functions_present_schema : A list of function names representing the current schema.

    Returns:
    --------
    int : Status code indicating the validation result:
        - 1 : Error, 'epwmblk' is missing.
        - 2 : Error, 'epwmblk' is present more than once.
        - 3 : Success, 'epwmblk' is present exactly once.
    """

    epwm_count = functions_present_schema.count("epwmblk")

    if epwm_count == 0:
        return 1  # Error: 'epwmblk' is missing
    elif epwm_count > 1:
        return 2  # Error: 'epwmblk' occurs more than once
    else:
        return 3  # Success: 'epwmblk' occurs exactly once


def extract_pwm_parameters(blocks, target_function):

    """
    Extracts PWM parameters from a block matching the target function.

    This function iterates through a list of blocks and extracts specific parameters 
    if a block with the target function name is found. It retrieves the first integer 
    parameter (`pwm_period`) and the string parameter (`pwm_output`).

    Example Call:
    -------------
    pwm_period, pwm_output = extract_pwm_parameters(blocks, "target_function_name")

    Parameters:
    -----------
    blocks          : A list of blocks, each containing attributes such as `fcn`, `intPar`, and `str`.
    target_function : The function name to match within the blocks.

    Returns:
    --------
    tuple
        A tuple containing:
        - pwm_period : int or None
            The first integer parameter of the block if available.
        - pwm_output : str or None
            The string parameter of the block if available.
        Returns (None, None) if no matching block is found.
    """

    for block in blocks:
        if block.fcn == target_function:
            pwm_period = block.intPar[0] if len(block.intPar) > 0 else None
            pwm_output = block.str
            return pwm_period, pwm_output
    return None, None


def extract_adc_parameters(blocks, target_function):

    """
    Extracts ADC parameters from blocks matching the target function.

    This function scans a list of blocks to identify those with a specific target function 
    and extracts their ADC module and channel parameters. If an ADC module 'A'/'a' with 
    channel 0 is found, the function immediately returns `None`. Otherwise, it returns 
    a list of dictionaries containing the extracted parameters.

    Example Call:
    -------------
    adc_parameters = extract_adc_parameters(blocks, "target_function_name")

    Parameters:
    -----------
    blocks          : A list of blocks, each containing attributes such as `fcn`, `intPar`, and `str`.
    target_function : The function name to match within the blocks.

    Returns:
    --------
    list or None
        - A list of dictionaries containing:
            - "module" : str or None
                The ADC module identifier (e.g., 'A', 'B', etc.), or None if unavailable.
            - "channel" : int or None
                The ADC channel number, or None if unavailable.
        - Returns `None` immediately if the module is 'A'/'a' with channel 0.
    """

    extracted_blocks = []

    for block in blocks:
        if block.fcn == target_function:
            adc_module = block.str if len(block.str) > 0 else None
            adc_channel = block.intPar[0] if len(block.intPar) > 0 else None
            
            # Check if the ADC combination 'A'/'a' and channel 0 is present
            if adc_module and adc_channel is not None:
                if adc_module.lower() == 'a' and adc_channel == 0:
                    return None
            
            # Adds the dictionary with parameters
            extracted_blocks.append({
                "module": adc_module,
                "channel": adc_channel
            })

    return extracted_blocks


def create_project_structure(model, blocks):
    
    """
    Creates a project structure based on the specified project name.

    This function initializes the directory structure, configuration files, and main source file
    required for a project. It validates the configuration, processes necessary files, and ensures
    compatibility with Code Composer Studio (CCS) workflows. Additionally, it verifies environment 
    specifics like WSL paths and handles potential schema or configuration errors.

    Example Call:
    -------------
    create_project_structure("my_model", blocks)

    Parameters:
    -----------
    model  : The name of the project to be created.
    blocks : A list of blocks defining the project structure, containing attributes like 'fcn', 'intPar', and 'str'.

    Returns:
    --------
    -
    """

    functions_name = check_blocks_set(blocks)
    functions_present_schema = check_blocks_list(blocks)

    app = QApplication.instance() or QApplication([])
    check_wsl_environment()

    # Define paths for config.json in the directory where {model}_gen will be created and inside {model}_gen
    parent_dir = os.path.dirname(os.path.abspath('.'))
    config_path_outside_gen = os.path.join(parent_dir, general_config.path)

    # Check if config.json exists in the parent directory and copy it to {model}_gen, overwriting if needed
    if not os.path.isfile(config_path_outside_gen):
        QMessageBox.information(None, "File Status", f"{general_config.get_name()} not found in {parent_dir} .\nYou can set the paths under the menu settings -> settings -> configure")
        return 
    
    # Load the configuration from the parent directory
    general_config.path = config_path_outside_gen
    config = general_config.load()
    ti_path = config.get('ti_path', '')
    c2000Ware_path = config.get('c2000Ware_path', '')

    if isInWSL:

        # wsl path
        if ti_path.startswith("/mnt/c/"):

            # Convert in a windows path
            ti_path = convert_path_for_windows(ti_path)
        else: 
            ti_path = ti_path.replace('\\', '/')
        if c2000Ware_path.startswith("/mnt/c/"):
            c2000Ware_path = convert_path_for_windows(c2000Ware_path)
        else:
            c2000Ware_path = c2000Ware_path.replace('\\', '/')

    pysimCoder_path = os.environ.get('PYSUPSICTRL')
    CodeGen_path = pysimCoder_path + '/CodeGen'
    include_path = pysimCoder_path + '/CodeGen/Delfino/include'
    src_path = pysimCoder_path + '/CodeGen/Delfino/src'
    pyblock_path = pysimCoder_path + '/CodeGen/Common/include'
    devices_path = pysimCoder_path + '/CodeGen/Delfino/devices'
    targetConfigs_path = pysimCoder_path + '/CodeGen/Delfino/targetConfigs'

    project_dir = f"./{model}_project"
    src_dir = os.path.join(project_dir, "src")
    include_dir = os.path.join(project_dir, "include")
    targetConfigs_dir = os.path.join(project_dir, "targetConfigs")

    # Create the directories
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(include_dir, exist_ok=True)
    os.makedirs(targetConfigs_dir, exist_ok=True)

    # Name of the file that will be moved (eg example.c)
    source_file = f'{model}.c'
    destination_file = os.path.join(src_dir, f'{model}.c')

    # Check if {model}.c exists in the current directoy
    if os.path.exists(source_file):
        if os.path.exists(destination_file):
            os.remove(destination_file)

        # Move {model}.c file in the src directory
        shutil.move(source_file, src_dir)

    config_data = open_project_config_window(model)
    if not config_data:
        QMessageBox.warning(None, "Project Cancelled", f"Project {model} has been cancelled.")
        return False

    save_project_config_file(model, config_data)
    config_window = ProjectConfigWindow(model)
    state = config_window.get_current_state()
    main_file = os.path.join(src_dir, "main.c")

    # Check if there is only one epwm block'
    if state == 2 or state ==4:
        check_result = check_epwm_block(functions_present_schema)

        if check_result == 1:
            QMessageBox.warning(None, "Error", f"ePWM block is missing from the schema. At least one ePWM block is required. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return

        elif check_result == 2:
            print("Error: 'epwmblk' is present more than once in the schema. Only one ePWM block is allowed.")
            QMessageBox.warning(None, "Error", f"ePWM block is present more than once in the schema. Only one ePWM block is allowed. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return
        
        if state == 4:
            adc_blocks = extract_adc_parameters(blocks, 'adcblk')
            if (adc_blocks == None):
                QMessageBox.warning(None, "Error", f"Module A, channel 0 is already busy managing synchronization. Project {model} has been cancelled.")
                project_dir = f"./{model}_project"
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
                return    
                
        tbprd, pwm_output = extract_pwm_parameters(blocks, 'epwmblk')
        dispatch_main_generation(state, main_file, model, None, tbprd, pwm_output)
        
    if state == 3:
        adc_blocks = extract_adc_parameters(blocks, 'adcblk')
        if (adc_blocks == None):
            QMessageBox.warning(None, "Error", f"Module A, channel 0 is already busy managing synchronization. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return  

    if state == 1 or state == 3:
        timer_period = config_data.get("timer_period")
        dispatch_main_generation(state, main_file, model, timer_period, None, None)

    find_and_copy_files(functions_name,  CodeGen_path, src_dir, include_dir)

    # Copy the pyblock.h file
    pyblock_file = os.path.join(pyblock_path, 'pyblock.h')
    if os.path.exists(pyblock_file):
        shutil.copy(pyblock_file, include_dir)

    # Copy contents of targetConfigs directory
    if os.path.exists(targetConfigs_path):
        for file_name in os.listdir(targetConfigs_path):
            full_file_name = os.path.join(targetConfigs_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, targetConfigs_dir)

    # Absolute path include directory
    include_dir_absolute_path = os.path.abspath(include_dir)

    if isInWSL:
        include_dir_absolute_path = convert_path_for_windows(include_dir_absolute_path)

    # create the .project, .cproject, .ccsproject files
    create_ccsproject_file(model)
    create_project_file(model, c2000Ware_path)
    create_cproject_file(model, ti_path, c2000Ware_path, include_dir_absolute_path)

    # Displays a message indicating that the project was created successfully
    QMessageBox.information(None, "Project Status", "Project successfully created")

