import os
import sys
import shutil
from numpy import nonzero, ones, asmatrix, size, array, zeros
import json
import tkinter as tk
from tkinter import messagebox, filedialog

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

# File name where to save the paths
config_file = 'config.json'

# Main window in Tkinter
root = None


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


def load_config():

    """ Loads paths from the config.json file if it exists.
    
    This function attempts to read and load data from a JSON configuration file
    named `config.json`, which is specified by the global `config_file` variable.
    If the file exists, its contents are parsed and returned as a dictionary.
    If the file does not exist, an empty dictionary is returned.

    Example Call:
    -------------
    config_data = load_config()
    
    Parameters
    ----------
    -

    Returns:
    --------
    dict
    - A dictionary containing the parsed configuration data if the file exists.
    - An empty dictionary if the file does not exist.

    """

    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return json.load(file)
    return {}


def save_config(ti_path, c2000Ware_path):
    
    """ Saves paths to the `config.json` file.

    This function saves the specified paths to a JSON configuration file named `config.json`.
    It writes the provided paths to the file, creating or overwriting the file if it already exists.
    A message box is displayed to inform the user that the paths have been saved successfully.

    Example Call:
    -------------
    save_config(ti_path="path/to/ti", c2000Ware_path="path/to/c2000ware")

    Parameters:
    -----------
    ti_path        : The path for TI folder.
    c2000Ware_path : The path for C2000Ware folder.

    Returns:
    --------
    -

    """
    
    # Dictionary to save in .json file
    config = {
        'ti_path': ti_path,
        'c2000Ware_path': c2000Ware_path
    }

    with open(config_file, 'w') as file:
        json.dump(config, file)
    messagebox.showinfo("Configuration Saved", "Paths saved successfully!")


def delete_config_file():
    
    """ Deletes the configuration file if it exists.

    This function checks if the configuration file exists in the
    current directory. If found, it deletes the file and shows a confirmation 
    message to the user.

    Example Call:
    -------------
    delete_config_file()

    Parameters:
    -----------
    -

    Returns:
    --------
    -

    """

    if os.path.isfile(config_file):
            os.remove(config_file)
            messagebox.showinfo("Configuration", f"{config_file} has been deleted.")


def open_config_window():

    """ Opens a Tkinter window for configuration to set and save file paths.

    This function creates a graphical user interface (GUI) using Tkinter that allows
    users to input or select various file paths and save them to a `config.json` file.
    The window provides entry fields for paths and buttons to browse directories.

    Example Call:
    -------------
    open_config_window()

    Parameters
    ----------
    -

    Returns
    -------
    -

    """

    global root
    root = tk.Tk()
    root.title("Configuration")

    # Load current config or set empty strings
    current_config = load_config()
    ti_path = tk.StringVar(root, value=current_config.get('ti_path', ''))
    c2000_path = tk.StringVar(root, value=current_config.get('c2000Ware_path', ''))

    root.protocol("WM_DELETE_WINDOW", lambda: None)

    # Function to open file dialog and set path in the corresponding entry field
    def select_directory(var):

        # Opens a dialog box that allows the user to select a directory
        selected_path = filedialog.askdirectory()

        if selected_path:
            var.set(selected_path)

    tk.Label(root, text="ti folder path:").grid(row=0, column=0, sticky='e')
    entry_ti = tk.Entry(root, textvariable=ti_path, width=100)
    entry_ti.grid(row=0, column=1, pady=5)
    tk.Button(root, text="Browse", command=lambda: select_directory(ti_path)).grid(row=0, column=2)

    tk.Label(root, text="C2000Ware_4_01_00_00 folder path:").grid(row=1, column=0, sticky='e')
    entry_c2000ware = tk.Entry(root, textvariable=c2000_path, width=100)
    entry_c2000ware.grid(row=1, column=1, pady=5)
    tk.Button(root, text="Browse", command=lambda: select_directory(c2000_path)).grid(row=1, column=2)

    # Save the inputs and close window
    def save_and_close():
        save_config(ti_path.get(), c2000_path.get())

        # Stop the mainloop without closing the window.
        root.quit()

    tk.Button(root, text="Save", command=save_and_close).grid(row=2, column=1, pady=10, sticky='e')

    # Start the main loop of the Tkinter application
    root.mainloop()

    # Close the main window
    root.destroy()


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


def copy_files_based_on_content(file_to_inspection, src_path, include_path, devices_path, src_dir, include_dir):
    
    """ Copies specific files based on the content of a file to inspection.

    This function reads the contents of a specified `file_to_inspection` and checks for 
    the presence of specific keywords ('inputGPIOblk' and 'outputGPIOblk'). If a keyword 
    is found, it copies corresponding files from various source paths to destination directories.

    Example Call:
    -------------
    copy_files_based_on_content(file_to_inspection="path/to/destination", src_path="src/path", 
                                include_path="include/path", devices_path="devices/path", 
                                src_dir="src/dir", include_dir="include/dir")

    Parameters:
    -----------
    file_to_inspection : The file to read and inspect for specific keywords.
    src_path           : The directory containing `.c` files.
    include_path       : The directory containing `.h` files.
    devices_path       : The directory containing the functions associated with the blocks (e.g. inputGPIOblk).
    src_dir            : The destination directory for `.c` files (where they will be copied).
    include_dir        : The destination directory for `.h` files (where they will be copied).

    Returns:
    --------
    -

    """
    
    try:
        with open(file_to_inspection, 'r') as file:
            content = file.read()

            if 'inputGPIOblk' in content:
                copy_file_if_exists(os.path.join(src_path, 'button.c'), src_dir)
                copy_file_if_exists(os.path.join(include_path, 'button.h'), include_dir)
                copy_file_if_exists(os.path.join(devices_path, 'inputGPIOblk.c'), src_dir)

            if 'outputGPIOblk' in content:
                copy_file_if_exists(os.path.join(src_path, 'led.c'), src_dir)
                copy_file_if_exists(os.path.join(include_path, 'led.h'), include_dir)
                copy_file_if_exists(os.path.join(devices_path, 'outputGPIOblk.c'), src_dir)
            
            if 'epwmblk' in content:
                copy_file_if_exists(os.path.join(src_path, 'epwm.c'), src_dir)
                copy_file_if_exists(os.path.join(include_path, 'epwm.h'), include_dir)
                copy_file_if_exists(os.path.join(devices_path, 'epwmblk.c'), src_dir)

            if 'adcblk' in content:
                copy_file_if_exists(os.path.join(src_path, 'adc.c'), src_dir)
                copy_file_if_exists(os.path.join(include_path, 'adc.h'), include_dir)
                copy_file_if_exists(os.path.join(devices_path, 'adcblk.c'), src_dir)

    except FileNotFoundError:
        print(f"The file {file_to_inspection} isn't found'")
    except IOError as e:
        print(f"I/O Error {e}")


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

    """ Displays a modal window with a message and Yes/No buttons for user response.

    This function creates a pop-up window with a specified title and message, 
    allowing the user to respond by selecting either "Yes" or "No." The window 
    includes scrollable text to view long messages, and disables the close button 
    to ensure a response is provided.

    Example Call:
    -------------
    user_response = advise("Warning", "Are you sure you want to proceed?")

    Parameters:
    -----------
    title      : The title of the window and header of the message.
    message    : The message text displayed within the window.

    Returns:
    --------
    bool
    - `True` if the user selects "Yes" 
    - `False` if the user selects "No."

    """

    # Initialize the main window
    root = tk.Tk()
    root.title(title)
    root.geometry("650x400")

    response = tk.BooleanVar(value=False)

    # Prevents closing by means of the cross
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    tk.Label(root, text=title, font=("Helvetica", 16, "bold")).pack(pady=10)
    frame = tk.Frame(root)
    frame.pack(pady=10, padx=20, fill="both", expand=True)
    text_box = tk.Text(frame, wrap="none", width=70, height=15)
    text_box.insert("1.0", message)

    # Prevents text editing
    text_box.config(state="disabled")

    # Creating vertical and horizontal scroll bar
    y_scroll = tk.Scrollbar(frame, orient="vertical", command=text_box.yview)
    x_scroll = tk.Scrollbar(frame, orient="horizontal", command=text_box.xview)

    # Configure Text to use scrollbars
    text_box.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    # Place the Text and scrollbars in the frame
    text_box.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # Function to set the response and close the window
    def set_response(value):
        response.set(value)

        # Stop the mainloop without closing the window
        root.quit()

    tk.Button(root, text="Yes", command=lambda: set_response(True)).pack(side="left", padx=20, pady=5, expand=True)
    tk.Button(root, text="No", command=lambda: set_response(False)).pack(side="right", padx=20, pady=5, expand=True)

    # Start the main loop of the Tkinter application
    root.mainloop()

    # Close the main window
    root.destroy()

    return response.get()


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
                f"{missing_paths_str}\n\nDo you want to change paths (Yes) or delete the config.json file (No)"
            )
            if response:
                open_config_window()

                # Reload updated paths from new configuration
                config = load_config()
                ti_path_update = config.get('ti_path', '')
                c2000_path_update = config.get('c2000Ware_path', '')

                if isInWSL:
                    ti_path_update = convert_path_for_wsl(ti_path_update)
                    c2000_path_update = convert_path_for_wsl(c2000_path_update)

                # Update the paths to check with the new values
                paths_to_check = update_paths(ti_path_update, c2000_path_update)
            else:
                delete_config_file()
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
                    f"{missing_message}Do you want to delete the config.json file (Yes) or not (No)"
                )


                if response:
                    delete_config_file()
                    return 
                else:
                    return
            else:
                messagebox.showinfo("Paths and Files Check", "All required paths and files are present.")
                break


def press_configure_button():

    """ Handles the configuration setup process when the configure button is pressed.

    This function initializes the environment check, opens the configuration window, 
    and verifies paths by loading configuration settings. It ensures that WSL is detected 
    if applicable and verifies required paths for `ti_path` and `c2000Ware_path`.

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
    open_config_window()

    config = load_config()
    ti_path = config.get('ti_path', '')
    c2000Ware_path = config.get('c2000Ware_path', '')

    check_paths(ti_path, c2000Ware_path)


def create_project_structure(model):
    
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

    check_wsl_environment()

    # Define paths for config.json in the directory where {model}_gen will be created and inside {model}_gen
    parent_dir = os.path.dirname(os.path.abspath('.'))
    config_path_outside_gen = os.path.join(parent_dir, 'config.json')
    config_path_inside_gen = os.path.join(parent_dir, f'{model}_gen', 'config.json')

    # Check if config.json exists in the parent directory and copy it to {model}_gen, overwriting if needed
    if os.path.isfile(config_path_outside_gen):
        os.makedirs(os.path.join(parent_dir, f'{model}_gen'), exist_ok=True)  # Ensure {model}_gen directory exists
        shutil.copy(config_path_outside_gen, config_path_inside_gen)  # Copy and overwrite if exists
    else:

        # If config.json doesn't exists in the parent folder
        messagebox.showinfo("File Status", f"config.json not found in {parent_dir} .\nYou can set the paths under the menu settings -> settings -> configure")
        return 

    config = load_config()
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

    # Call the function to copy files based on content in {model}.c
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

   
    # Absolute path include directory
    include_dir_absolute_path = os.path.abspath(include_dir)

    if isInWSL:
        include_dir_absolute_path = convert_path_for_windows(include_dir_absolute_path)


    # create the .project, .cproject, .ccsproject files
    create_ccsproject_file(model)
    create_project_file(model, c2000Ware_path)
    create_cproject_file(model, ti_path, c2000Ware_path, include_dir_absolute_path)

    # Displays a message indicating that the project was created successfully
    messagebox.showinfo("Project Status", "Project successfully created")
