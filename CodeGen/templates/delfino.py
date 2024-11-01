import os
import sys
import shutil
from numpy import nonzero, ones, asmatrix, size, array, zeros
from os import environ
import json
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox
import tkinter as tk
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog

# Variabile globale per determinare l'ambiente
isInWSL = False

# Configuration file path
config_file = 'config.json'

def ask_installation_environment():
    """Chiede all'utente dove ha installato PySimCoder e salva la scelta."""
    def on_next():
        global isInWSL
        selected_option = environment_var.get()
        if selected_option == "wsl":
            isInWSL = True
        elif selected_option == "linux":
            isInWSL = False
        else:
            messagebox.showerror("Selection Error", "Please select an environment.")
            return
        root.destroy()

    # Crea la finestra Tkinter
    root = tk.Tk()
    root.title("Select Installation Environment")

    # Imposta la dimensione della finestra (larghezza x altezza)
    root.geometry("700x150")  # Puoi modificare i valori "400x200" per ingrandire ulteriormente

    # Disabilita il pulsante "X" per chiudere la finestra
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    # Variabile per memorizzare l'opzione selezionata
    environment_var = tk.StringVar()

    # Creazione dei pulsanti di opzione
    tk.Label(root, text="Where did you install PySimCoder?").pack(pady=10)
    tk.Radiobutton(root, text="On Windows WSL", variable=environment_var, value="wsl").pack(anchor="w", padx=20)
    tk.Radiobutton(root, text="On a Linux environment", variable=environment_var, value="linux").pack(anchor="w", padx=20)

    # Pulsante per proseguire
    tk.Button(root, text="Next", command=on_next).pack(pady=10)

    root.mainloop()

def load_config():
    """Load paths from config.json if it exists"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return json.load(file)
    return {}

def save_config(first_headers_path, second_headers_path, third_headers_path, first_source_path, second_source_path):
    """Save paths to config.json"""
    config = {
        'first_headers_path': first_headers_path,
        'second_headers_path': second_headers_path,
        'third_headers_path': third_headers_path,
        'first_source_path': first_source_path,
        'second_source_path': second_source_path
    }
    with open(config_file, 'w') as file:
        json.dump(config, file)
    messagebox.showinfo("Configuration Saved", "Paths saved successfully!")

def open_config_window():
    """Open tkinter configuration window to set paths"""

    global root  # Make root global for clipboard access
    root = Tk()
    root.title("Configuration")

    # Load current config or set empty strings
    current_config = load_config()
    first_headers_path = StringVar(root, value=current_config.get('first_headers_path', ''))
    second_headers_path = StringVar(root, value=current_config.get('second_headers_path', ''))
    third_headers_path = StringVar(root, value=current_config.get('third_headers_path', ''))
    first_source_path = StringVar(root, value=current_config.get('first_source_path', ''))
    second_source_path = StringVar(root, value=current_config.get('second_source_path', ''))

    # Function to open file dialog and set path in the corresponding entry field
    def select_directory(var):
        if isInWSL:
            # Display a message or handle WSL-specific behavior if needed
            print("You are in WSL. Ensure X server is running for GUI operations.")
        selected_path = filedialog.askdirectory()
        if selected_path:
            var.set(selected_path)

    # Labels, entry fields, and buttons for selecting paths
    Label(root, text="First Headers Path:").grid(row=0, column=0, sticky='e')
    entry_first_headers = Entry(root, textvariable=first_headers_path, width=100)
    entry_first_headers.grid(row=0, column=1, pady=5)
    Button(root, text="Browse", command=lambda: select_directory(first_headers_path)).grid(row=0, column=2)

    Label(root, text="Second Headers Path:").grid(row=1, column=0, sticky='e')
    entry_second_headers = Entry(root, textvariable=second_headers_path, width=100)
    entry_second_headers.grid(row=1, column=1, pady=5)
    Button(root, text="Browse", command=lambda: select_directory(second_headers_path)).grid(row=1, column=2)

    # New third headers path
    Label(root, text="Third Headers Path:").grid(row=2, column=0, sticky='e')
    entry_third_headers = Entry(root, textvariable=third_headers_path, width=100)
    entry_third_headers.grid(row=2, column=1, pady=5)
    Button(root, text="Browse", command=lambda: select_directory(third_headers_path)).grid(row=2, column=2)

    Label(root, text="First Source Path:").grid(row=3, column=0, sticky='e')
    entry_first_source = Entry(root, textvariable=first_source_path, width=100)
    entry_first_source.grid(row=3, column=1, pady=5)
    Button(root, text="Browse", command=lambda: select_directory(first_source_path)).grid(row=3, column=2)

    Label(root, text="Second Source Path:").grid(row=4, column=0, sticky='e')
    entry_second_source = Entry(root, textvariable=second_source_path, width=100)
    entry_second_source.grid(row=4, column=1, pady=5)
    Button(root, text="Browse", command=lambda: select_directory(second_source_path)).grid(row=4, column=2)


    # Save the inputs and close window
    def save_and_close():
        save_config(first_headers_path.get(), second_headers_path.get(),
                    third_headers_path.get(), first_source_path.get(), second_source_path.get())
        root.destroy()
    
    Button(root, text="Save", command=save_and_close).grid(row=5, column=1, pady=10, sticky='e')
    root.mainloop()



def create_cproject_file(model, first_path, second_path, third_path):

    project_dir = f"./{model}_project"
    cproject_file = os.path.join(project_dir, ".cproject")

    # Ottiene il percorso di pysimCoder
    pysimCoder_path = environ.get('PYSUPSICTRL')

    # Rimuovi la parte finale "/PysimCoder"
    base_path = os.path.dirname(pysimCoder_path)

    include_path = os.path.join(base_path, f"{model}_gen", f"{model}_project", "include")
    include_path = include_path.replace("\\", "/")

    #Se su wsl il path sarà simile a qualcosa come:
    #/mnt/c/Users/lucia/Desktop/ciaociao_gen/ciaociao_project/include
    # quindi togliamo /mnt/c e sostituiamo con:
    # C:/Users/lucia/Desktop/ciaociao_gen/ciaociao_project/include
    if include_path.startswith('/mnt/'):
        include_path = include_path.replace('/mnt/c/', 'C:/', 1)

    # Contenuto del file .cproject
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
                                        <listOptionValue builtIn="false" value="{first_path}"/>
                                        <listOptionValue builtIn="false" value="{second_path}"/>
                                        <listOptionValue builtIn="false" value="{third_path}"/>
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
                                        <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd"/>
                                        <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd"/>
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

    # Verifica se la cartella del progetto esiste
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Scrivi il contenuto nel file .cproject
    with open(cproject_file, 'w', encoding='utf-8') as file:
        file.write(cproject_content)



def create_ccsproject_file(model):
    """ Crea il file .ccsproject in formato XML """
    project_dir = f"./{model}_project"
    ccsproject_file = os.path.join(project_dir, ".ccsproject")

    # Costruisci il contenuto del file .ccsproject
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

    # Verifica se la cartella del progetto esiste
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Scrivi il contenuto nel file .ccsproject
    with open(ccsproject_file, 'w', encoding='utf-8') as file:
        file.write(ccsproject_content)
    


def create_project_file(model, first_path, second_path):
    """ Crea il file .project in formato XML """
    project_dir = f"./{model}_project"
    project_file = os.path.join(project_dir, ".project")

    # Costruisci il contenuto del file .project
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
        '            <name>F2837xD_Adc.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_Adc.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_CodeStartBranch.asm</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_CodeStartBranch.asm</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_DefaultISR.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_DefaultISR.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_GlobalVariableDefs.c</name>\n'
        '            <type>1</type>\n'
        #'            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/source/F2837xD_GlobalVariableDefs.c</locationURI>\n'
        f'            <locationURI>file:/{first_path}/F2837xD_GlobalVariableDefs.c</locationURI>\n'                
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_Gpio.c</name>\n'
        '            <type>1</type>\n'
        #'           <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Gpio.c</locationURI>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_Gpio.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_Ipc.c</name>\n'
        '            <type>1</type>\n'
        #'           <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Ipc.c</locationURI>\n'
        f'           <locationURI>file:/{second_path}/F2837xD_Ipc.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_PieCtrl.c</name>\n'
        '            <type>1</type>\n'
        #'            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_PieCtrl.c</locationURI>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_PieCtrl.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_PieVect.c</name>\n'
        '            <type>1</type>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_PieVect.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_SysCtrl.c</name>\n'
        '            <type>1</type>\n'
        #'            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_SysCtrl.c</locationURI>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_SysCtrl.c</locationURI>\n'
        '        </link>\n'
        '        <link>\n'
        '            <name>F2837xD_usDelay.asm</name>\n'
        '            <type>1</type>\n'
        #'            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_usDelay.asm</locationURI>\n'
        f'            <locationURI>file:/{second_path}/F2837xD_usDelay.asm</locationURI>\n'
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

    # Verifica se la cartella del progetto esiste
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Scrivi il contenuto nel file .project
    with open(project_file, 'w', encoding='utf-8') as file:
        file.write(project_content)

    print(f"File {model}.project generato in {project_dir}")




def convert_path_for_wsl(path):
    """Converte un percorso di Windows in un percorso compatibile con WSL."""
    if path and os.name == 'posix' and 'microsoft' in os.uname().release.lower():
        # Converte "C:\\Users\\utente\\percorso" in "/mnt/c/Users/utente/percorso"
        path = path.replace('\\', '/')
        if path[1] == ':':  # Verifica che il percorso sia di tipo C:\...
            drive_letter = path[0].lower()
            path = f"/mnt/{drive_letter}{path[2:]}"
    return path


def check_required_files_in_path(path, required_files):
    """Controlla se tutti i file richiesti sono presenti nel percorso specificato."""
    missing_files = [file for file in required_files if not os.path.isfile(os.path.join(path, file))]
    return missing_files

def convert_path_for_windows(path):
    """Converte un percorso WSL in un percorso compatibile con Windows mantenendo gli slash ('/')."""
    if path.startswith('/mnt/') and os.name == 'posix' and 'microsoft' in os.uname().release.lower():
        # Esempio: "/mnt/c/Users/utente/percorso" diventa "C:/Users/utente/percorso"
        parts = path.split('/')
        drive_letter = parts[2].upper() + ':'  # Ottiene la lettera dell'unità e aggiunge ":"
        windows_path = drive_letter + '/' + '/'.join(parts[3:])
        return windows_path
    return path  # Ritorna il percorso originale se non è un percorso WSL



def create_project_structure(model):
    ask_installation_environment()
    print("Is in WSL:", isInWSL)

    # Load the updated configuration paths
    config = load_config()
    first_headers_path = config.get('first_headers_path', '')
    second_headers_path = config.get('second_headers_path', '')
    third_headers_path = config.get('third_headers_path', '')
    first_source_path = config.get('first_source_path', '')
    second_source_path = config.get('second_source_path', '')

    # Open the configuration window to allow users to update paths as needed
    open_config_window()

    # Ricarica i percorsi aggiornati dopo la chiusura della finestra di configurazione
    config = load_config()
    first_headers_path = config.get('first_headers_path', '')
    second_headers_path = config.get('second_headers_path', '')
    third_headers_path = config.get('third_headers_path', '')
    first_source_path = config.get('first_source_path', '')
    second_source_path = config.get('second_source_path', '')



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

    # Crea le cartelle
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(include_dir, exist_ok=True)
    os.makedirs(targetConfigs_dir, exist_ok=True)

    # Crea il file adc_soc_epwm_cpu01.c

    main_file = os.path.join(src_dir, "adc_soc_epwm_cpu01.c")

    with open(main_file, 'w') as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   adc_soc_epwm_cpu01.c\n")
        f.write("// TITLE:  CPU Timers Example for F2837xD.\n")
        f.write("//###########################################################################\n\n")
    
        # Included Files
        f.write("// Included Files\n")
        f.write('#include "F28x_Project.h"\n')
        f.write('#include "led.h"\n')
        f.write('#include "button.h"\n\n')
    
        # Function Prototypes
        f.write("// Function Prototypes\n")
        f.write("void ConfigureADC(void);\n")
        f.write("void ConfigureEPWM(void);\n")
        f.write("void SetupADCEpwm(Uint16 channel);\n")
        f.write("void setup(void);\n")
        f.write("void loop(void);\n")
        f.write("interrupt void adca1_isr(void);\n\n")
    
        # Defines and Globals
        f.write("// Defines\n")
        f.write("#define RESULTS_BUFFER_SIZE 256\n\n")
        f.write("// Globals\n")
        f.write("Uint16 AdcaResults[RESULTS_BUFFER_SIZE];\n")
        f.write("Uint16 resultsIndex;\n")
        f.write("volatile Uint16 bufferFull;\n")
        f.write("double time;\n\n")
    
        # Main Function
        f.write("void main(void)\n")
        f.write("{\n")
        f.write("    setup();\n")
        f.write("    loop();\n")
        f.write("}\n\n")
    
        # Setup Function
        f.write("void setup(void)\n")
        f.write("{\n")
        f.write("    InitSysCtrl();       // Initialize the CPU\n")
        f.write("    InitGpio();          // Initialize the GPIO\n\n")
        f.write(f"    {model}_init();      // Initialize blocks generated by PySimCoder\n\n")
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
        f.write("    ConfigureADC();\n")
        f.write("    ConfigureEPWM();\n\n")
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
        f.write("}\n\n")
    
        # Loop Function
        f.write("void loop(void)\n")
        f.write("{\n")
        f.write("    //take conversions indefinitely in loop\n")
        f.write("    do\n")
        f.write("    {\n")
        f.write("        //start ePWM\n")
        f.write("        EPwm1Regs.ETSEL.bit.SOCAEN = 1;\n")
        f.write("        EPwm1Regs.TBCTL.bit.CTRMODE = 0;\n\n")
        f.write("        //wait while ePWM causes ADC conversions, which then cause interrupts,\n")
        f.write("        while(!bufferFull);\n")
        f.write("        bufferFull = 0; //clear the buffer full flag\n\n")
        f.write("        //stop ePWM\n")
        f.write("        EPwm1Regs.ETSEL.bit.SOCAEN = 0;  //disable SOCA\n")
        f.write("        EPwm1Regs.TBCTL.bit.CTRMODE = 3; //freeze counter\n\n")
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
    
        # ConfigureEPWM Function
        f.write("// ConfigureEPWM - Configure EPWM SOC and compare values\n")
        f.write("void ConfigureEPWM(void)\n")
        f.write("{\n")
        f.write("    EALLOW;\n")
        f.write("    // Assumes ePWM clock is already enabled\n")
        f.write("    EPwm1Regs.ETSEL.bit.SOCAEN = 0;    // Disable SOC on A group\n")
        f.write("    EPwm1Regs.ETSEL.bit.SOCASEL = 4;   // Select SOC on up-count\n")
        f.write("    EPwm1Regs.ETPS.bit.SOCAPRD = 1;    // Generate pulse on 1st event\n")
        f.write("    EPwm1Regs.CMPA.bit.CMPA = 0x0800;  // Set compare A value to 2048 counts\n")
        f.write("    EPwm1Regs.TBPRD = 0x1000;          // Set period to 4096 counts\n")
        f.write("    EPwm1Regs.TBCTL.bit.CTRMODE = 3;   // freeze counter\n")
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
        f.write("    AdcaRegs.ADCSOC0CTL.bit.TRIGSEL = 5;      //trigger on ePWM1 SOCA/C\n")
        f.write("    AdcaRegs.ADCINTSEL1N2.bit.INT1SEL = 0;    //end of SOC0 will set INT1 flag\n")
        f.write("    AdcaRegs.ADCINTSEL1N2.bit.INT1E = 1;      //enable INT1 flag\n")
        f.write("    AdcaRegs.ADCINTFLGCLR.bit.ADCINT1 = 1;    //make sure INT1 flag is cleared\n")
        f.write("    EDIS;\n")
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
        f.write(f"    {model}_isr(time);\n\n")
        f.write("    PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;\n")
        f.write("}\n")



    # Nome del file che deve essere spostato (ad esempio ciao.c)
    source_file = f'{model}.c'
    destination_file = os.path.join(src_dir, f'{model}.c')

    # Verifica se esiste il file {model}.c nella cartella corrente
    if os.path.exists(source_file):
    # Rimuovi il file di destinazione se esiste già, per consentire lo spostamento senza errori
        if os.path.exists(destination_file):
            os.remove(destination_file)

        # Sposta il file {model}.c nella cartella src
        shutil.move(source_file, src_dir)

        # Verifica se il file {model}.c contiene il nome 'inputGPIOblk.c'
        with open(destination_file, 'r') as file:
            content = file.read()
            if 'inputGPIOblk' in content:
                # Copia il file button.c dalla cartella src alla cartella di destinazione
                button_file = os.path.join(src_path, 'button.c')
                if os.path.exists(button_file):
                    shutil.copy(button_file, src_dir)
                    print("button.c copiato con successo.")

                # Copia il file button.h dalla cartella headers alla cartella headers di destinazione
                button_header_file = os.path.join(include_path, 'button.h')  
                if os.path.exists(button_header_file):
                    shutil.copy(button_header_file, include_dir)  
                    print("button.h copiato con successo.")
                    
                inputGPIOblk_file = os.path.join(devices_path, 'inputGPIOblk.c')
                if os.path.exists(inputGPIOblk_file):
                    shutil.copy(inputGPIOblk_file, src_dir)
            else:
                print("inputGPIOblk non presente in {model}.c.")

            if 'outputGPIOblk' in content:
                # Copia il file button.c dalla cartella src alla cartella di destinazione
                led_file = os.path.join(src_path, 'led.c')
                if os.path.exists(led_file):
                    shutil.copy(led_file, src_dir)

                    # Copia il file button.h dalla cartella headers alla cartella headers di destinazione
                led_header_file = os.path.join(include_path, 'led.h')  
                if os.path.exists(led_header_file):
                    shutil.copy(led_header_file, include_dir)  
                    
                outputGPIOblk_file = os.path.join(devices_path, 'outputGPIOblk.c')
                if os.path.exists(outputGPIOblk_file):
                    shutil.copy(outputGPIOblk_file, src_dir)

            else:
                print("outputGPIOblk non presente in {model}.c.")

    # Copia i file dalla directory include nel percorso include_path alla directory include del progetto
    #if os.path.exists(include_path):
        #for file_name in os.listdir(include_path):
            #full_file_name = os.path.join(include_path, file_name)
            #if os.path.isfile(full_file_name):
                #shutil.copy(full_file_name, include_dir)



     # Copia i file dalla directory src nel percorso src_path alla directory src del progetto
    #if os.path.exists(src_path):
        #for file_name in os.listdir(src_path):
            #full_file_name = os.path.join(src_path, file_name)
            #if os.path.isfile(full_file_name):
                #shutil.copy(full_file_name, src_dir)

    # Copia il file pyblock.h nella directory include del progetto
    pyblock_file = os.path.join(pyblock_path, 'pyblock.h')
    if os.path.exists(pyblock_file):
        shutil.copy(pyblock_file, include_dir)

    # Copia i file nella directory devices
    #if os.path.exists(devices_path):
        #for file_name in os.listdir(devices_path):
            #full_file_name = os.path.join(devices_path, file_name)
            #if os.path.isfile(full_file_name):
                #shutil.copy(full_file_name, src_dir)
        
    # copia contenuto directory targetConfigs
    if os.path.exists(targetConfigs_path):
        for file_name in os.listdir(targetConfigs_path):
            full_file_name = os.path.join(targetConfigs_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, targetConfigs_dir)

    print("First Headers Path:", first_headers_path)
    print("Second Headers Path:", second_headers_path)
    print("Third Headers Path", third_headers_path)
    print("First Source Path:", first_source_path)
    print("Second Source Path:", second_source_path)



    if isInWSL:
        if first_source_path.startswith("C:\\") or first_source_path.startswith("c:\\"):
            first_source_path = convert_path_for_wsl(first_source_path)
        if second_source_path.startswith("C:\\") or second_source_path.startswith("c:\\"):
            second_source_path = convert_path_for_wsl(second_source_path)
    
        print("First Source Path wsl:", first_source_path)
        print("Second Source Path wsl:", second_source_path)


    while True:
        # Verifica se uno dei percorsi contiene il file specifico
        file_name = 'F2837xD_GlobalVariableDefs.c'
        file_in_first = os.path.isfile(os.path.join(first_source_path, file_name))
        file_in_second = os.path.isfile(os.path.join(second_source_path, file_name))

        if file_in_first:
            print(f"{file_name} trovato in {first_source_path}")
            GlobalVariableDefs_path = first_source_path
            other_path = second_source_path  # L'altro percorso per la verifica dei file
            break  # Esce dal ciclo se il file è trovato
        elif file_in_second:
            print(f"{file_name} trovato in {second_source_path}")
            GlobalVariableDefs_path = second_source_path
            other_path = first_source_path  # L'altro percorso per la verifica dei file
            break  # Esce dal ciclo se il file è trovato
        else:
            # Apri una finestra di avviso se il file non è presente in nessuno dei percorsi
            response = messagebox.askyesno("File not found", f"{file_name} not found in the given source paths. Do you want to change the paths?")
            if response:
                # Riapre la finestra di configurazione per modificare i percorsi
                open_config_window()

                # Ricarica i percorsi aggiornati
                config = load_config()
                first_source_path = config.get('first_source_path', '')
                second_source_path = config.get('second_source_path', '')
            else:
                # Mostra una finestra di avviso e cancella i file nella cartella {model}_project
                messagebox.showinfo("Project Status", "Project not generated. Cleaning up project files...")
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)  # Cancella la cartella {model}_project e tutto il suo contenuto
                return  # Esce dal ciclo se preme no
    
    while True:
        # Controlla se l'altro percorso contiene i file richiesti
        required_files = [
            'F2837xD_Adc.c', 'F2837xD_CodeStartBranch.asm', 'F2837xD_DefaultISR.c',
            'F2837xD_Gpio.c', 'F2837xD_Ipc.c', 'F2837xD_PieCtrl.c', 'F2837xD_PieVect.c',
            'F2837xD_SysCtrl.c', 'F2837xD_usDelay.asm'
        ]
        missing_files = [file for file in required_files if not os.path.isfile(os.path.join(other_path, file))]

        if missing_files:
            missing_files_str = "\n".join(missing_files)
            response = messagebox.askyesno(
                "Missing Files",
                f"The following files are missing in the path '{other_path}':\n{missing_files_str}\nDo you want to change the paths?"
            )
            if response:
                open_config_window()
                # Ricarica i percorsi aggiornati
                config = load_config()
                first_source_path = config.get('first_source_path', '')
                second_source_path = config.get('second_source_path', '')

                # Verifica nuovamente la presenza dei file richiesti nell'altro percorso aggiornato
                missing_files = [file for file in required_files if not os.path.isfile(os.path.join(other_path, file))]
                if not missing_files:
                    # Tutti i file sono stati trovati, esci dal ciclo
                    break
            else:
                # Mostra una finestra di avviso e cancella i file nella cartella {model}_project
                messagebox.showinfo("Project Status", "Project not generated. Cleaning up project files...")
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)  # Cancella la cartella {model}_project e tutto il suo contenuto
                return  # Esce dalla funzione se l'utente preme "No"
        else:
            # Tutti i file sono presenti, esci dal ciclo
            break

    GlobalVariableDefs_path = convert_path_for_windows(GlobalVariableDefs_path)
    other_path = convert_path_for_windows(other_path)
    print(GlobalVariableDefs_path)
    print(other_path)

    if isInWSL:
        # percorso di wsl
        if first_headers_path.startswith("/mnt/c/"):
            #lo convertiamo in un percorso Windows
            first_headers_path = convert_path_for_windows(first_headers_path)
        else: 
            first_headers_path = first_headers_path.replace('\\', '/')
        if second_headers_path.startswith("/mnt/c/"):
            second_headers_path = convert_path_for_windows(second_headers_path)
        else:
            second_headers_path = second_headers_path.replace('\\', '/')
        if third_headers_path.startswith("/mnt/c/"):
            third_headers_path = convert_path_for_windows(third_headers_path)
        else:
            third_headers_path = third_headers_path.replace('\\', '/')


    # Crea funzioni per creare i file .project, .cproject, .ccsproject
    create_ccsproject_file(model)
    create_project_file(model, GlobalVariableDefs_path, other_path)
    create_cproject_file(model, first_headers_path, second_headers_path, third_headers_path)

    # Mostra un messaggio che indica che il progetto è stato creato con successo
    messagebox.showinfo("Project Status", "Project successfully created")

