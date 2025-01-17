﻿
import os
import sys
import shutil
from numpy import nonzero, ones, asmatrix, size, array, zeros
import json
from supsisim.qtvers import *


r""" The following functionalities are implemented in this script:
    - Create a valid project structure for Code Composer Studio (CCS).
        - This script supports both Linux environments and WSL (Windows Subsystem for Linux).
        - Paths to essential folders (TI, C2000Ware) can be configured via the PySimCoder GUI 
          under Settings -> Settings -> Configure. This action generates a `config.json` file.
            - Without this configuration file, the script cannot generate the CCS project structure.
            - If required paths are missing, the project creation process will stop, and temporary files will be cleaned up.
            - If source files are missing, the user will be prompted to either keep or delete the `config.json` file.
            - Paths can be entered for both Windows and WSL, e.g.:
                - C:\ti\c2000\C2000Ware_4_01_00_00
                - /mnt/c/ti/c2000/C2000Ware_4_01_00_00
        - Save configured paths into a `config.json` file for reuse in future runs.
        - Automatically organize all files into a project hierarchy and generate the following CCS files:
            - `.project`
            - `.cproject`
            - `.ccsproject`
        - Generate a `main.c` file tailored to the selected operation mode. This file:
            - Calls functions created by PySimCoder and adjusts function names dynamically.
            - Includes only relevant files based on the blocks present in the project, e.g.:
                - If `{model}.c` contains the word `inputGPIOblk`, it includes `inputGPIOblk.c`, `button.c`, and `button.h`.
    - Handle project-specific configurations:
        - Each project generates its own configuration file: `{model}_configuration.json`, 
          which contains all the necessary settings for that specific project, including:
            - Timer period, if applicable.
            - ePWM output settings, if applicable.
            - ADC synchronization details, if applicable.
        - These configurations ensure that the generated CCS files and `main.c` are tailored to the project's requirements.

"""

 
# Global variables

# Saved if it is a linux environment or wsl
isInWSL = False

#################################################################################################################################################
# Classes and functions to manage global and project configurations.
#################################################################################################################################################

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
        Sets the initial interface values based on the loaded configuration.
        """

        mode = self.config_data.get("mode")
        self.mode_combo.setCurrentText(mode if mode else "-")

        if mode == "1":
            peripheral = self.config_data.get("peripheral", "-")
            self.peripheral_combo.setCurrentText(peripheral)
            self.peripheral_label.show()
            self.peripheral_combo.show()

            if peripheral == "Timer":
                timer_period = self.config_data.get("timer_period", "")
                self.timer_period_input.setText(timer_period)
                self.timer_period_label.show()
                self.timer_period_input.show()
            elif peripheral == "ePWM":
                epwm_output = self.config_data.get("epwm_output_mode1", "-")
                self.epwm_output_combo_mode1.setCurrentText(epwm_output)
                self.epwm_output_label_mode1.setText("ePWM that generates the interrupt:")
                self.epwm_output_label_mode1.show()
                self.epwm_output_combo_mode1.show()

        elif mode == "2":
            trigger_adc = self.config_data.get("trigger_adc", "-")
            self.trigger_adc_combo.setCurrentText(trigger_adc)
            self.trigger_adc_label.show()
            self.trigger_adc_combo.show()

            if trigger_adc == "Timer":
                timer_period = self.config_data.get("timer_period", "")
                self.timer_period_input.setText(timer_period)
                self.timer_period_label.show()
                self.timer_period_input.show()
            elif trigger_adc == "ePWM":
                epwm_output = self.config_data.get("epwm_output_mode2", "-")
                self.epwm_output_combo_mode2.setCurrentText(epwm_output)
                self.epwm_output_label_mode2.setText("ePWM that triggers ADC:")
                self.epwm_output_label_mode2.show()
                self.epwm_output_combo_mode2.show()


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

        # Drop-down menu for ePWM Output selection (Mode 1)
        self.epwm_output_layout_mode1 = QHBoxLayout()
        self.epwm_output_label_mode1 = QLabel("ePWM Output (Mode 1):")
        self.epwm_output_combo_mode1 = QComboBox()
        self.epwm_output_combo_mode1.addItems(["-"] + [f"out{i}{j}" for i in range(1, 13) for j in ['a', 'b']])
        self.epwm_output_combo_mode1.currentTextChanged.connect(self.update_save_button_state)
        self.epwm_output_combo_mode1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        view1 = QListView()
        self.epwm_output_combo_mode1.setView(view1)

        self.epwm_output_layout_mode1.addWidget(self.epwm_output_label_mode1)
        self.epwm_output_layout_mode1.addWidget(self.epwm_output_combo_mode1)

        self.epwm_output_label_mode1.hide()
        self.epwm_output_combo_mode1.hide()
        layout.addLayout(self.epwm_output_layout_mode1)

        # Drop-down menu for ePWM Output selection (Mode 2)
        self.epwm_output_layout_mode2 = QHBoxLayout()
        self.epwm_output_label_mode2 = QLabel("ePWM Output (Mode 2):")
        self.epwm_output_combo_mode2 = QComboBox()
        self.epwm_output_combo_mode2.addItems(["-"] + [f"out{i}{j}" for i in range(1, 13) for j in ['a', 'b']])
        self.epwm_output_combo_mode2.currentTextChanged.connect(self.update_save_button_state)
        self.epwm_output_combo_mode2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        view2 = QListView()
        self.epwm_output_combo_mode2.setView(view2)

        self.epwm_output_layout_mode2.addWidget(self.epwm_output_label_mode2)
        self.epwm_output_layout_mode2.addWidget(self.epwm_output_combo_mode2)

        self.epwm_output_label_mode2.hide()
        self.epwm_output_combo_mode2.hide()
        layout.addLayout(self.epwm_output_layout_mode2)

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
            self.epwm_output_label_mode1.hide()
            self.epwm_output_combo_mode1.hide()
            self.epwm_output_label_mode2.hide()
            self.epwm_output_combo_mode2.hide()
            return

        if "-" in self.mode_combo.itemText(0):
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
            self.epwm_output_label_mode2.hide()
            self.epwm_output_combo_mode2.hide()

        elif mode == "2":
            self.trigger_adc_combo.clear()
            self.trigger_adc_combo.addItems(["-", "ePWM", "Timer"])
            self.trigger_adc_label.show()
            self.trigger_adc_combo.show()

            self.peripheral_label.hide()
            self.peripheral_combo.hide()
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            self.epwm_output_label_mode1.hide()
            self.epwm_output_combo_mode1.hide()

        self.update_save_button_state()


    def on_peripheral_changed(self, peripheral):

        """
        Show or hide the timer period field and ePWM output field for Mode 1.
        """

        if peripheral == "-":
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            self.epwm_output_label_mode1.hide()
            self.epwm_output_combo_mode1.hide()
            return

        # Removes "-" after first selection
        if "-" in self.peripheral_combo.itemText(0):
            self.peripheral_combo.removeItem(0)

        if peripheral == "Timer":
            self.timer_period_label.show()
            self.timer_period_input.show()
            self.epwm_output_label_mode1.hide()
            self.epwm_output_combo_mode1.hide()
        elif peripheral == "ePWM":
            self.timer_period_label.hide()
            self.timer_period_input.hide()

            # Adds "-" only if it is not already present
            if "-" not in [self.epwm_output_combo_mode1.itemText(i) for i in range(self.epwm_output_combo_mode1.count())]:
                self.epwm_output_combo_mode1.insertItem(0, "-")

            # Show combo box and label
            self.epwm_output_label_mode1.setText("ePWM that generates interrupt:")
            self.epwm_output_label_mode1.show()
            self.epwm_output_combo_mode1.show()

            # Removes "-" immediately when the user selects a different option
            self.epwm_output_combo_mode1.currentTextChanged.connect(self.handle_epwm_selection_mode1)

        self.update_save_button_state()


    def on_trigger_adc_changed(self, trigger):

        """
        Show or hide the timer period field and ePWM output field for Mode 2.
        """

        if trigger == "-":
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            self.epwm_output_label_mode2.hide()
            self.epwm_output_combo_mode2.hide()
            return

        # Removes "-" after first selection
        if "-" in self.trigger_adc_combo.itemText(0):
            self.trigger_adc_combo.removeItem(0)

        if trigger == "Timer":
            self.timer_period_label.show()
            self.timer_period_input.show()
            self.epwm_output_label_mode2.hide()
            self.epwm_output_combo_mode2.hide()
        elif trigger == "ePWM":
            self.timer_period_label.hide()
            self.timer_period_input.hide()

            # Adds "-" only if it is not already present
            if "-" not in [self.epwm_output_combo_mode2.itemText(i) for i in range(self.epwm_output_combo_mode2.count())]:
                self.epwm_output_combo_mode2.insertItem(0, "-")

            # Show combo box and label
            self.epwm_output_label_mode2.setText("ePWM trigger ADC:")
            self.epwm_output_label_mode2.show()
            self.epwm_output_combo_mode2.show()

            # Removes "-" immediately when the user selects a different option
            self.epwm_output_combo_mode2.currentTextChanged.connect(self.handle_epwm_selection_mode2)

        self.update_save_button_state()


    def handle_epwm_selection_mode1(self, value):

        """
        Handles the selection of an ePWM option in Mode 1 and removes the '-' option.
        """

        if value != "-" and "-" in [self.epwm_output_combo_mode1.itemText(i) for i in range(self.epwm_output_combo_mode1.count())]:
            self.epwm_output_combo_mode1.removeItem(0)

    def handle_epwm_selection_mode2(self, value):

        """
        Handles the selection of an ePWM option in Mode 2 and removes the '-' option.
        """

        if value != "-" and "-" in [self.epwm_output_combo_mode2.itemText(i) for i in range(self.epwm_output_combo_mode2.count())]:
            self.epwm_output_combo_mode2.removeItem(0)


    def update_save_button_state(self):

        """
        Enable or disable the Save button based on the current state of the fields.
        Conditions to enable:
        - Mode 1 + Timer + valid period
        - Mode 1 + ePWM + ePWM output
        - Mode 2 + Timer + valid period
        - Mode 2 + ePWM + ePWM output
        """

        mode = self.mode_combo.currentText()
        peripheral = self.peripheral_combo.currentText()
        trigger_adc = self.trigger_adc_combo.currentText()
        timer_period = self.timer_period_input.text()

        if mode == "1":
            if peripheral == "ePWM" and self.epwm_output_combo_mode1.currentText() != "-":
                self.save_button.setEnabled(True)
                return
            elif peripheral == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                self.save_button.setEnabled(True)
                return

        elif mode == "2":
            if trigger_adc == "ePWM" and self.epwm_output_combo_mode2.currentText() != "-":
                self.save_button.setEnabled(True)
                return
            elif trigger_adc == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                self.save_button.setEnabled(True)
                return

        self.save_button.setEnabled(False)


    def get_current_state(self):
    
        """
        Returns the current state based on the selected fields.
        Possible states:
        - 1: Mode 1 + Timer + valid period
        - 2: Mode 1 + ePWM + ePWM output
        - 3: Mode 2 + Timer + valid period
        - 4: Mode 2 + ePWM + ePWM output
        """
    
        mode = self.mode_combo.currentText()
        peripheral = self.peripheral_combo.currentText()
        trigger_adc = self.trigger_adc_combo.currentText()
        timer_period = self.timer_period_input.text()

        if mode == "1":
            if peripheral == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                return 1
            elif peripheral == "ePWM" and self.epwm_output_combo_mode1.currentText() != "-":
                return 2

        elif mode == "2":
            if trigger_adc == "Timer" and timer_period.isdigit() and int(timer_period) > 0:
                return 3
            elif trigger_adc == "ePWM" and self.epwm_output_combo_mode2.currentText() != "-":
                return 4

        # No valid state
        return None


    def cancel_and_close(self):

        """
        Delete the project. 
        The {model}_project folder.
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

        # Close the window
        event.accept()


    def save_and_close(self):

        """
        Save the selected configuration to a JSON file.
        """

        selected_mode = self.mode_combo.currentText()
        selected_peripheral = None
        selected_trigger_adc = None
        timer_period = None
        selected_epwm_output_mode1 = None
        selected_epwm_output_mode2 = None

        # Check the mode and assign the relevant values
        if selected_mode == "1":
            selected_peripheral = self.peripheral_combo.currentText()
            if selected_peripheral == "Timer":
                timer_period = self.timer_period_input.text()
            elif selected_peripheral == "ePWM":
                selected_epwm_output_mode1 = self.epwm_output_combo_mode1.currentText()
                if selected_epwm_output_mode1 == "-":

                    # Set to None if "-" is still selected
                    selected_epwm_output_mode1 = None
    
        elif selected_mode == "2":
            selected_trigger_adc = self.trigger_adc_combo.currentText()
            if selected_trigger_adc == "Timer":
                timer_period = self.timer_period_input.text()
            elif selected_trigger_adc == "ePWM":
                selected_epwm_output_mode2 = self.epwm_output_combo_mode2.currentText()
                if selected_epwm_output_mode2 == "-":

                    # Set to None if "-" is still selected
                    selected_epwm_output_mode2 = None

        config_data = {
            "mode": selected_mode,
            "peripheral": selected_peripheral if selected_peripheral != "-" else None,
            "trigger_adc": selected_trigger_adc if selected_trigger_adc != "-" else None,
            "timer_period": timer_period if timer_period else None,
            "epwm_output_mode1": selected_epwm_output_mode1,
            "epwm_output_mode2": selected_epwm_output_mode2,
        }

        # Save data
        save_project_config_file(self.model, config_data)

        # Closes the window with Accepted status
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
        self.resize(800, 250)

        # Load existing configuration
        config = general_config.load()
        self.ti_path = config.get('ti_path', '')
        self.c2000Ware_path = config.get('c2000Ware_path', '')
        self.compiler_version = config.get('compiler_version', 'ti-cgt-c2000_22.6.1.LTS')

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

        # Dropdown for selecting the compiler
        compiler_layout = QHBoxLayout()
        compiler_label = QLabel("Select Compiler Version:")
        self.compiler_dropdown = QComboBox()
        self.compiler_dropdown.addItems([
            "ti-cgt-c2000_22.6.1.LTS",
            "ti-cgt-c2000_21.6.0.LTS"
        ])
        self.compiler_dropdown.setCurrentText(self.compiler_version)
        self.compiler_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        compiler_layout.addWidget(compiler_label)
        compiler_layout.addWidget(self.compiler_dropdown)

        # Save and Cancel buttons
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
        layout.addLayout(compiler_layout)
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

        # Gather data from the form
        config_data = {
            "ti_path": self.ti_input.text(),
            "c2000Ware_path": self.c2000_input.text(),
            "compiler_version": self.compiler_dropdown.currentText(),
        }

        # Save using the new function
        save_general_config_file(config_data)
        self.accept()


    def closeEvent(self, event):

        """
        Ensures that the "Rejected" state is set if closed with the 'x'
        """

        self.reject()


# File name where to save the paths.
# It cannot be at the top of the code, it must be declared after the class declaration.
general_config = ConfigFile("general_config")


def save_general_config_file(config_data):

    """
    Saves the general configuration file with specified paths.

    This function creates or updates the configuration file with the provided data,
    and displays a confirmation message upon successful save.

    Example Call:
    -------------
    save_general_config_file({
        "ti_path": "path/to/TI",
        "c2000Ware_path": "path/to/C2000Ware",
        "compiler_version": "21.6.0.LTS"
    })

    Parameters:
    -----------
    config_data : dict -> Dictionary containing the configuration data to save.

    Returns:
    --------
    -

    """

    config_file = ConfigFile(name="general_config", extension="json")
    config_file.save(config_data)

    QMessageBox.information(None, "General Configs Saved", "Paths and compiler saved successfully!")


def save_project_config_file(model, config_data):

    """
    Saves the project configuration file for a specific project.

    This function creates or updates the configuration file for a project 
    based on the given model name and configuration data.
    
    Example Call:
    -------------
    save_project_config_file(
        "example_project",
        {
            "mode": "1",
            "peripheral": "Timer",
            "trigger_adc": None,
            "timer_period": 5000,
            "epwm_output_mode1": None,
            "epwm_output_mode2": None
        }
    )

    Parameters:
    -----------
    model       : str -> The name of the project.
    config_data : dict -> Dictionary containing the configuration data to save.

    Returns:
    --------
    -

    """

    # Project Directory
    project_dir = f"./{model}_project"
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    config_file = ConfigFile(name=os.path.join(project_dir, f"{model}_configuration"), extension="json")
    config_file.save(config_data)


def open_config_window():

    """
    Opens the configuration window for user input.

    Example Call:
    -------------
    open_config_window()

    Parameters:
    -----------
    -

    Returns:
    --------
    bool    : True if the configuration was saved (Accepted), False otherwise (Rejected).

    """

    app = QApplication.instance() or QApplication([])
    config_window = ConfigWindow()

    # Return QDialog.Accepted or QDialog.Rejected
    result = config_window.exec()
    return result == QDialog.Accepted


def open_project_config_window(model):

    """
    Opens the project configuration window for a specific project.
    It collects and returns the configuration data if the user saves their changes.

    Example Call:
    -------------
    open_project_config_window("example_model")

    Parameters:
    -----------
    model : str -> The name of the project to configure.

    Returns:
    --------
    dict or None    : A dictionary containing the configuration data if saved, or `None` if the operation was canceled.

    """

    app = QApplication.instance() or QApplication([])
    project_config_window = ProjectConfigWindow(model)

    # Returns QDialog.Accepted or QDialog.Rejected
    result = project_config_window.exec()

    if result == QDialog.Accepted:

        # Build the configuration data
        mode = project_config_window.mode_combo.currentText()
        peripheral = project_config_window.peripheral_combo.currentText() if mode == "1" else None
        trigger_adc = project_config_window.trigger_adc_combo.currentText() if mode == "2" else None
        timer_period = project_config_window.timer_period_input.text() or None
        epwm_output_mode1 = (
            project_config_window.epwm_output_combo_mode1.currentText()
            if mode == "1" and peripheral == "ePWM"
            else None
        )
        epwm_output_mode2 = (
            project_config_window.epwm_output_combo_mode2.currentText()
            if mode == "2" and trigger_adc == "ePWM"
            else None
        )

        # Return the complete configuration
        config_data = {
            "mode": mode,
            "peripheral": peripheral,
            "trigger_adc": trigger_adc,
            "timer_period": timer_period,
            "epwm_output_mode1": epwm_output_mode1,
            "epwm_output_mode2": epwm_output_mode2,
        }
        return config_data

    return None

#################################################################################################################################################
# Functions that check the paths entered in the global configuration and, in case of problems, indicate exactly what is wrong.
#################################################################################################################################################

def advise(title, message):

    """
    Displays a customizable confirmation dialog with a scrollable message and "Yes"/"No" buttons.

    This function creates a modal dialog using PyQt, allowing users to read a detailed message
    and make a choice between "Yes" and "No." The dialog includes a scrollable text area for long messages
    and a title to provide context.

    Example Call:
    -------------
    user_response = advise(
        "Exit Confirmation",
        "Are you sure you want to exit the application?\nAll unsaved changes will be lost."
    )

    Parameters:
    -----------
    title   : str -> The title of the dialog window.
    message : str -> The message to display inside the scrollable text area.

    Returns:
    --------
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


def update_paths(ti_path, c2000_path, compiler):

    """
    Updates paths based on the provided `ti_path`, `c2000_path`, and `compiler`.

    This function generates a dictionary with paths required for project configuration.
    The paths include linker files, header files, and source files, which are determined
    based on the specified TI path, C2000Ware path, and compiler version.

    Example Call:
    -------------
    paths = update_paths(
        "C:/ti",
        "C:/ti/c2000/C2000Ware_4_01_00_00",
        "ti-cgt-c2000_22.6.1.LTS"
    )

    Parameters:
    -----------
    ti_path    : str -> The path where the TI folder is located.
    c2000_path : str -> The path where the C2000Ware_4_01_00_00 folder is located.
    compiler   : str -> The version of the compiler to be used (e.g., "ti-cgt-c2000_22.6.1.LTS").

    Returns:
    --------
    dict       : A dictionary containing updated paths.

    Example Output:
    ---------------
    {
        "linker_path1": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd",
        "linker_path2": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd",
        "first_headers_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/include",
        "second_headers_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/include",
        "third_headers_path": "C:/ti/ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include",
        "first_source_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/source",
        "second_source_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source"
    }
    """
    
    # Determine third_headers_path based on the selected compiler
    if compiler == "ti-cgt-c2000_22.6.1.LTS":
        third_headers_path = os.path.join(ti_path, 'ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include')
    elif compiler == "ti-cgt-c2000_21.6.0.LTS":
        third_headers_path = os.path.join(ti_path, 'ccs1110/ccs/tools/compiler/ti-cgt-c2000_21.6.0.LTS/include')

    # Build the dictionary of paths
    paths_to_check = {
        "linker_path1": os.path.join(c2000_path, 'device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd'),
        "linker_path2": os.path.join(c2000_path, 'device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd'),
        "first_headers_path": os.path.join(c2000_path, 'device_support/f2837xd/headers/include'),
        "second_headers_path": os.path.join(c2000_path, 'device_support/f2837xd/common/include'),
        "third_headers_path": third_headers_path,
        "first_source_path": os.path.join(c2000_path, 'device_support/f2837xd/headers/source'),
        "second_source_path": os.path.join(c2000_path, 'device_support/f2837xd/common/source'),
    }

    return paths_to_check


def check_paths(ti_path, c2000_path, compiler):
    
    """
    Verifies and updates required paths and files for the project configuration.

    This function checks if essential paths and files, based on `ti_path`, `c2000_path`,
    and `compiler`, are accessible. If the environment is WSL, paths are converted 
    accordingly. Missing paths or files trigger user prompts to either update paths 
    or delete the configuration file. The function loops until all paths and files 
    are verified.

    Required Files:
    ---------------
    - F2837xD_GlobalVariableDefs.c
    - F2837xD_CpuTimers.c
    - F2837xD_CodeStartBranch.asm
    - F2837xD_DefaultISR.c
    - F2837xD_Gpio.c
    - F2837xD_Ipc.c
    - F2837xD_PieCtrl.c
    - F2837xD_PieVect.c
    - F2837xD_SysCtrl.c
    - F2837xD_usDelay.asm

    Example Call:
    -------------
    check_paths(
        "C:/ti",
        "C:/ti/c2000/C2000Ware_4_01_00_00",
        "ti-cgt-c2000_22.6.1.LTS"
    )

    Parameters:
    -----------
    ti_path    : str -> The path where the TI folder is located.
    c2000_path : str -> The path where the C2000Ware_4_01_00_00 folder is located.
    compiler   : str -> The version of the compiler to be used (e.g., "ti-cgt-c2000_22.6.1.LTS").

    Returns:
    --------
    -

    """

    if isInWSL:
        ti_path = convert_path_for_wsl(ti_path)
        c2000_path = convert_path_for_wsl(c2000_path)

    paths_to_check = update_paths(ti_path, c2000_path, compiler)

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
                paths_to_check = update_paths(ti_path_update, c2000_path_update, compiler)
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
                    general_config.delete()
                    return 
                else:
                    return
            else:
                QMessageBox.information(None, "Paths and Files Check", "All required paths and files are present.")
                break

#################################################################################################################################################
# Functions to run the project on wsl, windows and linux.
#################################################################################################################################################

def check_wsl_environment():

    """ Detects if the environment is running within Windows Subsystem for Linux (WSL).

    This function determines whether the current environment is WSL or a native Linux
    installation by inspecting the system's release name. It sets the global variable 
    `isInWSL` to `True` if WSL is detected, otherwise `False`.

    Example Call:
    -------------
    check_wsl_environment()

    Parameters:
    -----------
    -

    Returns:
    --------
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
    wsl_path = convert_path_for_wsl("C:\\Users\\user\\path\\to\\file.c")

    Parameters:
    -----------
    path       : str -> The file path in Windows format (e.g., "C:\\Users\\user\\path\\to\\file.c").

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
    windows_path = convert_path_for_windows("/mnt/c/Users/user/path/to/file.c")

    Parameters:
    -----------
    path       : str -> The file path in WSL format (e.g., "/mnt/c/Users/user/path").

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

#################################################################################################################################################
# Functions to create the files needed to create a project for CCS (.project, .cproject, .ccsproject).
#################################################################################################################################################

def create_ccsproject_file(model, compiler):

    """
    Creates a .ccsproject file in XML format for a given project.

    This function generates a `.ccsproject` file within a project-specific directory.
    The file is created in XML format and includes basic project options. The function ensures that the 
    directory exists before writing the file.

    Example Call:
    -------------
    create_ccsproject_file("exampleModel", "ti-cgt-c2000_22.6.1.LTS")

    Parameters:
    -----------
    model      : str -> The name of the project for which the `.ccsproject` file is being created.
    compiler   : str -> The version of the compiler to be used (e.g., "ti-cgt-c2000_22.6.1.LTS").

    Returns:
    --------
    -

    Example:
    --------
    Input:
        model = "exampleModel"
        compiler = "ti-cgt-c2000_22.6.1.LTS"

    Output:
        Creates a file `./exampleModel_project/.ccsproject` with the specified XML content.
    """
    
    project_dir = f"./{model}_project"
    ccsproject_file = os.path.join(project_dir, ".ccsproject")

    if (compiler == "ti-cgt-c2000_22.6.1.LTS"):
        codegenToolVersion = "22.6.1.LTS"
    if (compiler == "ti-cgt-c2000_21.6.0.LTS"):
        codegenToolVersion = "21.6.0.LTS"

    # Content of .ccsproject file
    ccsproject_content = (
        '<?xml version="1.0" encoding="UTF-8" ?>\n'
        '<?ccsproject version="1.0"?>\n'
        '<projectOptions>\n'
        '    <!-- Specifica il tipo di dispositivo che stai usando -->\n'
        '    <deviceVariant value="com.ti.ccstudio.deviceModel.C2000.GenericC28xxDevice"/>\n'
        '    <deviceFamily value="C2000"/>\n'
        f'    <codegenToolVersion value="{codegenToolVersion}"/>\n'
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
    model      : str -> The name of the project for which the `.project` file is being created.
    c2000_path : str -> The path where the C2000Ware_4_01_00_00 folder is located.

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


def create_cproject_file(model, ti_path, c2000_path, include, state, compiler, main4_nr_epwm_trigger_adc):

    """
    Creates a .cproject file in XML format for a given project.

    This function generates a `.cproject` file in a project-specific directory.
    The file is created in XML format and includes detailed configuration settings. 

    Example Call:
    -------------
    create_cproject_file(
        "exampleModel",
        "C:/ti",
        "C:/ti/c2000/C2000Ware_4_01_00_00",
        "C:/Users/name/Desktop/untitled_gen/untitled_project/include",
        1,
        "ti-cgt-c2000_22.6.1.LTS",
        3
    )

    Parameters:
    -----------
    model      : str -> The name of the project for which the `.cproject` file is being created.
    ti_path    : str -> The path where the TI folder is located.
    c2000_path : str -> The path where the C2000Ware_4_01_00_00 folder is located.
    include    : str -> The include directory of the project.
    state      : int -> The current state of the project (If main1 is used the state will be = 1, and so on for mains 2,3 and 4), used in the conditional defines.
    compiler   : str -> The version of the compiler to be used (e.g., "ti-cgt-c2000_22.6.1.LTS").
    main4_nr_epwm_trigger_adc : int or None -> The number of ePWM triggers for ADC, used as a conditional define.

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
        state = 1
        compiler = "ti-cgt-c2000_22.6.1.LTS"
        main4_nr_epwm_trigger_adc = 3

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

    
    if (compiler == "ti-cgt-c2000_22.6.1.LTS"):
        number_version = 22
        codegen_version = "22.6.1.LTS"
        third_headers_path = ti_path + '/ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include'
    if (compiler == "ti-cgt-c2000_21.6.0.LTS"):
        number_version = 21
        codegen_version = "21.6.0.LTS"
        third_headers_path = ti_path + '/ccs1110/ccs/tools/compiler/ti-cgt-c2000_21.6.0.LTS/include'

    conditional_define = ""
    if main4_nr_epwm_trigger_adc is not None:
        conditional_define = f'<listOptionValue builtIn="false" value="NREPWMTRIGGERADC={main4_nr_epwm_trigger_adc}"/>'


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
                            <toolChain id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.DebugToolchain.1936615022" name="TI Build Tools" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.DebugToolchain" targetTool="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.linkerDebug.1604840405">
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
                                <option id="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION.1659874217" superClass="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION" value="{codegen_version}" valueType="string"/>
                                <targetPlatform id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.targetPlatformDebug.872252835" name="Platform" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.targetPlatformDebug"/>
                                <builder buildPath="${{BuildDirectory}}" id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.builderDebug.523509514" name="GNU Make.CPU1_RAM" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.builderDebug"/>
                                <tool id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.compilerDebug.1225049945" name="C2000 Compiler" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.compilerDebug">
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.SILICON_VERSION.76848770" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.SILICON_VERSION" value="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.SILICON_VERSION.28" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.LARGE_MEMORY_MODEL.1426538618" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.LARGE_MEMORY_MODEL" value="true" valueType="boolean"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.UNIFIED_MEMORY.1204196634" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.UNIFIED_MEMORY" value="true" valueType="boolean"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.FLOAT_SUPPORT.912837455" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.FLOAT_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.FLOAT_SUPPORT.fpu32" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.CLA_SUPPORT.467689498" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.CLA_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.CLA_SUPPORT.cla1" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.TMU_SUPPORT.484008760" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.TMU_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.TMU_SUPPORT.tmu0" valueType="enumerated"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.VCU_SUPPORT.1379050903" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.VCU_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.VCU_SUPPORT.vcu2" valueType="enumerated"/>

                                    <!-- Sezione Include Path -->
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.INCLUDE_PATH.1816198112" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.INCLUDE_PATH" valueType="includePath">
                                        <listOptionValue builtIn="false" value="{first_headers_path}"/>
                                        <listOptionValue builtIn="false" value="{second_headers_path}"/>
                                        <listOptionValue builtIn="false" value="{third_headers_path}"/>
                                        <listOptionValue builtIn="false" value="{include_path}"/>
                                    </option>

                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DEBUGGING_MODEL.2023058995" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DEBUGGING_MODEL" value="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DEBUGGING_MODEL.SYMDEBUG__DWARF" valueType="enumerated"/>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DEFINE.928837016" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DEFINE" valueType="definedSymbols">
                                        <listOptionValue builtIn="false" value="CPU1"/>
                                        <listOptionValue builtIn="false" value="_LAUNCHXL_F28379D"/>
                                        <listOptionValue builtIn="false" value="STATE={state}"/>
                                        {conditional_define}
                                    </option>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DISPLAY_ERROR_NUMBER.1888790822" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DISPLAY_ERROR_NUMBER" value="true" valueType="boolean"/>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DIAG_WARNING.1826112291" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.DIAG_WARNING" valueType="stringList">
                                        <listOptionValue builtIn="false" value="225"/>
                                    </option>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.ABI.1734084811" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.ABI" value="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compilerID.ABI.coffabi" valueType="enumerated"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__C_SRCS.935175564" name="C Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__C_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__CPP_SRCS.1754916874" name="C++ Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__CPP_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__ASM_SRCS.966474163" name="Assembly Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__ASM_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__ASM2_SRCS.1331774997" name="Assembly Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.compiler.inputType__ASM2_SRCS"/>
                                </tool>

                                <!-- Sezione Linker Config -->
                                <tool id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.linkerDebug.1604840405" name="C2000 Linker" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exe.linkerDebug">
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.MAP_FILE.150192862" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.MAP_FILE" value="&quot;${{ProjName}}.map&quot;" valueType="string"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.OUTPUT_FILE.508871516" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.OUTPUT_FILE" value="${{ProjName}}.out" valueType="string"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.STACK_SIZE.794155856" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.STACK_SIZE" value="0x100" valueType="string"/>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.LIBRARY.779473277" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.LIBRARY" valueType="libs">
                                        <listOptionValue builtIn="false" value="rts2800_fpu32.lib"/>
                                        <listOptionValue builtIn="false" value="{linker_path1}"/>
                                        <listOptionValue builtIn="false" value="{linker_path2}"/>
                                        <listOptionValue builtIn="false" value="libc.a"/>
                                    </option>
                                    <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.SEARCH_PATH.1443810135" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.SEARCH_PATH" valueType="libPaths">
                                        <listOptionValue builtIn="false" value="${{CG_TOOL_ROOT}}/lib"/>
                                    </option>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.DISPLAY_ERROR_NUMBER.96471687" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.DISPLAY_ERROR_NUMBER" value="true" valueType="boolean"/>
                                    <option id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.XML_LINK_INFO.1957298402" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.linkerID.XML_LINK_INFO" value="&quot;${{ProjName}}_linkInfo.xml&quot;" valueType="string"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exeLinker.inputType__CMD_SRCS.1799253343" name="Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exeLinker.inputType__CMD_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exeLinker.inputType__CMD2_SRCS.478843577" name="Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exeLinker.inputType__CMD2_SRCS"/>
                                    <inputType id="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exeLinker.inputType__GEN_CMDS.1897434562" name="Generated Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_{number_version}.6.exeLinker.inputType__GEN_CMDS"/>
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

#################################################################################################################################################
# Functions that control the blocks inserted in the diagram.
#################################################################################################################################################

def check_blocks_list(blocks):

    """
    Analyzes blocks and returns a list of functions used, including duplicates.

    This function iterates through a list of blocks, extracts their associated 
    functions (if available), and returns them as a list, preserving duplicates.

    Example Call:
    -------------
    result = check_blocks_list(list_blocks)

    Parameters:
    -----------
    blocks     : list -> List of blocks.

    Returns:
    --------
    list       : List of functions associated with the provided blocks, including duplicates.

    """

    block_functions = []

    for block in blocks:
        block_function = getattr(block, 'fcn', 'N/A')

        if block_function != 'N/A':
            block_functions.append(block_function)

    return block_functions


def check_blocks_set(blocks):

    """
    Analyzes blocks and returns a set of functions used.

    This function iterates through a list of blocks, extracts their associated 
    functions (if available), and returns them as a set.

    Example Call:
    -------------
    result = check_blocks_set(list_blocks)

    Parameters:
    -----------
    blocks     : list -> List of blocks.

    Returns:
    --------
    set        : Set of functions associated with the provided blocks.

    """

    block_functions = set()

    for block in blocks:
        block_function = getattr(block, 'fcn', 'N/A')

        if block_function != 'N/A':
            block_functions.add(block_function)

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
    found_files = find_and_copy_files(
        ["adcblk", "step", "outputGPIOblk"],                # List of function names
        "C:/path/to/CodeGen",                               # Path to CodeGen directory
        "C:/path/to/project/source",                        # Destination directory for .c files
        "C:/path/to/project/include"                        # Destination directory for .h files
    )
    
    Parameters:
    -----------
    function_names : set -> Set of function names for which files need to be located and copied.
    CodeGen_path   : str -> Path to the directory where the source and header files are located.
    dest_c_dir     : str -> Destination directory for `.c` files.
    dest_h_dir     : str -> Destination directory for `.h` files.

    Returns:
    --------
    dict           : A dictionary where each function is mapped to its associated `.c` and `.h` file paths. 
                     The dictionary contains two keys for each function:
                     - "c_files": A list of paths to the copied `.c` files.
                     - "h_files": A list of paths to the copied `.h` files.

    """

    found_files = {}
    os.makedirs(dest_c_dir, exist_ok=True)
    os.makedirs(dest_h_dir, exist_ok=True)

    # Special rules for specific functions
    special_cases = {
        "adcblk": ["adcblk.c", "adc.c", "adcDelfino.h"],
        "inputGPIOblk": ["inputGPIOblk.c", "button.c", "button.h"],
        "outputGPIOblk": ["outputGPIOblk.c", "ledDelfino.c", "led.h"],
        "epwmblk": ["epwmblk.c", "epwm.c", "epwm.h"],
        "delfinoPlotblk": ["delfinoPlotblk.c", "sci.c", "sci.h"],
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
        found_files[function] = {"c_files": [], "h_files": []}

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
                    
                    # Append the file to the correct list in found_files
                    if file_name.endswith(".c"):
                        found_files[function]["c_files"].append(dest_path)
                    elif file_name.endswith(".h"):
                        found_files[function]["h_files"].append(dest_path)

    return found_files


def check_epwm_block(functions_present_schema):

    """
    Validates the presence of the 'epwmblk' function in the provided schema.

    This function checks the number of occurrences of the 'epwmblk' function in 
    the input list. It identifies errors if the function is missing.

    Example Call:
    -------------
    result = check_epwm_block(["epwmblk", "adcblk"])

    Parameters:
    -----------
    functions_present_schema : list -> A list of function names representing the current schema.

    Returns:
    --------
    int : Status code indicating the validation result:
        - 1 : Error, 'epwmblk' is missing.
        - 2 : Success, 'epwmblk' is present at least once.
    """

    epwm_count = functions_present_schema.count("epwmblk")

    if epwm_count == 0:
        return 1  # Error: 'epwmblk' is missing
    else:
        return 2  # Success: 'epwmblk' there is at least once


def find_matching_pwm_output(blocks, target_function, epwm_output):

    """
    Searches for a block in the given list that matches the target function 
    and the specified ePWM output.

    This function iterates through the provided list of blocks to find the first block 
    that satisfies the following conditions:
    - The block's function name (`fcn`) matches the specified `target_function`.
    - The block's string parameter (`str`) matches the given `epwm_output`.

    If a match is found, the function returns the block's first integer parameter and 
    string parameter. If no match is found, it returns `(None, None)`.

    Example Call:
    -------------
    result = find_matching_pwm_output(list_blocks, target_function="epwmblk", epwm_output="out1a")

    # Output
    result: (2000, 'out1a')

    Parameters:
    -----------
    blocks : list ->
        A list of block to search through. Each block is expected to have:
        - `fcn` : str -> The function name of the block.
        - `intPar` : list[int] -> A list of integer parameters associated with the block.
        - `str` : str -> A string parameter associated with the block.
    
    target_function : str -> The name of the function to match within the blocks' `fcn` attribute.  
    epwm_output : str -> The PWM output value to match within the blocks' `str` attribute.
    
    Returns:
    --------
    tuple
        A tuple containing:
        - pwm_period : int or None -> The first integer parameter of the matching block, if found.
        - pwm_output : str or None -> The string parameter of the matching block, if found.

        If no block matches the criteria, returns `(None, None)`.

    """

    for block in blocks:
        if block.fcn == target_function:
            pwm_period = block.intPar[0] if len(block.intPar) > 0 else None
            pwm_output = block.str

            if pwm_output == epwm_output:
                return pwm_period, pwm_output  # Match found, return immediately

    return None, None  # No match found


def extract_adc_parameters(blocks, target_function):

    """
    Extracts ADC parameters from the blocks that match the target function.

    This function searches through a list of blocks, identifies those that match the 
    specified `target_function`, and extracts relevant ADC parameters. It filters 
    only those blocks where `generateInterrupt` is set to 1. 

    Example Call:
    -------------

    result = extract_adc_parameters(list_blocks, "adcblk")

    # Example Output:
    # result: {"module": "A", "soc": 0, "channel": 1}

    Parameters:
    -----------
    blocks : list -> 
        A list of blocks to search through. Each block is expected to have:
        - `fcn` : str -> The function name of the block.
        - `str` : str -> A string parameter associated with the block (e.g., ADC module).
        - `intPar` : list[int] -> A list of integer parameters including:
            - [0]: ADC channel (e.g., 1, 2, 3).
            - [1]: SOC (start-of-conversion) index.
            - [2]: Generate interrupt flag (1 for active, 0 otherwise).
    
    target_function : str -> The name of the function to match within the blocks' `fcn` attribute.

    Returns:
    --------
    int or dict:
        - -1 : No matching blocks found.
        - -2 : Multiple matching blocks found.
        - dict : A dictionary containing the extracted ADC parameters if a single match is found.
            - "module" : str -> The ADC module (e.g., "A", "B", "C").
            - "soc" : int -> The SOC index of the block.
            - "channel" : int -> The ADC channel of the block.

    """

    matching_blocks = []

    for block in blocks:

        # Check if the block matches the target function
        if block.fcn == target_function:

            # Extract parameters
            adc_module = block.str if len(block.str) > 0 else None
            adc_channel = block.intPar[0] if len(block.intPar) > 0 else None
            soc = block.intPar[1] if len(block.intPar) > 0 else None
            generate_interrupt = block.intPar[2] if len(block.intPar) > 0 else None

            # Filter for blocks with generateInterrupt == 1
            if generate_interrupt == 1:
                matching_blocks.append({
                    "module": adc_module,
                    "soc": soc,
                    "channel": adc_channel
                })

    # Handle return cases
    if len(matching_blocks) == 0:
        return -1  # No matching blocks
    elif len(matching_blocks) > 1:
        return -2  # Multiple matching blocks
    else:
        return matching_blocks[0]  # Single matching block

#################################################################################################################################################
# Functions that manage and generate the different main.
#################################################################################################################################################

def dispatch_main_generation(state, path_main, model, timer_period, tbprd, pwm_output, adc_block):

    """
    Dispatches the generation of `main.c` based on the provided state.

    This function determines which specific function to call for generating 
    the `main.c` file based on the provided `state`.

    Example Calls:
    --------------
    # State 1: Mode 1 with Timer
    dispatch_main_generation(
        state=1,
        path_main="path/to/main.c",
        model="exampleModel",
        timer_period=1000,
        tbprd=None,
        pwm_output=None,
        adc_block=None
    )

    # State 2: Mode 1 with ePWM
    dispatch_main_generation(
        state=2,
        path_main="path/to/main.c",
        model="exampleModel",
        timer_period=None,
        tbprd=2000,
        pwm_output="out1a",
        adc_block=None
    )

    # State 3: Mode 2 with Timer and ADC
    dispatch_main_generation(
        state=3,
        path_main="path/to/main.c",
        model="exampleModel",
        timer_period=5000,
        tbprd=None,
        pwm_output=None,
        adc_block={"module": "A", "soc": 0, "channel": 3}
    )

    # State 4: Mode 2 with ePWM and ADC
    dispatch_main_generation(
        state=4,
        path_main="path/to/main.c",
        model="exampleModel",
        timer_period=None,
        tbprd=4000,
        pwm_output="out2b",
        adc_block={"module": "B", "soc": 1, "channel": 5}
    )

    Parameters:
    -----------
    state         : int ->
        Defines the mode of operation:
        - 1: Mode 1 with Timer interrupts.
        - 2: Mode 1 with ePWM interrupts.
        - 3: Mode 2 with Timer and ADC triggering.
        - 4: Mode 2 with ePWM and ADC triggering.

    path_main     : str -> Full path to the `main.c` file to be generated.

    model         : str -> Name of the model being used for generation.

    timer_period  : int or None ->
        Timer period in microseconds.
        Set to `None` if not applicable.

    tbprd         : int or None -> 
        Timer Base Period Register value for ePWM (defines the PWM period).
        Set to `None` if not applicable.

    pwm_output    : str or None -> 
        Identifier of the ePWM output channel (e.g., "out1a", "out1b").
        Set to `None` if not applicable.

    adc_block     : dict or None ->
        Configuration dictionary for ADC triggering. It should contain:
        - "module": str -> ADC module (e.g., "A", "B", "C", "D").
        - "soc": int -> ADC SOC (Start of Conversion) index.
        - "channel": int -> ADC channel.
        Set to `None` if not applicable.

    Returns:
    --------
    -

    """

    if state == 1:
        generate_main_mode1_timer(path_main, model, timer_period)
    elif state == 2:
        generate_main_mode1_epwm(path_main, model, tbprd, pwm_output)
    elif state == 3:
        generate_main_mode2_timer(path_main, model, timer_period, adc_block)
    elif state == 4:
        generate_main_mode2_epwm(path_main, model, tbprd, pwm_output, adc_block)
    else:
        raise ValueError(f"Invalid state: {state}. Expected 1, 2, 3, or 4.")


# state 1
def generate_main_mode1_timer(path_main, model, timer_period):
    
    """
    Generates the main.c file for Mode 1 using Timer interrupts.

    Example Call:
    -------------
    generate_main_mode1_timer("path/to/main.c", "model_name", 1000)

    Parameters:
    -----------
    path_main    : str -> Path to the output main.c file.
    model        : str -> Name of the model.
    timer_period : int -> Timer period in microseconds.

    Returns:
    --------
    -

    """

    Tsamp = float(timer_period)/1000000

    with open(path_main, 'w') as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   main.c\n")
        f.write("// AUTHOR: Tatiana Dal Busco\n")
        f.write("// DATE:   December 2024\n")
        f.write("//###########################################################################\n\n")
    
        f.write('#include "F28x_Project.h"\n\n')
    
        # Function prototypes
        f.write("void setup(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n")
        f.write("__interrupt void cpu_timer0_isr(void);\n\n")
    
        # Global variables
        f.write(f"static double Tsamp = {Tsamp};  // Time range\n")
        f.write("static double T = 0.0;         // Current time\n\n")
    
        # Main function
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    while (1) {}\n")
        f.write("}\n\n")
    
        # ISR of Timer0
        f.write("// CPU Timer 0 ISR: Handles periodic timer interrupts\n")
        f.write("__interrupt void cpu_timer0_isr(void)\n")
        f.write("{\n")
        f.write("    CpuTimer0.InterruptCount++;\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")
    
        # Initial setup
        f.write("// Sets up system control, peripherals, interrupts, and Timer 0 for the application\n")
        f.write("void setup(void)\n")
        f.write("{\n\n")
        f.write("    // Initialize the system control: clock, PLL, and peripheral settings\n")
        f.write("    InitSysCtrl();\n\n")
        f.write("    // Initialize General Purpose Input/Output pins\n")
        f.write("    InitGpio();\n\n")
        f.write("    // Disable all CPU interrupts\n")
        f.write("    DINT;\n\n")
        f.write("    // Initialize the Peripheral Interrupt Expansion (PIE) control registers\n")
        f.write("    InitPieCtrl();\n\n")
        f.write("    // Clear all interrupt enable registers\n")
        f.write("    IER = 0x0000;\n\n")
        f.write("    // Clear all interrupt flag registers\n")
        f.write("    IFR = 0x0000;\n\n")
        f.write("    // Initialize the PIE vector table with default interrupt vectors\n")
        f.write("    InitPieVectTable();\n\n")
        f.write(f"    {model}_init();\n\n")
        f.write("    // Map the CPU Timer 0 interrupt to its ISR (Interrupt Service Routine)\n")
        f.write("    EALLOW;\n")
        f.write("    PieVectTable.TIMER0_INT = &cpu_timer0_isr;\n")
        f.write("    EDIS;\n\n")
        f.write("    // Initialize CPU Timers and configure Timer 0\n")
        f.write("    InitCpuTimers();\n")
        f.write(f"    ConfigCpuTimer(&CpuTimer0, 200, {timer_period});\n")
        f.write("    CpuTimer0Regs.TCR.all = 0x4000; // Start Timer 0\n\n")
        f.write("    // Enable CPU interrupt group 1\n")
        f.write("    IER |= M_INT1;\n\n")
        f.write("    // Enable PIE interrupt for Timer 0\n")
        f.write("    PieCtrlRegs.PIEIER1.bit.INTx7 = 1;\n\n")
        f.write("    // Enable global interrupts and real-time interrupts\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n\n")
        f.write("}\n\n")
    
        # get_run_time function
        f.write("// Returns the current runtime\n")
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
    
        # get_Tsamp function
        f.write("// Returns the sampling time interval\n")
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
    path_main   : str -> Path to the output main.c file.
    model       : str -> Name of the model to integrate into the main program.
    tbprd       : int -> Timer base period register value for ePWM.
    pwm_output  : str -> Specifies the ePWM output channel (e.g., "out1a", "out1b").

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
        f.write("//###########################################################################\n")
        f.write("// FILE:   main.c\n")
        f.write("// AUTHOR: Tatiana Dal Busco\n")
        f.write("// DATE:   December 2024\n")
        f.write("//###########################################################################\n\n")

        f.write('#include "F28x_Project.h"\n\n')

        # Function prototypes
        f.write("void setup(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n")
        f.write(f"__interrupt void {number_epwm}_isr(void);\n\n")

        # Global variables
        f.write(f"static double Tsamp = {pwm_period}; // Time range\n")
        f.write("static double T = 0.0;         // Current time\n\n")

        # Main function
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    while (1) {}\n")
        f.write("}\n\n")

        # ISR for ePWM
        f.write("// ePWM1 Interrupt Service Routine\n")
        f.write(f"__interrupt void {number_epwm}_isr(void)\n")
        f.write("{\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n\n")
        f.write("    // Clear the interrupt flag for ePWM\n")
        f.write(f"    {epwm_regs}.ETCLR.bit.INT = 1;\n\n")
        f.write("    // Acknowledge the interrupt in PIE\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP3;\n")
        f.write("}\n\n")

        # Setup function
        f.write("// Sets up system control, peripherals, interrupts, and ePWM for the application\n")
        f.write("void setup(void)\n")
        f.write("{\n\n")
        f.write("    // Initialize the system control: clock, PLL, and peripheral settings\n")
        f.write("    InitSysCtrl();\n\n")
        f.write("    // Initialize General Purpose Input/Output pins\n")
        f.write("    InitGpio();\n\n")
        f.write("    // Disable all CPU interrupts\n")
        f.write("    DINT;\n\n")
        f.write("   // Initialize the Peripheral Interrupt Expansion (PIE) control registers\n")
        f.write("    InitPieCtrl();\n\n")
        f.write("    // Clear all interrupt enable registers\n")
        f.write("    IER = 0x0000;\n\n")
        f.write("    // Clear all interrupt flag registers\n")
        f.write("    IFR = 0x0000;\n\n")
        f.write("    // Initialize the PIE vector table with default interrupt vectors\n")
        f.write("    InitPieVectTable();\n\n")
        f.write(f"    {model}_init();\n\n")
        f.write("    // Link ISR to ePWM1 interrupt\n")
        f.write("    EALLOW;\n")
        f.write(f"    PieVectTable.{number_epwm_capsLock}_INT = &{number_epwm}_isr;\n")
        f.write("    EDIS;\n\n")
        f.write("    // Enable ePWM interrupt in PIE group 3\n")
        f.write(f"    PieCtrlRegs.PIEIER3.bit.INTx{number_epwm_digit} = 1;\n\n")
        f.write("    // Enable CPU interrupt group 3\n")
        f.write("    IER |= M_INT3;\n\n")
        f.write("    // Enable global interrupts and real-time interrupts\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n\n")
        f.write("}\n\n")

        # get_run_time function
        f.write("// Returns the current runtime\n")
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
    
        # get_Tsamp function
        f.write("// Returns the sampling time interval\n")
        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")


# state 3
def generate_main_mode2_timer(path_main, model, timer_period, adc_block):

    """
    Generates the main.c file for Mode 2 with Timer-based ADC triggering.

    Example Call:
    -------------
    generate_main_mode2_timer(
        path_main="/path/to/main.c", 
        model="exampleModel", 
        timer_period=10000, 
        adc_block={"module": "A", "soc": 0, "channel": 3}
    )

    Parameters:
    -----------
    path_main    : str -> The file path where the main.c file will be generated.
    model        : str -> The name of the project for which the file is generated.
    timer_period : int -> The timer period in microseconds for sampling intervals.
    adc_block    : dict -> A dictionary containing ADC configuration with keys:
        - "module": str -> The ADC module to use (e.g., "A", "B", "C", "D").
        - "soc": int -> The Start of Conversion (SOC) index to use.
        - "channel": int -> The ADC channel to use.

    Returns:
    --------
    -

    """

    Tsamp = float(timer_period)/1000000

    # Extract values
    module = adc_block.get('module', None)
    module_lower = module.lower() if module else None
    soc = int(adc_block.get('soc', 0))  # Convert np.int64 to standard Python int
    channel = int(adc_block.get('channel', 0))  # Convert np.int64 to standard Python int

    if(module == 'A'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx1 = 1;"
    if(module == 'B'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx2 = 1;"
    if(module == 'C'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx3 = 1;"
    if(module == 'D'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx4 = 1;"


    with open(path_main, 'w') as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   main.c\n")
        f.write("// AUTHOR: Tatiana Dal Busco\n")
        f.write("// DATE:   December 2024\n")
        f.write("//###########################################################################\n\n")
    
        f.write('#include "F28x_Project.h"\n\n')

        # Function Prototypes
        f.write("// Function Prototypes\n")
        f.write("void setup(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n")
        f.write(f"__interrupt void adc{module_lower}1_isr(void);\n")
        f.write("__interrupt void cpu_timer0_isr(void);\n\n")

        # Defines
        f.write("// Defines\n")
        f.write("#define RESULTS_BUFFER_SIZE 256\n\n")

        # Globals
        f.write("// Globals\n")
        f.write("Uint16 AdcResults[RESULTS_BUFFER_SIZE];\n")
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
        f.write("        }\n")
        f.write("    }\n")
        f.write("}\n\n")

        # Timer ISR
        f.write("// CPU Timer 0 ISR\n")
        f.write("__interrupt void cpu_timer0_isr(void)\n{\n")
        f.write("    CpuTimer0.InterruptCount++;\n\n")
        f.write("    // Force start ADC conversion (It must be the last one, compared to the other adcs)\n")
        f.write(f"    Adc{module_lower}Regs.ADCSOCFRC1.bit.SOC{soc} = 1;\n\n")
        f.write("    // Acknowledge interrupt in PIE\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")

        # ADC ISR
        f.write("// ADC ISR\n")
        f.write(f"__interrupt void adc{module_lower}1_isr(void)\n{{\n\n")
        f.write("    // Store ADC result in buffer\n")
        f.write(f"    AdcResults[resultsIndex++] = Adc{module_lower}ResultRegs.ADCRESULT{soc};\n")
        f.write("    if (resultsIndex >= RESULTS_BUFFER_SIZE)\n")
        f.write("    {\n")
        f.write("        resultsIndex = 0; // Reset the buffer index\n")
        f.write("        bufferFull = 1;   // Set the buffer full flag\n")
        f.write("    }\n\n")
        f.write("    // Clear ADC interrupt flag\n")
        f.write(f"    Adc{module_lower}Regs.ADCINTFLGCLR.bit.ADCINT1 = 1;\n\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n\n")
        f.write("    // Acknowledge the interrupt in PIE\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")

        # Setup Function
        f.write("// Sets up system control, peripherals, interrupts, and ePWM for the application\n")
        f.write("void setup(void)\n")
        f.write("{\n\n")
        f.write("    // Initialize the system control: clock, PLL, and peripheral settings\n")
        f.write("    InitSysCtrl();\n\n")
        f.write("    // Initialize General Purpose Input/Output pins\n")
        f.write("    InitGpio();\n\n")
        f.write("    // Disable all CPU interrupts\n")
        f.write("    DINT;\n\n")
        f.write("    // Initialize the Peripheral Interrupt Expansion (PIE) control registers\n")
        f.write("    InitPieCtrl();\n\n")
        f.write("    // Clear all interrupt enable registers\n")
        f.write("    IER = 0x0000;\n\n")
        f.write("    // Clear all interrupt flag registers\n")
        f.write("    IFR = 0x0000;\n\n")
        f.write("    // Initialize the PIE vector table with default interrupt vectors\n")
        f.write("    InitPieVectTable();\n\n")
        f.write(f"    {model}_init();\n\n")
        f.write("    // Map ISRs to interrupt vectors\n")
        f.write("    EALLOW;\n")
        f.write("    PieVectTable.TIMER0_INT = &cpu_timer0_isr;\n")
        f.write(f"    PieVectTable.ADC{module}1_INT = &adc{module_lower}1_isr;\n")
        f.write("    EDIS;\n\n")
        f.write("    // Configure CPU Timer 0\n")
        f.write("    InitCpuTimers();\n")
        f.write(f"    ConfigCpuTimer(&CpuTimer0, 200, {timer_period});\n")
        f.write("    CpuTimer0Regs.TCR.all = 0x4000; // Start Timer 0\n\n")
        f.write("    // Enable PIE interrupts for Timer 0 and ADC\n")
        f.write("    IER |= M_INT1;                     // Enable CPU interrupt group 1\n")
        f.write("    PieCtrlRegs.PIEIER1.bit.INTx7 = 1; // Enable PIE interrupt for Timer 0\n")
        f.write(f"    {interrupt}                       // Enable PIE interrupt for ADC\n\n")
        f.write("    // Enable global and real-time interrupts\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n\n")
        f.write("}\n\n")

        # get_run_time function
        f.write("// Returns the current runtime\n")
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
    
        # get_Tsamp function
        f.write("// Returns the sampling time interval\n")
        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")


# state 4
def generate_main_mode2_epwm(path_main, model, tbprd, pwm_output, adc_block):

    """
    Generates the main.c file for Mode 2 with ePWM-based ADC triggering.

     Example Call:
    -------------
    generate_main_mode2_epwm(
        path_main="/path/to/main.c", 
        model="exampleModel", 
        tbprd=2000, 
        pwm_output="out1a", 
        adc_block={"module": "A", "soc": 0, "channel": 3}
    )

    Parameters:
    -----------
    path_main   : str -> The file path where the main.c file will be generated.
    model       : str -> The name of the project for which the file is generated.
    tbprd       : int -> Time-base period for ePWM in clock cycles.
    pwm_output  : str -> The ePWM output channel (e.g., "out1a", "out2b") used for ADC triggering.
    adc_block   : dict -> A dictionary containing ADC configuration with keys:
        - "module": str -> The ADC module to use (e.g., "A", "B", "C", "D").
        - "soc": int -> The Start of Conversion (SOC) index to use.
        - "channel": int -> The ADC channel to use.

    Returns:
    --------
    -

    """

    pwm_period = (2 * int(tbprd)) / 1e8
    
    if pwm_output == "out1a" or pwm_output == "out1b":
        epwmRegs = "EPwm1Regs"

    elif pwm_output == "out2a" or pwm_output == "out2b":
        epwmRegs = "EPwm2Regs"

    elif pwm_output == "out3a" or pwm_output == "out3b":
        epwmRegs = "EPwm3Regs"

    elif pwm_output == "out4a" or pwm_output == "out4b":
        epwmRegs = "EPwm4Regs"

    elif pwm_output == "out5a" or pwm_output == "out5b":
        epwmRegs = "EPwm5Regs"

    elif pwm_output == "out6a" or pwm_output == "out6b":
        epwmRegs = "EPwm6Regs"

    elif pwm_output == "out7a" or pwm_output == "out7b":
        epwmRegs = "EPwm7Regs"

    elif pwm_output == "out8a" or pwm_output == "out8b":
        epwmRegs = "EPwm8Regs"

    elif pwm_output == "out9a" or pwm_output == "out9b":
        epwmRegs = "EPwm9Regs"

    elif pwm_output == "out10a" or pwm_output == "out10b":
        epwmRegs = "EPwm10Regs"

    elif pwm_output == "out11a" or pwm_output == "out11b":
        epwmRegs = "EPwm11Regs"

    elif pwm_output == "out12a" or pwm_output == "out12b":
        epwmRegs = "EPwm12Regs"

    # Extract values
    module = adc_block.get('module', None)
    module_lower = module.lower() if module else None
    soc = int(adc_block.get('soc', 0))
    channel = int(adc_block.get('channel', 0))

    if(module == 'A'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx1 = 1;"
    if(module == 'B'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx2 = 1;"
    if(module == 'C'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx3 = 1;"
    if(module == 'D'):
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx4 = 1;"

    with open(path_main, "w") as f:

        f.write("//###########################################################################\n")
        f.write("// FILE:   main.c\n")
        f.write("// AUTHOR: Tatiana Dal Busco\n")
        f.write("// DATE:   December 2024\n")
        f.write("//###########################################################################\n\n")
    
        # Included Files
        f.write('#include "F28x_Project.h"\n\n')
    
        # Function Prototypes
        f.write("// Function Prototypes\n")
        f.write("void ConfigureADC(void);\n")
        f.write("void SetupADCEpwm(Uint16 channel);\n")
        f.write("void setup(void);\n")
        f.write("void loop(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n")
        f.write(f"interrupt void adc{module_lower}1_isr(void);\n\n")
    
        # Defines and Globals
        f.write("// Defines\n")
        f.write("#define RESULTS_BUFFER_SIZE 256\n\n")
        f.write("// Globals\n")
        f.write("Uint16 AdcResults[RESULTS_BUFFER_SIZE];\n")
        f.write("Uint16 resultsIndex;\n")
        f.write("volatile Uint16 bufferFull;\n")
        f.write(f"static double Tsamp = {pwm_period}; // Time range\n")
        f.write("static double T = 0.0;        // Current time\n\n")
    
        # Main Function
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    loop();\n")
        f.write("}\n\n")
    
        # adca1_isr Function
        f.write(f"// adc{module_lower}1_isr - Read ADC Buffer in ISR\n")
        f.write(f"// Everytime ADC complete a conversion, the value is memorized in the AdcResults buffer.\n")
        f.write(f"interrupt void adc{module_lower}1_isr(void)\n")
        f.write("{\n\n")
        f.write("   // Store ADC result in buffer\n")
        f.write(f"    AdcResults[resultsIndex++] = Adc{module_lower}ResultRegs.ADCRESULT{soc};\n")
        f.write("    if(RESULTS_BUFFER_SIZE <= resultsIndex)\n")
        f.write("    {\n")
        f.write("        resultsIndex = 0; // Reset the buffer index\n")
        f.write("        bufferFull = 1;   // Mark the buffer as full\n")
        f.write("    }\n\n")
        f.write("   // Clear ADC interrupt flag\n")
        f.write(f"    Adc{module_lower}Regs.ADCINTFLGCLR.bit.ADCINT1 = 1;\n\n")
        f.write("    // Check if overflow has occurred\n")
        f.write(f"    if(1 == Adc{module_lower}Regs.ADCINTOVF.bit.ADCINT1)\n")
        f.write("    {\n")
        f.write(f"        Adc{module_lower}Regs.ADCINTOVFCLR.bit.ADCINT1 = 1; // Clear overflow flag\n")
        f.write(f"        Adc{module_lower}Regs.ADCINTFLGCLR.bit.ADCINT1 = 1; // Clear interrupt flag\n")
        f.write("    }\n\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n\n")
        f.write("    // Acknowledge interrupt in PIE\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")

        # Setup Function
        f.write("// Sets up system control, peripherals, interrupts, and ePWM for the application\n")
        f.write("void setup(void)\n")
        f.write("{\n\n")
        f.write("    // Initialize the system control: clock, PLL, and peripheral settings\n")
        f.write("    InitSysCtrl();\n\n")
        f.write("    // Initialize General Purpose Input/Output pins\n")
        f.write("    InitGpio();\n\n")
        f.write("    // Disable all CPU interrupts\n")
        f.write("    DINT;\n\n")
        f.write("    // Initialize the Peripheral Interrupt Expansion (PIE) control registers\n")
        f.write("    InitPieCtrl();\n\n")
        f.write("    // Clear all interrupt enable registers\n")
        f.write("    IER = 0x0000;\n\n")
        f.write("    // Clear all interrupt flag registers\n")
        f.write("    IFR = 0x0000;\n\n")
        f.write("    // Initialize the PIE vector table with default interrupt vectors\n")
        f.write("    InitPieVectTable();\n\n")
        f.write("    // Map the ADC ISR to the interrupt vector\n")
        f.write("    EALLOW;\n")
        f.write(f"    PieVectTable.ADC{module}1_INT = &adc{module_lower}1_isr;\n")
        f.write("    EDIS;\n\n")
        f.write("    // Configure ePWM for ADC triggering\n")
        f.write("    EALLOW;\n")
        f.write(f"    {epwmRegs}.ETSEL.bit.SOCAEN = 0; // Disable SOC\n")
        f.write(f"    {epwmRegs}.ETSEL.bit.SOCASEL = 6;// Select SOC on up-down count\n")
        f.write(f"    {epwmRegs}.ETPS.bit.SOCAPRD = 1; // Generate pulse on 1st event\n")
        f.write("    EDIS;\n\n")
        f.write(f"    {model}_init();\n\n")
        f.write("    EALLOW;\n")
        f.write(f"    {epwmRegs}.TBCTL.bit.CTRMODE = 3; // freeze counter\n")
        f.write("    EDIS;\n\n")
        f.write("    // Enable global and real-time interrupts\n")
        f.write("    IER |= M_INT1;\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n\n")
        f.write("    // Initialize the ADC results buffer\n")
        f.write("    for(resultsIndex = 0; resultsIndex < RESULTS_BUFFER_SIZE; resultsIndex++)\n")
        f.write("    {\n")
        f.write("        AdcResults[resultsIndex] = 0;\n")
        f.write("    }\n")
        f.write("    resultsIndex = 0; // Reset buffer index\n")
        f.write("    bufferFull = 0;   // Reset buffer full flag\n\n")
        f.write("    // Enable PIE interrupt for ADC\n")
        f.write(f"    {interrupt}\n\n")
        f.write("    // Enable Time Base Clock Sync\n")
        f.write("    EALLOW;\n")
        f.write("    CpuSysRegs.PCLKCR0.bit.TBCLKSYNC = 1;\n")
        f.write("    EDIS;\n\n")
        #f.write("    EALLOW;\n")
        f.write("}\n\n")
    
        # Loop Function
        f.write("// Main loop - Continuously processes ADC conversions\n")
        f.write("void loop(void)\n")
        f.write("{\n\n")
        f.write("    do\n")
        f.write("    {\n\n")
        f.write("        // Start ePWM for ADC triggering\n")
        f.write(f"        {epwmRegs}.ETSEL.bit.SOCAEN = 1;\n")
        f.write(f"        {epwmRegs}.TBCTL.bit.CTRMODE = 2; // Set ePWM counter to up-down mode\n\n")
        f.write("        // Wait until the buffer is full\n")
        f.write("        while(!bufferFull);\n")
        f.write("        bufferFull = 0; // Reset buffer full flag\n\n")
        f.write("        // Stop ePWM\n")
        f.write(f"        {epwmRegs}.ETSEL.bit.SOCAEN = 0;  // Disable SOC\n")
        f.write(f"        {epwmRegs}.TBCTL.bit.CTRMODE = 3; // Freeze ePWM counter\n\n")
        f.write("        // At this point, AdcResults[] contains ADC conversion results\n\n")
        f.write("    } while(1);\n")
        f.write("}\n\n")

        # get_run_time function
        f.write("// Returns the current runtime\n")
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
    
        # get_Tsamp function
        f.write("// Returns the sampling time interval\n")
        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")
    
#################################################################################################################################################
# Functions called in other scripts to generate the project and to set global configurations
#################################################################################################################################################

def press_configure_button():
    
    """
    Handles the configuration setup triggered by the configure button.

    This function checks the environment (e.g., WSL detection) and opens a configuration 
    window for the user to set or adjust settings. If the configuration is saved, it 
    proceeds to validate paths.
    
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
    ti_path_saved = config.get('ti_path', '')
    c2000Ware_path_saved = config.get('c2000Ware_path', '')
    compiler_saved = config.get('compiler_version', '')

    check_paths(ti_path_saved, c2000Ware_path_saved, compiler_saved)


def create_project_structure(model, blocks_list):
    
    """
    Initializes the directory structure and configuration for a new project.

    This function sets up the required directory structure, configuration files, and 
    source files for a Code Composer Studio (CCS) project. It validates user settings, 
    processes the provided schema (blocks_list), and ensures compatibility with the 
    PysimCoder environment. It also checks for WSL-specific path requirements and 
    handles configuration or schema errors.

    Example Call:
    -------------
    create_project_structure("my_model", blocks)

    Parameters:
    -----------
    model       : str -> The name of the project to be created.
    blocks_list : list -> A list of blocks defining the project schema.

    Returns:
    --------
    -

    """

    triggerOnePWM = None

    # Extracts functions from schema blocks
    functions_name = check_blocks_set(blocks_list)
    functions_present_schema = check_blocks_list(blocks_list)

    # Initialize the PyQt application
    app = QApplication.instance() or QApplication([])

    # Ensure the environment is properly configured for WSL
    check_wsl_environment()

    # Define paths for configuration files and check if global config exists
    parent_dir = os.path.dirname(os.path.abspath('.'))
    config_path_outside_gen = os.path.join(parent_dir, general_config.path)

    if not os.path.isfile(config_path_outside_gen):
        QMessageBox.information(None, "File Status", f"{general_config.get_name()} not found in {parent_dir} .\nYou can set the paths under the menu settings -> settings -> configure")
        return 
    
    # Load general configuration settings
    general_config.path = config_path_outside_gen
    config = general_config.load()
    ti_folder_path = config.get('ti_path', '')
    c2000Ware_path = config.get('c2000Ware_path', '')
    compiler_version = config.get('compiler_version', '')

    # Convert paths if running under WSL
    if isInWSL:

        # Wsl path
        if ti_folder_path.startswith("/mnt/c/"):

            # Convert in a windows path
            ti_folder_path = convert_path_for_windows(ti_folder_path)
        
        # Path for windows, but it must be changed from \\ to / 
        else:
            ti_folder_path = ti_folder_path.replace('\\', '/')
        if c2000Ware_path.startswith("/mnt/c/"):
            c2000Ware_path = convert_path_for_windows(c2000Ware_path)
        else:
            c2000Ware_path = c2000Ware_path.replace('\\', '/')

    # Define paths based on environment variables
    pysimCoder_path = os.environ.get('PYSUPSICTRL')
    CodeGen_path = pysimCoder_path + '/CodeGen'
    include_path = pysimCoder_path + '/CodeGen/Delfino/include'
    src_path = pysimCoder_path + '/CodeGen/Delfino/src'
    pyblock_path = pysimCoder_path + '/CodeGen/Common/include'
    devices_path = pysimCoder_path + '/CodeGen/Delfino/devices'
    targetConfigs_path = pysimCoder_path + '/CodeGen/Delfino/targetConfigs'

    # Create project directory structure
    project_dir = f"./{model}_project"
    src_dir = os.path.join(project_dir, "src")
    include_dir = os.path.join(project_dir, "include")
    targetConfigs_dir = os.path.join(project_dir, "targetConfigs")

    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(include_dir, exist_ok=True)
    os.makedirs(targetConfigs_dir, exist_ok=True)

    # Move the source file to the src directory
    source_file = f'{model}.c'
    destination_file = os.path.join(src_dir, f'{model}.c')
    if os.path.exists(source_file):
        if os.path.exists(destination_file):
            os.remove(destination_file)
        shutil.move(source_file, src_dir)
    
    # Open project configuration window and validate inputs
    config_data = open_project_config_window(model)
    if not config_data:
        QMessageBox.warning(None, "Project Cancelled", f"Project {model} has been cancelled.")
        return False

    save_project_config_file(model, config_data)
    config_window = ProjectConfigWindow(model)
    state = config_window.get_current_state()
    main_file = os.path.join(src_dir, "main.c")

    # Validate ePWM blocks for state 2 and 4
    if state in [2, 4]:
        check_result = check_epwm_block(functions_present_schema)

        if check_result == 1:
            QMessageBox.warning(None, "Error", f"ePWM block is missing from the schema. At least one ePWM block is required. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return

        # Check ADC parameters if state is 4
        if state == 4:
            adc_blocks = extract_adc_parameters(blocks_list, 'adcblk')
            if (adc_blocks == None):
                QMessageBox.warning(None, "Error", f"Module A, channel 0 is already busy managing synchronization. Project {model} has been cancelled.")
                project_dir = f"./{model}_project"
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
                return  

    # Generate main file based on state
    if state == 1:
        timer_period = config_data.get("timer_period")
        dispatch_main_generation(state, main_file, model, timer_period, None, None, None)

    if state == 2:
        epwm_output_mode1 = config_data.get("epwm_output_mode1")

        tbprd, pwm_output = find_matching_pwm_output(blocks_list, "epwmblk", epwm_output_mode1)

        if tbprd is None and pwm_output is None:
            QMessageBox.warning(None, "Error", f"The epwm block with epwm output {epwm_output_mode1} that generates the interrupt is missing. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return
        
        dispatch_main_generation(state, main_file, model, None, tbprd, pwm_output, None)

    if state in [3, 4]:
        result = extract_adc_parameters(blocks_list, 'adcblk')

        if result == -1:
            QMessageBox.warning(None, "Error", f"No ADC block with generate Interrupt == 1 was found. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return

        elif result == -2:
            QMessageBox.warning(None, "Error", f"Multiple ADC blocks with generate Interrupt == 1 were found. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return
 
    if state == 3:
        timer_period = config_data.get("timer_period")
        dispatch_main_generation(state, main_file, model, timer_period, None, None, result)

    if state == 4:
        epwm_output_mode2 = config_data.get("epwm_output_mode2")

        tbprd, pwm_output = find_matching_pwm_output(blocks_list, "epwmblk", epwm_output_mode2)

        if tbprd is None and pwm_output is None:
            QMessageBox.warning(None, "Error", f"The epwm block with epwm output {epwm_output_mode2} that trigger the ADC is missing. Project {model} has been cancelled.")
            project_dir = f"./{model}_project"
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return
        dispatch_main_generation(state, main_file, model, None, tbprd, pwm_output, result)
        
        # Needed to figure out which epwm triggers the adc.
        # Added as global define in .cproject file.
        if pwm_output == "out1a" or pwm_output == "out1b":
            triggerOnePWM = 5

        elif pwm_output == "out2a" or pwm_output == "out2b":
            triggerOnePWM = 7

        elif pwm_output == "out3a" or pwm_output == "out3b":
            triggerOnePWM = 9

        elif pwm_output == "out4a" or pwm_output == "out4b":
            triggerOnePWM = 11

        elif pwm_output == "out5a" or pwm_output == "out5b":
            triggerOnePWM = 13

        elif pwm_output == "out6a" or pwm_output == "out6b":
            triggerOnePWM = 15

        elif pwm_output == "out7a" or pwm_output == "out7b":
            triggerOnePWM = 17

        elif pwm_output == "out8a" or pwm_output == "out8b":
            triggerOnePWM = 19

        elif pwm_output == "out9a" or pwm_output == "out9b":
            triggerOnePWM = 21

        elif pwm_output == "out10a" or pwm_output == "out10b":
            triggerOnePWM = 23

        elif pwm_output == "out11a" or pwm_output == "out11b":
            triggerOnePWM = 25

        elif pwm_output == "out12a" or pwm_output == "out12b":
            triggerOnePWM = 27

    # Copy necessary files
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
    create_ccsproject_file(model, compiler_version)
    create_project_file(model, c2000Ware_path)
    create_cproject_file(model, ti_folder_path, c2000Ware_path, include_dir_absolute_path, state, compiler_version, triggerOnePWM)

    # Displays a message indicating that the project was created successfully
    QMessageBox.information(None, "Project Status", "Project successfully created")
