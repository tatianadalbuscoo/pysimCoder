import os
import sys
import shutil
from numpy import nonzero, ones, asmatrix, size, array, zeros
from os import environ
import json
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, filedialog
import tkinter as tk

"""The following commands are provided:

    - Create a valid project for CCS
        - This script works on linux environment and on wsl.
        - The paths where to find the source files and headers needed by the CCS project (not the blocks) are configurable.
            - If it does not find the src files in the paths entered, which CCS uses, the project is not created and everything is cleaned.
            - Paths can be entered for both windows and wsl (Selectable from the browser button where to insert the path) eg:
                - C:\ti\c2000\C2000Ware_4_01_00_00\device_support\f2837xd\headers\source
                - /mnt/c/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/source
        - Save these paths to a .json file for future runs
        - Organize all files in a hierarchy and create .project .cproject and .ccsproject files with user-entered paths.
        - Generates the main file (adc_soc_epwm_cpu01.c) that calls the functions that PysimCoder creates, changing their name.
        - Include only files that use blocks in your project e.g.:
            - If {model}.c contains the word inputGPIOblk includes: inputGPIOblk.c, button.c and button.h
        
"""

# Tells if we are on wsl or a linux environment
isInWSL = False

# File name where to save the paths
config_file = 'config.json'

# Main window in Tkinter
root = None

def ask_installation_environment():
    
    """Asks the user where PySimCoder is installed and saves the choice.

    This function creates a Tkinter GUI window to prompt the user to select 
    the environment where PySimCoder is installed (either Windows WSL or Linux).
    The user's choice is stored in a global variable `isInWSL`.

    Call:
    -----
    ask_installation_environment()

    Functionality:
    --------------
    - Opens a GUI window with radio buttons for environment selection.
    - Prevents window closure using the "X" button.
    - Stores the user's selection in a global variable `isInWSL`.
    - Closes the window after a valid selection is made, or shows an error if no selection is provided.

    Raises:
    -------
    - Displays an error message if the user does not make a selection.

    """

    def on_next():
        
        global isInWSL

        # Save the user's choice: wsl or linux
        selected_option = environment_var.get()
        if selected_option == "wsl":
            isInWSL = True
        elif selected_option == "linux":
            isInWSL = False
        else:
            messagebox.showerror("Selection Error", "Please select an environment.")
            return

        # Close the application
        root.destroy()

    global root

    # Create window la Tkinter
    root = tk.Tk()
    root.title("Select Installation Environment")
    root.geometry("700x150")


    # Disable the "X" button to close the window
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    # Variable to store the selected option
    environment_var = tk.StringVar()

    tk.Label(root, text="Where did you install PySimCoder?").pack(pady=10)
    tk.Radiobutton(root, text="On Windows WSL", variable=environment_var, value="wsl").pack(anchor="w", padx=20)
    tk.Radiobutton(root, text="On a Linux environment", variable=environment_var, value="linux").pack(anchor="w", padx=20)
    tk.Button(root, text="Next", command=on_next).pack(pady=10)

    # Keeps the application running
    root.mainloop()


def load_config():

    """Loads paths from the config.json file if it exists.

    This function attempts to read and load data from a JSON configuration file
    named `config.json`, which is specified by the global `config_file` variable.
    If the file exists, its contents are parsed and returned as a dictionary.
    If the file does not exist, an empty dictionary is returned.

    Call:
    -----
    config_data = load_config()

    Functionality:
    --------------
    - Checks if the `config.json` file exists in the current working directory.
    - Opens and reads the file if it is found, returning the parsed JSON data.
    - Returns an empty dictionary if the file is not present.

    Returns:
    --------
    dict
        A dictionary containing the parsed configuration data if the file exists.
        An empty dictionary if the file does not exist.

    Raises:
    -------
    - May raise `json.JSONDecodeError` if the `config.json` file is not formatted correctly.
    - May raise `OSError` if there are issues reading the file.

    """

    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return json.load(file)
    return {}


def save_config(ti_path, c2000ware_path):

    """Saves the provided paths to a config.json file.

    This function takes multiple file paths as arguments and stores them in a 
    dictionary, which is then serialized and written to a JSON configuration 
    file named `config.json`. After successfully saving the data, a message box 
    is displayed to inform the user.

    Call:
    -----
    save_config(second_headers_path, third_headers_path, first_source_path, second_source_path, c2000ware_path)

    Parameters:
    -----------
    first_headers_path : Path to the first header files.
    second_headers_path : Path to the second header files.
    third_headers_path : Path to the third header files.
    first_source_path : Path to the first source files.
    second_source_path : Path to the second source files.
    c2000ware_path : Path to the C2000Ware installation.

    Functionality:
    --------------
    - Creates a dictionary containing the provided file paths.
    - Writes this dictionary to a `config.json` file in the current directory.
    - Displays a confirmation message box once the data is successfully saved.

    Raises:
    -------
    - May raise `OSError` if there are issues writing to the `config.json` file.

    """

    # Dictionary to save in .json file
    config = {
        'ti_path': ti_path,
        'c2000ware_path': c2000ware_path
    }

    with open(config_file, 'w') as file:
        json.dump(config, file)
    messagebox.showinfo("Configuration Saved", "Paths saved successfully!")


def open_config_window():

    """Opens a Tkinter window for configuration to set and save file paths.

    This function creates a graphical user interface (GUI) using Tkinter that allows
    users to input or select various file paths and save them to a `config.json` file.
    The window provides entry fields for paths and buttons to browse directories.

    Call:
    -----
    open_config_window()

    Functionality:
    --------------
    - Loads current configuration data if `config.json` exists, otherwise sets default empty values.
    - Provides entry fields for:
        - First headers path.
        - Second headers path.
        - Third headers path.
        - First source path.
        - Second source path.
    - Includes "Browse" buttons that open a file dialog to select directories.
    - Saves the updated paths to `config.json` when the "Save" button is clicked.
    - Closes the window after saving the configuration.

    Raises:
    -------
    - `OSError` if there are issues writing to the `config.json` file.

    """

    global root
    root = Tk()
    root.title("Configuration")

    # Load current config or set empty strings
    current_config = load_config()
    ti_path = StringVar(root, value=current_config.get('ti_path', ''))
    c2000ware_path = StringVar(root, value=current_config.get('c2000ware_path', ''))

    # Function to open file dialog and set path in the corresponding entry field
    def select_directory(var):

        # Opens a dialog box that allows the user to select a directory
        selected_path = filedialog.askdirectory()

        if selected_path:
            var.set(selected_path)

    Label(root, text="ti folder path:").grid(row=0, column=0, sticky='e')
    entry_ti = Entry(root, textvariable=ti_path, width=100)
    entry_ti.grid(row=0, column=1, pady=5)
    Button(root, text="Browse", command=lambda: select_directory(ti_path)).grid(row=0, column=2)

    Label(root, text="C2000Ware_4_01_00_00 folder path:").grid(row=1, column=0, sticky='e')
    entry_c2000ware = Entry(root, textvariable=c2000ware_path, width=100)
    entry_c2000ware.grid(row=1, column=1, pady=5)
    Button(root, text="Browse", command=lambda: select_directory(c2000ware_path)).grid(row=1, column=2)

    # Save the inputs and close window
    def save_and_close():
        save_config(ti_path.get(), c2000ware_path.get())

        # Destroys all widgets and terminates the main loop (closes the graphical interface)
        root.destroy()

    # save_and_close() will be called when the user clicks "Save" button.
    Button(root, text="Save", command=save_and_close).grid(row=2, column=1, pady=10, sticky='e')

    # Start the main loop of the Tkinter application
    root.mainloop()


def convert_path_for_wsl(path):

    """Converts a Windows path to a WSL-compatible path.

    This function takes a Windows-style file path and converts it to a format 
    that can be used within WSL. The function 
    checks if the current environment is WSL before performing the conversion.

    Call:
    -----
    new_path = convert_path_for_wsl(path)

    Parameters:
    -----------
    path : The file path in Windows format (e.g., "C:\\Users\\user\\path").

    Functionality:
    --------------
    - Check if path isn't empty, and if the code is running in a WSL environment
    - Converts backslashes (`\\`) in the path to forward slashes (`/`).
    - Checks if the path starts with a drive letter (e.g., "C:").
    - Converts paths like "C:\\Users\\user\\path" to "/mnt/c/Users/user/path", 
      which is the format required by WSL.

    Returns:
    --------
    - The converted WSL-compatible path. If the path is already compatible or the conditions are not met, returns the original path unchanged.

    Example:
    --------
    Input: "C:\\Users\\user\\path"
    Output: "/mnt/c/Users/user/path"

    """

    # Check if path isn't empty, and if the code is running in a WSL environment
    if path and 'microsoft' in os.uname().release.lower():
        path = path.replace('\\', '/')

        # Check if the path is something like C:\...
        if path[1] == ':':
            drive_letter = path[0].lower()
            path = f"/mnt/{drive_letter}{path[2:]}"

    return path


def convert_path_for_windows(path):

    """Converts a WSL path to a Windows-compatible path while maintaining slashes ('/').

    This function takes a path formatted for WSL and converts it to a Windows path format, preserving the use of forward slashes ('/')
    instead of backslashes ('\\'). The function checks if the path is a WSL path and 
    if it is running in a WSL environment before performing the conversion.

    Call:
    -----
    new_path = convert_path_for_windows(path)

    Parameters:
    -----------
    path : The file path in WSL format (e.g., "/mnt/c/Users/user/path").

    Functionality:
    --------------
    - Checks if the path starts with '/mnt/', which is indicative of a WSL path.
    - Extracts the drive letter from the path and converts it to uppercase with a colon (':').
    - Joins the remaining parts of the path to create a Windows path (e.g., "C:/Users/user/path").

    Returns:
    --------
    - The converted Windows-compatible path. If the path is not a WSL path or we aren't in a wsl envoirment the original path is returned.

    Example:
    --------
    Input: "/mnt/c/Users/user/path"
    Output: "C:/Users/user/path"

    """

    # Check if starts with /mnt/, and if the code is running in a WSL environment
    if path.startswith('/mnt/') and 'microsoft' in os.uname().release.lower():
        parts = path.split('/')
        drive_letter = parts[2].upper() + ':'
        windows_path = drive_letter + '/' + '/'.join(parts[3:])
        return windows_path
    return path 


def check_required_files_in_path(path, required_files):

    """Checks if all required files are present in the specified directory.

    This function verifies the existence of specific files in a given directory.
    It takes a list of filenames that are required and checks if each one exists
    in the provided path. If any files are missing, it returns a list of those files.

    Call:
    -----
    missing_files = check_required_files_in_path(path, required_files)

    Parameters:
    -----------
    path : The directory path where the files should be checked.
    required_files : A list of filenames that need to be present in the specified path.

    Functionality:
    --------------
    - Collects files that do not exist in the `missing_files` list.

    Returns:
    --------
    - A list of filenames that are missing from the specified directory. 
    - Returns an empty list if all files are present.

    Example:
    --------
    Input:
        path = "/path/to/directory"
        required_files = ["file1.txt", "file2.txt", "file3.txt"]

    Output:
        If "file2.txt" does not exist, returns ["file2.txt"].
        If all files exist, returns [].

    """
  
    missing_files = [file for file in required_files if not os.path.isfile(os.path.join(path, file))]
    return missing_files


def create_ccsproject_file(model):

    """Creates a .ccsproject file in XML format for a given project.

    This function generates a `.ccsproject` file within a project-specific directory.
    The file is created in XML format and includes basic project options. The function ensures that the 
    directory exists before writing the file.

    Call:
    -----
    create_ccsproject_file(model)

    Parameters:
    -----------
    model : The name of the project for which the `.ccsproject` file is being created.

    Functionality:
    --------------
    - Writes the XML content into a `.ccsproject` file in the specified directory.

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


def create_project_file(model, c2000ware_path):

    """Creates a .project file in XML format for a given project.

    This function generates a `.project` file in a project-specific directory.
    The file is formatted as XML and includes project settings.

    Call:
    -----
    create_project_file(model, first_path, second_path)

    Parameters:
    -----------
    model : The name of the project for which the `.project` file is being created.
    first_path : The path used for certain linked resources.
    second_path : The path used for other linked resources.

    Functionality:
    --------------
    - Writes the XML content into a `.project` file in the specified directory.

    Example:
    --------
    Input:
        model = "exampleModel"
        first_path = "/path/to/first"
        second_path = "/path/to/second"

    Output:
        Creates a file `./exampleModel_project/.project` with the specified XML content.

    """
    first_path = c2000ware_path + '/device_support/f2837xd/headers/source'
    second_path = c2000ware_path + '/device_support/f2837xd/common/source'

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

    """Creates a .cproject file in XML format for a given project.

    This function generates a `.cproject` file in a project-specific directory.
    The file is created in XML format and includes detailed configuration settings. 

    Call:
    -----
    create_cproject_file(model, first_path, second_path, third_path)

    Parameters:
    -----------
    model : The name of the project for which the `.cproject` file is being created.
    first_path : The first include path to be added to the project configuration.
    second_path : The second include path to be added to the project configuration.
    third_path : The third include path to be added to the project configuration.
    include: The include directory of the project

    Functionality:
    --------------
    - Writes the XML content to the `.cproject` file in the specified directory.

    Example:
    --------
    Input:
        model = "exampleModel"
        first_path = "/path/to/first/include"
        second_path = "/path/to/second/include"
        third_path = "/path/to/third/include"

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
    
    if isInWSL:
        include_path = convert_path_for_windows(include_path)

    # Build content of .cproject file
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


def copy_files_based_on_content(destination_file, src_path, include_path, devices_path, src_dir, include_dir):

    """
    Checks if the content of a given file contains specific keywords and copies 
    associated files to their respective destination directories.

    Parameters:
    -----------
    destination_file : The path of the file to be read and analyzed for specific keywords.
    src_path : The path to the source directory containing the .c files.
    include_path : The path to the source directory containing the .h files.
    devices_path : The path to the directory containing device-related source files.
    src_dir : The destination directory where .c files should be copied.
    include_dir : The destination directory where .h files should be copied.

    Functionality:
    --------------
    - Reads the content of `destination_file` to check for the presence of the keywords 
      'inputGPIOblk' and 'outputGPIOblk'.
    - If 'inputGPIOblk' is found, copies 'button.c', 'button.h', and 'inputGPIOblk.c' 
      to their respective destination directories if they exist.
    - If 'outputGPIOblk' is found, copies 'led.c', 'led.h', and 'outputGPIOblk.c' 
      to their respective destination directories if they exist.

    Example:
    --------
    If `destination_file` contains the keyword 'inputGPIOblk', the function will:
    - Check if 'button.c', 'button.h', and 'inputGPIOblk.c' exist in their respective paths.
    - Copy the existing files to `src_dir` and `include_dir` as appropriate.

    Raises:
    -------
    - Prints an error message if `destination_file` is not found or if an I/O error occurs.
    """
    try:
        with open(destination_file, 'r') as file:
            content = file.read()

            if 'inputGPIOblk' in content:
                copy_file_if_exists(os.path.join(src_path, 'button.c'), src_dir, 'button.c')
                copy_file_if_exists(os.path.join(include_path, 'button.h'), include_dir, 'button.h')
                copy_file_if_exists(os.path.join(devices_path, 'inputGPIOblk.c'), src_dir, 'inputGPIOblk.c')

            if 'outputGPIOblk' in content:
                copy_file_if_exists(os.path.join(src_path, 'led.c'), src_dir, 'led.c')
                copy_file_if_exists(os.path.join(include_path, 'led.h'), include_dir, 'led.h')
                copy_file_if_exists(os.path.join(devices_path, 'outputGPIOblk.c'), src_dir, 'outputGPIOblk.c')

    except FileNotFoundError:
        print(f"The file {destination_file} isn't found'")
    except IOError as e:
        print(f"I/O Error {e}")


def copy_file_if_exists(src_file, dest_dir, file_name):
    """
    Copies a file to the destination directory if it exists.

    Parameters:
    -----------
    src_file : The path to the source file that needs to be copied.
    dest_dir : The path to the destination directory where the file should be copied.
    file_name : The name of the file used in confirmation or error messages.

    Functionality:
    --------------
    - If the file exists, it copies the file to `dest_dir` using `shutil.copy()`.

    """

    if os.path.exists(src_file):
        shutil.copy(src_file, dest_dir)


def create_project_structure(model):

    """
    Main function to create a complete project structure for a specified model.

    This function orchestrates the entire process of setting up the project directory, 
    creating necessary subdirectories, generating source files, copying required files, 
    and configuring project-specific settings. It also interacts with the user to handle 
    cases where files or paths are missing, ensuring that the project can be generated 
    successfully or informing the user if the process is aborted.

    Functionality:
    --------------
    - Asks the user for the installation environment and loads configuration paths.
    - Creates project directories (e.g., `src`, `include`, `targetConfigs`).
    - Generates the main source file (`adc_soc_epwm_cpu01.c`) with necessary code.
    - Checks for the presence of specific source files and copies them if found.
    - Handles path conversions for WSL.
    - Ensures required files are present in the configured paths; prompts the user to 
      update paths if necessary.
    - Calls helper functions to create `.project`, `.cproject`, and `.ccsproject` 
      configuration files.
    - Displays a final message confirming the successful creation of the project.

    Parameters:
    -----------
    model : The name of the project for which the project structure is being created.

    """

    ask_installation_environment()
    open_config_window()

    # It makes sure that the data being worked on has been freshly modified by the user.
    config = load_config()
    ti_path = config.get('ti_path', '')
    c2000ware_path = config.get('c2000ware_path', '')

    pysimCoder_path = environ.get('PYSUPSICTRL')
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
       f.write("//###########################################################################\n")
       f.write("// Abilita solo il timer 0\n\n")
        
       f.write("// Included Files\n")
       f.write('#include "F28x_Project.h"\n')

       f.write("// Function Prototypes\n")
       f.write('__interrupt void cpu_timer0_isr(void);\n')
       f.write('void setup(void);\n\n')

       f.write("double time;\n\n")

       f.write("void main(void)\n")
       f.write("{\n")
       f.write("    setup();\n")
       f.write("    while(1) {}\n")
       f.write(f"    {model}_end();  // Condizione per finire\n")
       f.write("}\n\n")

       f.write("__interrupt void cpu_timer0_isr(void)\n")
       f.write("{\n")
       f.write("    CpuTimer0.InterruptCount++;\n")
       f.write(f"    {model}_isr(time);\n")
       f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
       f.write("}\n\n")

       f.write("void setup(void)\n")
       f.write("{\n")
       f.write("    InitSysCtrl();\n")
       f.write("    InitGpio();\n")
       f.write(f"    {model}_init();  // Inizializza i blocchi generati da PySimCoder\n\n")

       f.write("    DINT;\n")
       f.write("    InitPieCtrl();\n")
       f.write("    IER = 0x0000;\n")
       f.write("    IFR = 0x0000;\n")
       f.write("    InitPieVectTable();\n\n")

       f.write("    EALLOW;\n")
       f.write("    PieVectTable.TIMER0_INT = &cpu_timer0_isr;\n")
       f.write("    EDIS;\n\n")

       f.write("    InitCpuTimers();\n")
       f.write("    ConfigCpuTimer(&CpuTimer0, 200, 100000);\n")
       f.write("    CpuTimer0Regs.TCR.all = 0x4000;\n\n")

       f.write("    IER |= M_INT1;\n")
       f.write("    PieCtrlRegs.PIEIER1.bit.INTx7 = 1;\n\n")

       f.write("    EINT;\n")
       f.write("    ERTM;\n")
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

    #Call the function to copy files based on content in {model}.c
    copy_files_based_on_content(destination_file, src_path, include_path, devices_path, src_dir, include_dir)

    # Copy the pyblock.h file into the project's include directory
    pyblock_file = os.path.join(pyblock_path, 'pyblock.h')
    if os.path.exists(pyblock_file):
        shutil.copy(pyblock_file, include_dir)

    # Copy contents of targetConfigs directory
    if os.path.exists(targetConfigs_path):
        for file_name in os.listdir(targetConfigs_path):
            full_file_name = os.path.join(targetConfigs_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, targetConfigs_dir)

    #if isInWSL:
        
        # Path windows insert, eg: C:\ti\c2000\C2000Ware_4_01_00_00\device_support\f2837xd\headers\include
        # convert in wsl path because must search for src files.
        #if first_source_path.startswith("C:\\") or first_source_path.startswith("c:\\"):
            #first_source_path = convert_path_for_wsl(first_source_path)
        #if second_source_path.startswith("C:\\") or second_source_path.startswith("c:\\"):
            #second_source_path = convert_path_for_wsl(second_source_path)

    #while True:

        # Check if one of the paths contains the specific file
        #file_name = 'F2837xD_GlobalVariableDefs.c'
        #file_in_first = os.path.isfile(os.path.join(first_source_path, file_name))
        #file_in_second = os.path.isfile(os.path.join(second_source_path, file_name))

        #if file_in_first:
            #GlobalVariableDefs_path = first_source_path
            #other_path = second_source_path
            #break  
        #elif file_in_second:
            #GlobalVariableDefs_path = second_source_path
            #other_path = first_source_path
            #break
        #else:
            # Warning dialog if file is not present in any of the paths.
            #response = messagebox.askyesno("File not found", f"{file_name} not found in the given source paths. Do you want to change the paths?")
            #if response:

                # Reopens the configuration window to edit the paths.
                #open_config_window()
                #config = load_config()
                #first_source_path = config.get('first_source_path', '')
                #second_source_path = config.get('second_source_path', '')

                #if isInWSL:
                    #first_source_path = convert_path_for_wsl(first_source_path)
                    #second_source_path = convert_path_for_wsl(second_source_path)
            #else:

                # Show a warning dialog and delete files in the {model}_project folder.
                #messagebox.showinfo("Project Status", "Project not generated. Cleaning up project files...")
                #if os.path.exists(project_dir):
                    #shutil.rmtree(project_dir)  
                #return 
    
    #while True:

        # Check if the other path contains the required files
        #required_files = [
        #    'F2837xD_Adc.c', 'F2837xD_CodeStartBranch.asm', 'F2837xD_DefaultISR.c',
        #   'F2837xD_Gpio.c', 'F2837xD_Ipc.c', 'F2837xD_PieCtrl.c', 'F2837xD_PieVect.c',
        #   'F2837xD_SysCtrl.c', 'F2837xD_usDelay.asm'
        #]
        #missing_files = [file for file in required_files if not os.path.isfile(os.path.join(other_path, file))]

        #if missing_files:
            #missing_files_str = "\n".join(missing_files)
            #response = messagebox.askyesno(
                #"Missing Files",
                #f"The following files are missing in the path '{other_path}':\n{missing_files_str}\nDo you want to change the paths?"
            #)
            #if response:
                #open_config_window()
                #config = load_config()
              
                #first_source_path = config.get('first_source_path', '')
                #second_source_path = config.get('second_source_path', '')

                #if isInWSL:
                    #first_source_path = convert_path_for_wsl(first_source_path)
                    #second_source_path = convert_path_for_wsl(second_source_path)

                #if GlobalVariableDefs_path == first_source_path:
                    #other_path = second_source_path
                #else:
                    #other_path = first_source_path

                # Check again for the presence of the required files in the other updated path
                #missing_files = [file for file in required_files if not os.path.isfile(os.path.join(other_path, file))]
                #if not missing_files:
                    #break
            #else:

                # Show a warning dialog and delete files in the {model}_project folder
                #messagebox.showinfo("Project Status", "Project not generated. Cleaning up project files...")
                #if os.path.exists(project_dir):
                    #shutil.rmtree(project_dir)
                #return  # Exit the function if the user presses "No"
        #else:

            # All files are present, exit the loop
            #break
    
    # Convert paths for windows
    #GlobalVariableDefs_path = convert_path_for_windows(GlobalVariableDefs_path)
    #other_path = convert_path_for_windows(other_path)

    if isInWSL:

        if ti_path.startswith("/mnt/c/"):
            ti_path = convert_path_for_windows(ti_path)
        else: 
            ti_path = ti_path.replace('\\', '/')
        # wsl path
        if c2000ware_path.startswith("/mnt/c/"):
            # Convert in a windows path
            c2000ware_path = convert_path_for_windows(c2000ware_path)
        else:
            c2000ware_path = c2000ware_path.replace('\\', '/')

    # Absolute path include directory
    include_dir_absolute_path = os.path.abspath(include_dir)

    # create the .project, .cproject, .ccsproject files
    create_ccsproject_file(model)
    create_project_file(model, c2000ware_path)
    create_cproject_file(model, ti_path, c2000ware_path, include_dir_absolute_path)

    # Displays a message indicating that the project was created successfully
    messagebox.showinfo("Project Status", "Project successfully created")


