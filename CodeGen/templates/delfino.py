import os
import sys
import shutil
from numpy import nonzero, ones, asmatrix, size, array, zeros
from os import environ

def create_cproject_file(model):

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
                                        <listOptionValue builtIn="false" value="${{CG_TOOL_ROOT}}/include"/>
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
                                        <listOptionValue builtIn="false" value="${{CG_TOOL_ROOT}}/include"/>
                                        <listOptionValue builtIn="false" value="{include_path}"/>
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
    


def create_project_file(model):
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



def create_project_structure(model):

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

    # Crea il file cpu_timers_cpu01.c
    main_file = os.path.join(src_dir, "cpu_timers_cpu01.c")
    with open(main_file, 'w') as f:
        f.write("//###########################################################################\n")
        f.write("// FILE:   cpu_timers_cpu01.c\n")
        f.write("// TITLE:  CPU Timers Example for F2837xD.\n")
        f.write("//###########################################################################\n")
        f.write("// Abilita solo il timer 0\n\n")
        
        f.write("// Included Files\n")
        f.write('#include "F28x_Project.h"\n')
        f.write('#include "led.h"\n')
        f.write('#include "button.h"\n\n')

        f.write("// Function Prototypes\n")
        f.write('__interrupt void cpu_timer0_isr(void);\n')
        f.write('void setup(void);\n\n')

        f.write("double time;\n\n")

        f.write("void main(void)\n")
        f.write("{\n")
        f.write(f"    {model}_init();  // Inizializza i blocchi generati da PySimCoder\n")
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
        f.write("    Button_Init();\n")
        f.write("    LED_Init();\n")
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

    # Nome del file che deve essere spostato (ad esempio ciao.c)
    source_file = f'{model}.c'

    # Verifica se esiste il file {model}.c nella cartella corrente
    if os.path.exists(source_file):
        # Sposta il file {model}.c nella cartella src
        shutil.move(source_file, src_dir)

    # Copia i file dalla directory include nel percorso include_path alla directory include del progetto
    if os.path.exists(include_path):
        for file_name in os.listdir(include_path):
            full_file_name = os.path.join(include_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, include_dir)


     # Copia i file dalla directory src nel percorso src_path alla directory src del progetto
    if os.path.exists(src_path):
        for file_name in os.listdir(src_path):
            full_file_name = os.path.join(src_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, src_dir)

    # Copia il file pyblock.h nella directory include del progetto
    pyblock_file = os.path.join(pyblock_path, 'pyblock.h')
    if os.path.exists(pyblock_file):
        shutil.copy(pyblock_file, include_dir)

    # Copia i file nella directory devices
    if os.path.exists(devices_path):
        for file_name in os.listdir(devices_path):
            full_file_name = os.path.join(devices_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, src_dir)
        
    # copia contenuto directory targetConfigs
    if os.path.exists(targetConfigs_path):
        for file_name in os.listdir(targetConfigs_path):
            full_file_name = os.path.join(targetConfigs_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, targetConfigs_dir)

    # Crea funzioni per creare i file .project, .cproject, .ccsproject
    create_ccsproject_file(model)
    create_project_file(model)
    create_cproject_file(model)
