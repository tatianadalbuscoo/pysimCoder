import os
import sys
import shutil
from numpy import nonzero, ones, asmatrix, size, array, zeros
import json
#import tkinter as tk
#from tkinter import messagebox, filedialog
from supsisim.qtvers import *


""" The following commands are provided:

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
    Classe per rappresentare un file di configurazione generico.
    """
    def __init__(self, name, extension="json"):
        """
        Inizializza un file di configurazione con nome ed estensione.
        """
        self.name = name
        self.extension = extension
        self.path = f"{self.name}.{self.extension}"

    def get_name(self, with_extension=True):
        return self.path if with_extension else self.name

    def exists(self):
        """
        Verifica se il file di configurazione esiste.
        """
        return os.path.isfile(self.path)

    def load(self):
        """
        Carica il contenuto del file di configurazione, se esiste.
        """
        if self.exists():
            with open(self.path, "r") as file:
                return json.load(file)
        return {}

    def save(self, data):
        """
        Salva i dati in formato JSON nel file di configurazione.
        """
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4)

    def delete(self):
        """
        Elimina il file di configurazione, se esiste.
        """
        if self.exists():
            os.remove(self.path)

    def __str__(self):
        """
        Rappresentazione testuale del file di configurazione.
        """
        return f"ConfigFile(name={self.name}, path={self.path})"


class ProjectConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Configuration")
        self.resize(800, 300)

        self.init_ui()

    def init_ui(self):
        # Layout principale
        layout = QVBoxLayout()

        # Spiegazione delle modalità
        explanation_label = QLabel(
            "Mode 1: Each module works independently. A peripheral (Timer or PWM) provides the time base via interrupt.\n"
            "Mode 2: A peripheral (Timer or PWM) triggers ADC conversion, and the ADC generates an interrupt when conversion is done.\n"
        )
        explanation_label.setWordWrap(True)
        layout.addWidget(explanation_label)

        # Menu a tendina per selezionare la modalità
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["-", "1", "2"])  # Aggiunge "-" come valore predefinito e le modalità 1 e 2
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)

        # Imposta il combobox per espandersi
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Layout per selezionare il tipo di periferica (PWM o Timer) per modalità 1
        self.peripheral_layout = QHBoxLayout()
        self.peripheral_label = QLabel("Interrupt Peripheral:")
        self.peripheral_combo = QComboBox()
        self.peripheral_combo.addItems(["-"])  # Solo "-" all'inizio
        self.peripheral_combo.currentTextChanged.connect(self.on_peripheral_changed)
        self.peripheral_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.peripheral_layout.addWidget(self.peripheral_label)
        self.peripheral_layout.addWidget(self.peripheral_combo)

        # Nasconde il layout della periferica all'inizio
        self.peripheral_label.hide()
        self.peripheral_combo.hide()
        layout.addLayout(self.peripheral_layout)

        # Menu a tendina per il Trigger ADC - visibile solo per modalità 2
        self.trigger_adc_layout = QHBoxLayout()
        self.trigger_adc_label = QLabel("Trigger ADC:")
        self.trigger_adc_combo = QComboBox()
        self.trigger_adc_combo.addItems(["-"])  # Solo "-" all'inizio
        self.trigger_adc_combo.currentTextChanged.connect(self.on_trigger_adc_changed)
        self.trigger_adc_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.trigger_adc_layout.addWidget(self.trigger_adc_label)
        self.trigger_adc_layout.addWidget(self.trigger_adc_combo)

        # Nasconde il layout del Trigger ADC all'inizio
        self.trigger_adc_label.hide()
        self.trigger_adc_combo.hide()
        layout.addLayout(self.trigger_adc_layout)

        # Campo per il periodo del timer - condiviso tra le modalità 1 e 2
        self.timer_period_layout = QHBoxLayout()
        self.timer_period_label = QLabel("Period Timer [ms]:")
        self.timer_period_input = QLineEdit()
        self.timer_period_input.setPlaceholderText("Enter timer period")
        self.timer_period_layout.addWidget(self.timer_period_label)
        self.timer_period_layout.addWidget(self.timer_period_input)

        # Nasconde il layout del periodo del timer all'inizio
        self.timer_period_label.hide()
        self.timer_period_input.hide()
        layout.addLayout(self.timer_period_layout)

        # Spacer per spingere i pulsanti verso il basso
        layout.addStretch()

        # Layout per i bottoni
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_close)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_and_close)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # Aggiunge i bottoni al layout principale
        layout.addLayout(button_layout)

        # Imposta il layout principale
        self.setLayout(layout)

    def on_mode_changed(self, mode):
        """
        Mostra o nasconde i campi in base alla modalita scelta.
        """
        if mode == "-":
            # Nasconde tutto se si torna a "-"
            self.peripheral_label.hide()
            self.peripheral_combo.hide()
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            self.trigger_adc_label.hide()
            self.trigger_adc_combo.hide()
            return

        if "-" in self.mode_combo.itemText(0):
            # Rimuove l'opzione "-" dalla modalità dopo la prima selezione
            self.mode_combo.removeItem(0)

        if mode == "1":
            # Mostra il menu periferica
            self.peripheral_combo.clear()
            self.peripheral_combo.addItems(["-", "PWM", "Timer"])  # Aggiunge "-" e le opzioni per modalità 1
            self.peripheral_label.show()
            self.peripheral_combo.show()

            # Nasconde i campi specifici per modalità 2
            self.trigger_adc_label.hide()
            self.trigger_adc_combo.hide()
            self.timer_period_label.hide()
            self.timer_period_input.hide()
        elif mode == "2":
            # Mostra il menu Trigger ADC
            self.trigger_adc_combo.clear()
            self.trigger_adc_combo.addItems(["-", "PWM", "Timer"])  # Aggiunge "-" e le opzioni per modalità 2
            self.trigger_adc_label.show()
            self.trigger_adc_combo.show()

            # Nasconde inizialmente il Period Timer finché non viene selezionato Timer
            self.timer_period_label.hide()
            self.timer_period_input.hide()

            # Nasconde il menu periferica
            self.peripheral_label.hide()
            self.peripheral_combo.hide()

    def on_peripheral_changed(self, peripheral):
        """
        Mostra o nasconde il campo per il periodo del timer in base alla periferica scelta (solo per modalita 1).
        """
        if peripheral == "-":
            # Nasconde il periodo del timer se si torna a "-"
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            return

        if "-" in self.peripheral_combo.itemText(0):
            # Rimuove l'opzione "-" dopo la prima selezione
            self.peripheral_combo.removeItem(0)

        if peripheral == "Timer":
            self.timer_period_label.show()
            self.timer_period_input.show()
        else:
            self.timer_period_label.hide()
            self.timer_period_input.hide()

    def on_trigger_adc_changed(self, trigger):
        """
        Mostra o nasconde il campo per il periodo del timer in base al trigger ADC scelto (solo per modalita 2).
        """
        if trigger == "-":
            # Nasconde il periodo del timer se si torna a "-"
            self.timer_period_label.hide()
            self.timer_period_input.hide()
            return

        if "-" in self.trigger_adc_combo.itemText(0):
            # Rimuove l'opzione "-" dopo la prima selezione
            self.trigger_adc_combo.removeItem(0)

        if trigger == "Timer":
            self.timer_period_label.show()
            self.timer_period_input.show()
        else:
            self.timer_period_label.hide()
            self.timer_period_input.hide()

    def cancel_and_close(self):
        self.reject()  # Chiude con stato "Rejected"

    def save_and_close(self):
        """
        Salva la configurazione selezionata e stampa i risultati.
        """
        selected_mode = self.mode_combo.currentText()  # Ottiene la modalità selezionata
        if selected_mode == "1":
            selected_peripheral = self.peripheral_combo.currentText()
            if selected_peripheral == "Timer":
                timer_period = self.timer_period_input.text() or "Not provided"
                print(f"Selected Mode: {selected_mode}, Peripheral: {selected_peripheral}, Timer Period: {timer_period}")
            else:
                print(f"Selected Mode: {selected_mode}, Peripheral: {selected_peripheral}")
        elif selected_mode == "2":
            selected_trigger = self.trigger_adc_combo.currentText()
            if selected_trigger == "Timer":
                timer_period = self.timer_period_input.text() or "Not provided"
                print(f"Selected Mode: {selected_mode}, ADC Trigger: {selected_trigger}, Timer Period: {timer_period}")
            else:
                print(f"Selected Mode: {selected_mode}, ADC Trigger: {selected_trigger}")
        self.accept()  # Chiude con stato "Accepted"









def save_general_config_file(config_file: ConfigFile, ti_path, c2000Ware_path):
    config_data = {
        "ti_path": ti_path,
        "c2000Ware_path": c2000Ware_path,
    }
    config_file.save(config_data)
    QMessageBox.information(None, "General configs Saved", "Paths saved successfully!")



# to do: metodo per gestire il salvataggio del config file del progetto



def open_config_window():
    app = QApplication.instance() or QApplication([])
    config_window = ConfigWindow()
    result = config_window.exec()  # Ritorna QDialog.Accepted o QDialog.Rejected
    return result == QDialog.Accepted  # True se salvato, False se annullato

def open_project_config_window():
    app = QApplication.instance() or QApplication([])
    project_config_window = ProjectConfigWindow()
    result = project_config_window.exec()  # Ritorna QDialog.Accepted o QDialog.Rejected
    return result == QDialog.Accepted  # True se salvato, False se annullato



# File name where to save the paths
general_config = ConfigFile("general_config")


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




class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration")
        self.resize(800, 200)

        # Carica la configurazione esistente
        config = general_config.load()
        self.ti_path = config.get('ti_path', '')
        self.c2000Ware_path = config.get('c2000Ware_path', '')

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Campo per il percorso TI
        ti_layout = QHBoxLayout()
        ti_label = QLabel("TI folder path:")
        self.ti_input = QLineEdit(self.ti_path)
        ti_browse = QPushButton("Browse")
        ti_browse.clicked.connect(self.browse_ti_path)
        ti_layout.addWidget(ti_label)
        ti_layout.addWidget(self.ti_input)
        ti_layout.addWidget(ti_browse)

        # Campo per il percorso C2000Ware
        c2000_layout = QHBoxLayout()
        c2000_label = QLabel("C2000Ware_4_01_00_00 folder path:")
        self.c2000_input = QLineEdit(self.c2000Ware_path)
        c2000_browse = QPushButton("Browse")
        c2000_browse.clicked.connect(self.browse_c2000_path)
        c2000_layout.addWidget(c2000_label)
        c2000_layout.addWidget(self.c2000_input)
        c2000_layout.addWidget(c2000_browse)

        # Bottone per salvare
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_close)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_and_close)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # Aggiunge tutto al layout
        layout.addLayout(ti_layout)
        layout.addLayout(c2000_layout)
        layout.addLayout(button_layout)

        # Imposta il layout principale
        self.setLayout(layout)

    def browse_ti_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select TI folder path")
        if path:
            self.ti_input.setText(path)

    def browse_c2000_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select C2000Ware folder path")
        if path:
            self.c2000_input.setText(path)

    def cancel_and_close(self):
        self.reject()  # Chiude con stato "Rejected"

    def save_and_close(self):
        save_general_config_file(general_config, self.ti_input.text(), self.c2000_input.text())
        self.accept()  # Chiude con stato "Accepted"

    def closeEvent(self, event):
        # Assicura che lo stato "Rejected" venga impostato se chiuso con la croce
        self.reject()




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
    str
    - The converted WSL-compatible path. If the path is already compatible or the conditions are not met, returns the original path unchanged.

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
    str
    - The converted Windows-compatible path. If the path is not a WSL path or we aren't in a wsl envoirment the original path is returned.

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





def copy_file_if_exists(path_file, dest_dir):

    """ Copies a file to a destination directory if it exists.

    This function checks if a specified file exists. If the file is found, 
    it copies it to the provided destination directory.

    Example Call:
    -------------
    copy_file_if_exists(path_file="path/to/file", dest_dir="path/to/destination")

    Parameters:
    -----------
    path_file  : The path to the file to copy.
    dest_dir   : The directory where the file should be copied if it exists..

    Returns:
    --------
    -

    """

    if os.path.exists(path_file):
        shutil.copy(path_file, dest_dir)


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
    dict
    - A dictionary containing updated paths.

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
    """Handles the configuration setup process when the configure button is pressed."""
    check_wsl_environment()
    app = QApplication.instance() or QApplication([])

    # Apri la finestra di configurazione
    if not open_config_window():
        return

    # Continua solo se la configurazione è stata salvata
    config = general_config.load()
    ti_path = config.get('ti_path', '')
    c2000Ware_path = config.get('c2000Ware_path', '')

    check_paths(ti_path, c2000Ware_path)





def check_blocks(blocks):
    """
    Analizza i blocchi e restituisce un set delle funzioni utilizzate.

    Parameters
    ----------
    blocks : list
        Lista di blocchi con attributi come 'fcn' e 'name'.

    Returns
    -------
    set
        Set delle funzioni dei blocchi.
    """
    block_functions = set()

    for block in blocks:
        block_function = getattr(block, 'fcn', 'N/A')

        if block_function != 'N/A':
            block_functions.add(block_function)

    return block_functions


def find_and_copy_c_files(function_names, CodeGen_path, dest_c_dir, dest_h_dir):
    print(f"Function names to process: {function_names}")    

    found_files = {}

    # Crea le directory di destinazione se non esistono
    os.makedirs(dest_c_dir, exist_ok=True)
    os.makedirs(dest_h_dir, exist_ok=True)

    # Regole speciali per funzioni specifiche
    special_cases = {
        "adcblk": ["adcblk.c", "adc.c", "adc.h"],
        "inputGPIOblk": ["inputGPIOblk.c", "button.c", "button.h"],
        "outputGPIOblk": ["outputGPIOblk.c", "led.c", "led.h"],
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

    # Ciclo attraverso le funzioni
    for function in function_names:
        found_files[function] = {"c_file": None, "h_file": None}

        # Determina i file da cercare (speciali o standard)
        files_to_search = special_cases.get(function, [f"{function}.c"])

        # Cerca e copia i file
        for file_name in files_to_search:
            dest_dir = dest_c_dir if file_name.endswith(".c") else dest_h_dir
            for root, _, files in os.walk(CodeGen_path):
                if file_name in files:
                    source_path = os.path.join(root, file_name)
                    dest_path = os.path.join(dest_dir, file_name)
                    shutil.copy(source_path, dest_path)
                    key = "c_file" if file_name.endswith(".c") else "h_file"
                    found_files[function][key] = dest_path
                    break  # Trova il file e interrompe la ricerca

    return found_files









def create_project_structure(model, blocks):
    
    """ Creates a project structure based on the specified model name.

    This function sets up the directory structure, configuration files, and main 
    source file needed for a project. It verifies WSL paths if necessary, copies 
    relevant files, and generates additional project files for a Code Composer 
    Studio (CCS) project.

    Example Call:
    -------------
    create_project_structure("my_model")

    Parameters:
    -----------
    model : The name of project

    Returns:
    --------
    -

    """
    open_project_config_window()
    functions_name = check_blocks(blocks)

    # Assicurati che QApplication sia attiva
    app = QApplication.instance() or QApplication([])

    check_wsl_environment()

    # Define paths for config.json in the directory where {model}_gen will be created and inside {model}_gen
    parent_dir = os.path.dirname(os.path.abspath('.'))
    config_path_outside_gen = os.path.join(parent_dir, general_config.path)

    # Check if config.json exists in the parent directory and copy it to {model}_gen, overwriting if needed
    if not os.path.isfile(config_path_outside_gen):
        QMessageBox.information(None, "File Status", f"{general_config.get_name()} not found in {parent_dir} .\nYou can set the paths under the menu settings -> settings -> configure")
        return 
        #os.makedirs(os.path.join(parent_dir, f'{model}_gen'), exist_ok=True)  # Ensure {model}_gen directory exists
        #shutil.copy(config_path_outside_gen, config_path_inside_gen)  # Copy and overwrite if exists
    
    # Load the configuration from the parent directory
    general_config.path = config_path_outside_gen  # Update the path dynamically
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

    # Create the main file adc_soc_epwm_cpu01.c
    main_file = os.path.join(src_dir, "cpu_timers_cpu01.c")

    with open(main_file, 'w') as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   cpu_timers_cpu01.c\n")
        f.write("// TITLE:  CPU Timers Example for F2837xD.\n")
        f.write("//###########################################################################\n\n")
    
        f.write('#include "F28x_Project.h"\n\n')  # Include principale per il progetto
    
        # Prototipi delle funzioni
        f.write("__interrupt void cpu_timer0_isr(void);\n")
        f.write("void setup(void);\n")
        f.write("double get_run_time(void);\n")
        f.write("double get_Tsamp(void);\n\n")
    
        # Variabili globali
        f.write("static double Tsamp = 0.01;  // Intervallo temporale 10 ms\n")
        f.write("static double T = 0.0;      // Tempo corrente\n\n")
    
        # Funzione main
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    while (1) {}\n")
        f.write(f"    {model}_end();\n")
        f.write("}\n\n")
    
        # ISR del Timer0
        f.write("__interrupt void cpu_timer0_isr(void)\n")
        f.write("{\n")
        f.write("    CpuTimer0.InterruptCount++;\n")
        f.write("    T += Tsamp;\n")
        f.write(f"    {model}_isr(T);\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n\n")
    
        # Configurazione iniziale
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
        f.write(f"    ConfigCpuTimer(&CpuTimer0, 100, 10000);\n")
        f.write("    CpuTimer0Regs.TCR.all = 0x4000;\n\n")
        f.write("    IER |= M_INT1;\n")
        f.write("    PieCtrlRegs.PIEIER1.bit.INTx7 = 1;\n\n")
        f.write("    EINT;\n")
        f.write("    ERTM;\n")
        f.write("}\n\n")
    
        # Funzioni helper
        f.write("double get_run_time(void)\n")
        f.write("{\n")
        f.write("    return T;\n")
        f.write("}\n\n")
    
        f.write("double get_Tsamp(void)\n")
        f.write("{\n")
        f.write("    return Tsamp;\n")
        f.write("}\n")




    # Name of the file that will be moved (eg example.c)
    source_file = f'{model}.c'
    destination_file = os.path.join(src_dir, f'{model}.c')

    # Check if {model}.c exists in the current directoy
    if os.path.exists(source_file):
        if os.path.exists(destination_file):
            os.remove(destination_file)

        # Move {model}.c file in the src directory
        shutil.move(source_file, src_dir)

    # Call the function to copy files based on content in {model}.c
    #copy_files_based_on_content(functions_name, src_path, include_path, devices_path, src_dir, include_dir)
    find_and_copy_c_files(functions_name,  CodeGen_path, src_dir, include_dir)

    # Copia il file pyblock.h
    pyblock_file = os.path.join(pyblock_path, 'pyblock.h')
    if os.path.exists(pyblock_file):
        shutil.copy(pyblock_file, include_dir)

    # Copia il file matop.h
    #matop_file = os.path.join(pyblock_path, 'matop.h')
    #if os.path.exists(matop_file):
        #shutil.copy(matop_file, include_dir)


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