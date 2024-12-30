
import os
import sys
import unittest
from unittest.mock import patch, mock_open
from shutil import rmtree
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))
from delfino import create_ccsproject_file, create_project_file, create_cproject_file


"""

Unit Test Suite for Project File Creation Functions

This test suite is designed to verify the functionality and correctness of three core functions:
- `create_ccsproject_file`: Responsible for generating `.ccsproject` files.
- `create_project_file`: Responsible for generating `.project` files.
- `create_cproject_file`: Responsible for generating `.cproject` files.

Mocking:
- The tests heavily rely on unittest.mock to simulate file system operations like os.makedirs and os.path.exists, as well as file input/output through builtins.open.
- For comprehensive validation, real filesystem tests are included to verify end-to-end functionality when mocking is not applied.

   
- Test create_ccsproject_file function

    - test_directory_creation:                                        Verify that the directory is created if it does not exist.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
                                                                      - The `os.makedirs` function is mocked to intercept and verify the directory creation logic.
                                                                      - The `open` function is mocked to ensure the focus remains on directory creation rather than file writing.
    
    - test_directory_creation_real:                                   Verify that the directory is actually created in the filesystem.
                                                                      Simulated Condition: The function is executed in a real filesystem environment without mocking.

    - test_file_written_correctly:                                    Verify that the `.ccsproject` file is written correctly when the directory exists.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `True`, simulating the existence of the directory.
                                                                      - The `os.makedirs` function is mocked to avoid creating the directory in the filesystem.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation.

    - test_combined_directory_and_file_creation:                      Verify that the directory is created and the `.ccsproject` file is written when the directory does not exist.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
                                                                      - The `os.makedirs` function is mocked to ensure the directory creation logic is invoked.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation.

    - test_different_compiler_version:                                Verify that the `.ccsproject` file is written correctly for a different compiler version (ti-cgt-c2000_21.6.0.LTS).

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `True`, simulating that the directory already exists.
                                                                      - The `os.makedirs` function is mocked to ensure it is not invoked since the directory exists.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation with the expected compiler version.

- Test create_project_file function

    - test_directory_creation:                                        Verify that the directory is created if it does not exist.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
                                                                      - The `os.makedirs` function is mocked to ensure that the directory creation logic is invoked.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation for the `.project` file.
    
    - test_directory_creation_real:                                   Verify that the directory is actually created in the filesystem.
                                                                      Simulated Condition: The function is executed in a real filesystem environment without mocking.

    - test_file_written_correctly_wsl:                                Verify that the `.project` file is written correctly when `isInWSL` is True.

                                                                      Simulated Condition:
                                                                      - `os.path.exists` is mocked to return `False`, simulating that the directory does not exist.
                                                                      - `os.makedirs` is mocked to ensure that the directory creation logic is invoked.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation.

    - test_file_written_correctly_linux:                              Verify that the `.project` file is written correctly when `isInWSL` is False.

                                                                      Simulated Condition:
                                                                      - `os.path.exists` is mocked to return `False`, simulating that the directory does not exist.
                                                                      - `os.makedirs` is mocked to ensure that the directory creation logic is invoked.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation.

    - test_combined_directory_and_file_creation:                      Verify that the directory is created and the `.project` file is written when the directory does not exist.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
                                                                      - The `os.makedirs` function is mocked to verify that the directory creation logic is invoked.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation.

- Test create_cproject_file function

    - test_directory_creation:                                        Verify that the directory is created and the `.cproject` file is written when the directory does not exist.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
                                                                      - The `os.makedirs` function is mocked to verify that the directory creation logic is invoked.
                                                                      - The `open` function is mocked to intercept and verify the file-writing operation.

    - test_directory_creation_real:                                   Verify that the directory is actually created in the filesystem.

                                                                      Simulated Condition:
                                                                      - The function is tested without mocking, creating a real directory on the filesystem.
                                                                      - After calling `create_cproject_file`, the directory's existence is verified.
                                                                      - Cleanup logic ensures the directory is removed after the test, regardless of the outcome.
 
    -   test_cproject_file_written_correctly_compiler_22_6_state_4:   Verify that the `.cproject` file is written correctly when the directory exists.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `True`, simulating the directory already exists.
                                                                      - The `os.makedirs` function is mocked to verify it is not invoked since the directory is already present.
                                                                      - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
                                                                      - The written content of the `.cproject` file is compared line by line with the expected content.

    - test_cproject_file_written_correctly_compiler_21_6_0_state_4:   Verify that the `.cproject` file is written correctly for the `21.6.0.LTS` compiler.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `True`, simulating the directory already exists.
                                                                      - The `os.makedirs` function is mocked to verify it is not invoked since the directory is already present.
                                                                      - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
                                                                      - The written content of the `.cproject` file is compared line by line with the expected content for the `21.6.0.LTS` compiler.

    - test_define_created_correctly_for_state_4:                      Verify that the `.cproject` file correctly includes the `STATE` and `NREPWMTRIGGERADC` defines.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `True`, simulating that the directory already exists.
                                                                      - The `os.makedirs` function is mocked to ensure it is not invoked since the directory is already present.
                                                                      - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
                                                                      - The written content of the `.cproject` file is checked to confirm that the `STATE` and `NREPWMTRIGGERADC` defines are correctly generated with the given values.
    
    - test_define_not_present_for_state_1:                            Verify that the `.cproject` file excludes the conditional `NREPWMTRIGGERADC` define.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `True`, simulating that the directory already exists.
                                                                      - The `os.makedirs` function is mocked to ensure it is not invoked since the directory is already present.
                                                                      - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
                                                                      - The written content of the `.cproject` file is checked to confirm that the `STATE` define is correctly generated with the value `1`,
                                                                      and the conditional define `NREPWMTRIGGERADC` is excluded as `main4_nr_epwm_trigger_adc` is `None`.
    
    - test_combined_directory_and_file_creation:                      Verify that the directory is created, and the `.cproject` file is written correctly when the directory does not exist.

                                                                      Simulated Condition:
                                                                      - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
                                                                      - The `os.makedirs` function is mocked to ensure the directory creation logic is invoked.
                                                                      - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
                                                                      - The written content of the `.cproject` file is checked to confirm that the `STATE` define is correctly generated and the
                                                                      conditional define `NREPWMTRIGGERADC` is included as `main4_nr_epwm_trigger_adc` is set to `3`.

"""


#################################################################################################################################################
# Test create_ccsproject_file function 
#################################################################################################################################################

class TestCreateCCSProjectFile(unittest.TestCase):
    

    def setUp(self):

        """

        Setup common variables for the tests.

        This method is run before every individual test in the class. It initializes
        commonly used variables to avoid redundancy and ensure consistency across tests.

        """

        # The name of the test project
        self.test_model = "testModel"

        # The compiler version used for the test
        self.test_compiler = "ti-cgt-c2000_22.6.1.LTS"

        # The expected project directory path
        self.project_dir = f"./{self.test_model}_project"

        # The expected .ccsproject file path
        self.ccsproject_file = os.path.join(self.project_dir, ".ccsproject")


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_directory_creation(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the directory is created if it does not exist.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
        - The `os.makedirs` function is mocked to intercept and verify the directory creation logic.
        - The `open` function is mocked to ensure the focus remains on directory creation rather than file writing.

        """

        create_ccsproject_file(self.test_model, self.test_compiler)

        # Verify that os.path.exists is called with the project directory. Expected: os.path.exists should be called once with the project directory.
        mock_exists.assert_called_once_with(self.project_dir)

        # Verify that os.makedirs is called to create the directory. Expected: os.makedirs should be called once to create the directory.
        mock_makedirs.assert_called_once_with(self.project_dir)

        # Ensure that open is not the focus of this test. Expected: open should be called once with the file path and write mode.
        mock_file.assert_called_once_with(self.ccsproject_file, "w", encoding="utf-8")


    def test_directory_creation_real(self):

        """

        Verify that the directory is actually created in the filesystem.
        Simulated Condition: The function is executed in a real filesystem environment without mocking.

        """

        try:
            create_ccsproject_file(self.test_model, "ti-cgt-c2000_22.6.1.LTS")

            # Verify that the directory exists in the real filesystem. 
            # Expected: The directory `./testModel_project` should be created in the current working directory.
            self.assertTrue(os.path.exists(self.project_dir))

        finally:

            # Cleanup: Remove the directory after the test
            if os.path.exists(self.project_dir):
                rmtree(self.project_dir)


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_file_written_correctly(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the `.ccsproject` file is written correctly when the directory exists.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `True`, simulating the existence of the directory.
        - The `os.makedirs` function is mocked to avoid creating the directory in the filesystem.
        - The `open` function is mocked to intercept and verify the file-writing operation.

        """

        create_ccsproject_file(self.test_model, self.test_compiler)

        # Verify that the open function is called with the correct file path, write mode, and encoding.
        # Expected: open should be called once with the .ccsproject file path.
        mock_file.assert_called_once_with(self.ccsproject_file, "w", encoding="utf-8")

        # Capture the mock file handle to verify the content written to the file
        file_handle = mock_file()

        # Define the expected content of the .ccsproject file
        expected_content = (
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

        # Verify that the content written to the file matches the expected content. 
        # Expected: The `expected_content` string should be written exactly once to the file.
        file_handle.write.assert_called_once_with(expected_content)


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_combined_directory_and_file_creation(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the directory is created and the `.ccsproject` file is written when the directory does not exist.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
        - The `os.makedirs` function is mocked to ensure the directory creation logic is invoked.
        - The `open` function is mocked to intercept and verify the file-writing operation.

        """

        create_ccsproject_file(self.test_model, self.test_compiler)

        # Verify that os.makedirs is called to create the project directory. Expected: The directory should be created.
        mock_makedirs.assert_called_once_with(self.project_dir)

        # Verify that the `.ccsproject` file is opened for writing with the specified path and encoding. Expected: The file should be opened once.
        mock_file.assert_called_once_with(self.ccsproject_file, "w", encoding="utf-8")


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_different_compiler_version(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the `.ccsproject` file is written correctly for a different compiler version (ti-cgt-c2000_21.6.0.LTS).

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `True`, simulating that the directory already exists.
        - The `os.makedirs` function is mocked to ensure it is not invoked since the directory exists.
        - The `open` function is mocked to intercept and verify the file-writing operation with the expected compiler version.

        """

        different_compiler = "ti-cgt-c2000_21.6.0.LTS"
        create_ccsproject_file(self.test_model, different_compiler)

        # Verify that the `.ccsproject` file is opened for writing. Expected: The file should be opened once.
        mock_file.assert_called_once_with(self.ccsproject_file, "w", encoding="utf-8")

        # Capture the file handle to verify its content
        file_handle = mock_file()

        # Define the expected content for the given compiler version
        expected_content = (
            '<?xml version="1.0" encoding="UTF-8" ?>\n'
            '<?ccsproject version="1.0"?>\n'
            '<projectOptions>\n'
            '    <!-- Specifica il tipo di dispositivo che stai usando -->\n'
            '    <deviceVariant value="com.ti.ccstudio.deviceModel.C2000.GenericC28xxDevice"/>\n'
            '    <deviceFamily value="C2000"/>\n'
            '    <codegenToolVersion value="21.6.0.LTS"/>\n'
            '    <!-- Specifica il formato di output (non ELF in questo caso) -->\n'
            '    <isElfFormat value="false"/>\n\n'
            '    <connection value=""/>\n'
            '    <!-- Indica la libreria di runtime standard -->\n'
            '    <rts value="libc.a"/>\n\n'
            '    <templateProperties value="id=com.ti.common.project.core.emptyProjectTemplate,"/>\n'
            '    <isTargetManual value="false"/>\n'
            '</projectOptions>\n'
        )

        # Verify that the content written to the file matches the expected content. Expected: Content should match expected_content.
        file_handle.write.assert_called_once_with(expected_content)


#################################################################################################################################################
# Test create_project_file function
#################################################################################################################################################

class TestCreateProjectFile(unittest.TestCase):


    def setUp(self):

        """

        Setup common variables for the tests.
        This method is run before every individual test in the class. 
        It initializes commonly used variables to avoid redundancy and ensure consistency across tests.

        """

        # Define a test model name
        self.test_model = "untitled"

        # Define the path to the C2000 library
        self.test_c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"

        # Define the expected project directory based on the test model
        self.project_dir = f"./{self.test_model}_project"

        # Define the full path to the expected `.project` file in the project directory
        self.project_file = os.path.join(self.project_dir, ".project")


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_directory_creation(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the directory is created if it does not exist.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
        - The `os.makedirs` function is mocked to ensure that the directory creation logic is invoked.
        - The `open` function is mocked to intercept and verify the file-writing operation for the `.project` file.

        """

        create_project_file(self.test_model, self.test_c2000_path)

        # Verify that os.path.exists is called with the project directory. Expected: os.path.exists should be called once with the project directory.
        mock_exists.assert_called_once_with(self.project_dir)

        # Verify that os.makedirs is called to create the directory. Expected: os.makedirs should be called once to create the directory.
        mock_makedirs.assert_called_once_with(self.project_dir)

        # Ensure that open is not the focus of this test. Expected: open should be called once with the file path and write mode.
        mock_file.assert_called_once_with(self.project_file, "w", encoding="utf-8")


    def test_directory_creation_real(self):

        """

        Verify that the directory is actually created in the filesystem.
        Simulated Condition: The function is executed in a real filesystem environment without mocking.

        """

        try:
            
            create_project_file(self.test_model, self.test_c2000_path)

            # Verify that the directory exists in the real filesystem. 
            # Expected: The directory `./untitled_project` should be created in the current working directory.
            self.assertTrue(os.path.exists(self.project_dir))

        finally:

            # Cleanup: Remove the directory after the test
            if os.path.exists(self.project_dir):
                rmtree(self.project_dir)


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_file_written_correctly_wsl(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the `.project` file is written correctly when `isInWSL` is True.

        Simulated Condition:
        - `os.path.exists` is mocked to return `False`, simulating that the directory does not exist.
        - `os.makedirs` is mocked to ensure that the directory creation logic is invoked.
        - The `open` function is mocked to intercept and verify the file-writing operation.

        """

        # Simulate `isInWSL` being set to True for the function call
        with patch.dict("delfino.__dict__", {"isInWSL": True}):

            model = "untitled"
            c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"

            # Define the expected XML content for the `.project` file
            expected_content = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<projectDescription>\n'
                '    <name>untitled</name>\n'
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
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_CpuTimers.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_Adc.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Adc.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_CodeStartBranch.asm</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_CodeStartBranch.asm</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_DefaultISR.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_DefaultISR.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_GlobalVariableDefs.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/source/F2837xD_GlobalVariableDefs.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_Gpio.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Gpio.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_Ipc.c</name>\n'
                '            <type>1</type>\n'
                '           <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Ipc.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_PieCtrl.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_PieCtrl.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_PieVect.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_PieVect.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_SysCtrl.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_SysCtrl.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_usDelay.asm</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:/C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_usDelay.asm</locationURI>\n'
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


            create_project_file(model, c2000_path)

            # Verify that `os.makedirs` is called with the correct project directory path. Expected: Directory is created.
            mock_makedirs.assert_called_once_with(f"./{model}_project")

            # Verify that the `.project` file is opened for writing in the correct location. Expected: File opened in write mode.
            mock_file.assert_called_once_with(f"./{model}_project/.project", "w", encoding="utf-8")

            # Extract the actual content written to the file
            file_handle = mock_file()
            actual_content = file_handle.write.call_args[0][0]

            # Verify that the written content matches the expected content. Expected: File content matches.
            self.assertEqual(actual_content, expected_content)


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_file_written_correctly_linux(self, mock_file, mock_exists, mock_makedirs):

        """
        
        Verify that the `.project` file is written correctly when `isInWSL` is False.

        Simulated Condition:
        - `os.path.exists` is mocked to return `False`, simulating that the directory does not exist.
        - `os.makedirs` is mocked to ensure that the directory creation logic is invoked.
        - The `open` function is mocked to intercept and verify the file-writing operation.

        """

        # Simulate `isInWSL` being set to False for the function call
        with patch.dict("delfino.__dict__", {"isInWSL": False}):

            model = "untitled"
            c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"

            # Define the expected XML content for the `.project` file
            expected_content = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<projectDescription>\n'
                '    <name>untitled</name>\n'
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
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_CpuTimers.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_Adc.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Adc.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_CodeStartBranch.asm</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_CodeStartBranch.asm</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_DefaultISR.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_DefaultISR.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_GlobalVariableDefs.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/source/F2837xD_GlobalVariableDefs.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_Gpio.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Gpio.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_Ipc.c</name>\n'
                '            <type>1</type>\n'
                '           <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_Ipc.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_PieCtrl.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_PieCtrl.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_PieVect.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_PieVect.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_SysCtrl.c</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_SysCtrl.c</locationURI>\n'
                '        </link>\n'
                '        <link>\n'
                '            <name>F2837xD_usDelay.asm</name>\n'
                '            <type>1</type>\n'
                '            <locationURI>file:C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source/F2837xD_usDelay.asm</locationURI>\n'
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

            create_project_file(model, c2000_path)

            # Verify that `os.makedirs` is called with the correct project directory path. Expected: Directory is created.
            mock_makedirs.assert_called_once_with(f"./{model}_project")

            # Verify that the `.project` file is opened for writing in the correct location. Expected: File opened in write mode.
            mock_file.assert_called_once_with(f"./{model}_project/.project", "w", encoding="utf-8")

            # Extract the actual content written to the file
            file_handle = mock_file()
            actual_content = file_handle.write.call_args[0][0]

            # Verify that the written content matches the expected content. Expected: File content matches.
            self.assertEqual(actual_content, expected_content)


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_combined_directory_and_file_creation(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the directory is created and the `.project` file is written when the directory does not exist.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
        - The `os.makedirs` function is mocked to verify that the directory creation logic is invoked.
        - The `open` function is mocked to intercept and verify the file-writing operation.

        """

        model = "untitled"
        c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"
        project_dir = f"./{model}_project"
        project_file = f"{project_dir}/.project"

        create_project_file(model, c2000_path)

        # Verify that `os.makedirs` is called with the correct directory path. Expected: Directory is created
        mock_makedirs.assert_called_once_with(project_dir)

        # Verify that the `.project` file is opened for writing. Expected: File is opened in write mode
        mock_file.assert_called_once_with(project_file, "w", encoding="utf-8")


#################################################################################################################################################
# Test create_cproject_file function
#################################################################################################################################################

class TestCreateCProjectFile(unittest.TestCase):


    def setUp(self):

        """

        Setup common variables for the tests.
        This method is run before every individual test in the class. 
        It initializes commonly used variables to avoid redundancy and ensure consistency across tests.

        """

        # Define a test model name
        self.test_model = "untitled"

        # Define paths for testing
        self.test_ti_path = "C:/ti"
        self.test_c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"
        self.test_include_path = "C:/Users/user/Desktop/untitled_gen/untitled_project/include"

        # Define project directory and file
        self.project_dir = f"./{self.test_model}_project"
        self.cproject_file = os.path.join(self.project_dir, ".cproject")

        # Other test parameters
        self.state = 4
        self.compiler = "ti-cgt-c2000_22.6.1.LTS"
        self.main4_nr_epwm_trigger_adc = 3


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_directory_creation(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the directory is created and the `.cproject` file is written when the directory does not exist.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
        - The `os.makedirs` function is mocked to verify that the directory creation logic is invoked.
        - The `open` function is mocked to intercept and verify the file-writing operation.

        """

        create_cproject_file(
            self.test_model,
            self.test_ti_path,
            self.test_c2000_path,
            self.test_include_path,
            self.state,
            self.compiler,
            self.main4_nr_epwm_trigger_adc
        )

        # Verify that os.makedirs is called with the correct project directory
        # Expected: The directory should be created because it does not exist
        mock_makedirs.assert_called_once_with(self.project_dir)

        # Verify that the `.cproject` file is opened for writing
        # Expected: The file should be opened in write mode with UTF-8 encoding
        mock_file.assert_called_once_with(self.cproject_file, "w", encoding="utf-8")
   

    def test_directory_creation_real(self):

        """

        Verify that the directory is actually created in the filesystem.

        Simulated Condition:
        - The function is tested without mocking, creating a real directory on the filesystem.
        - After calling `create_cproject_file`, the directory's existence is verified.
        - Cleanup logic ensures the directory is removed after the test, regardless of the outcome.

        """

        try:
            create_cproject_file(
                self.test_model,
                self.test_ti_path,
                self.test_c2000_path,
                self.test_include_path,
                self.state,
                self.compiler,
                self.main4_nr_epwm_trigger_adc
            )

            # Assert that the directory exists. Expected: The directory specified in `self.project_dir` is created.
            self.assertTrue(os.path.exists(self.project_dir))

        finally:

            # Cleanup: Remove the directory after the test
            if os.path.exists(self.project_dir):
                rmtree(self.project_dir)


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_cproject_file_written_correctly_compiler_22_6_state_4(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the `.cproject` file is written correctly when the directory exists.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `True`, simulating the directory already exists.
        - The `os.makedirs` function is mocked to verify it is not invoked since the directory is already present.
        - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
        - The written content of the `.cproject` file is compared line by line with the expected content.

        """

        create_cproject_file(
            self.test_model,
            self.test_ti_path,
            self.test_c2000_path,
            self.test_include_path,
            self.state,
            self.compiler,
            self.main4_nr_epwm_trigger_adc,
        )

        # Verify that os.makedirs is not called because the directory exists
        # Expected: Directory creation (`os.makedirs`) should not be invoked as the directory already exists.
        mock_makedirs.assert_not_called()

        # Verify that the `.cproject` file is opened for writing
        # Expected: The `.cproject` file should be opened in write mode with UTF-8 encoding.
        mock_file.assert_called_once_with(self.cproject_file, "w", encoding="utf-8")

        # Define the expected content of the `.cproject` file
        expected_content = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <?fileVersion 4.0.0?>
            <cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
                <storageModule configRelations="2" moduleId="org.eclipse.cdt.core.settings">
                    <cconfiguration id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750">
                        <storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750" moduleId="org.eclipse.cdt.core.settings" name="CPU1_RAM">
                            <macros>
                                <stringMacro name="INSTALLROOT_F2837XD" type="VALUE_PATH_DIR" value="${PROJECT_ROOT}/../../../../.."/>
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
                            <configuration artifactExtension="out" artifactName="${ProjName}" buildProperties="" cleanCommand="${CG_CLEAN_CMD}" description="RAM Build Configuration w/Debugger Support for CPU1" id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750" name="CPU1_RAM" parent="com.ti.ccstudio.buildDefinitions.C2000.Debug">
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
                                            <listOptionValue builtIn="false" value="PRODUCT_MACRO_IMPORTS={}"/>
                                        </option>
                                        <option id="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION.1659874217" superClass="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION" value="22.6.1.LTS" valueType="string"/>
                                        <targetPlatform id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.targetPlatformDebug.872252835" name="Platform" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.targetPlatformDebug"/>
                                        <builder buildPath="${BuildDirectory}" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.builderDebug.523509514" name="GNU Make.CPU1_RAM" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.exe.builderDebug"/>
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
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/include"/>
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/include"/>
                                                <listOptionValue builtIn="false" value="C:/ti/ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include"/>
                                                <listOptionValue builtIn="false" value="C:/Users/user/Desktop/untitled_gen/untitled_project/include"/>
                                            </option>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEBUGGING_MODEL.2023058995" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEBUGGING_MODEL" value="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEBUGGING_MODEL.SYMDEBUG__DWARF" valueType="enumerated"/>
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEFINE.928837016" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.compilerID.DEFINE" valueType="definedSymbols">
                                                <listOptionValue builtIn="false" value="CPU1"/>
                                                <listOptionValue builtIn="false" value="_LAUNCHXL_F28379D"/>
                                                <listOptionValue builtIn="false" value="STATE=4"/>
                                                <listOptionValue builtIn="false" value="NREPWMTRIGGERADC=3"/>
                                        
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
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.MAP_FILE.150192862" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.MAP_FILE" value="&quot;${ProjName}.map&quot;" valueType="string"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.OUTPUT_FILE.508871516" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.OUTPUT_FILE" value="${ProjName}.out" valueType="string"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.STACK_SIZE.794155856" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.STACK_SIZE" value="0x100" valueType="string"/>
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.LIBRARY.779473277" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.LIBRARY" valueType="libs">
                                                <listOptionValue builtIn="false" value="rts2800_fpu32.lib"/>
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd"/>
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd"/>
                                                <listOptionValue builtIn="false" value="libc.a"/>
                                            </option>
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.SEARCH_PATH.1443810135" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.SEARCH_PATH" valueType="libPaths">
                                                <listOptionValue builtIn="false" value="${CG_TOOL_ROOT}/lib"/>
                                            </option>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.DISPLAY_ERROR_NUMBER.96471687" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.DISPLAY_ERROR_NUMBER" value="true" valueType="boolean"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.XML_LINK_INFO.1957298402" superClass="com.ti.ccstudio.buildDefinitions.C2000_22.6.linkerID.XML_LINK_INFO" value="&quot;${ProjName}_linkInfo.xml&quot;" valueType="string"/>
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

        # Capture the actual content written to the file
        file_handle = mock_file()
        actual_content = file_handle.write.call_args[0][0]

        # Split the actual and expected content into lines for comparison
        actual_lines = actual_content.strip().splitlines()
        expected_lines = expected_content.strip().splitlines()

        # Verify that the number of lines is the same. Expected: Same number of lines in actual and expected content.
        self.assertEqual(len(actual_lines), len(expected_lines), "Number of lines in the content does not match")

        # Remove empty lines from both for a robust comparison
        actual_lines = [line for line in actual_lines if line.strip()]
        expected_lines = [line for line in expected_lines if line.strip()]

        # Compare line by line
        for i, (actual_line, expected_line) in enumerate(zip(actual_lines, expected_lines), start=1):
            with self.subTest(line=i):
                self.assertEqual(actual_line.strip(), expected_line.strip(), f"Mismatch at line {i}")

   
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_cproject_file_written_correctly_compiler_21_6_0_state_4(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the `.cproject` file is written correctly for the `21.6.0.LTS` compiler.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `True`, simulating the directory already exists.
        - The `os.makedirs` function is mocked to verify it is not invoked since the directory is already present.
        - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
        - The written content of the `.cproject` file is compared line by line with the expected content for the `21.6.0.LTS` compiler.

        """

        # Set the compiler to `21.6.0.LTS`
        self.compiler = "ti-cgt-c2000_21.6.0.LTS"

        create_cproject_file(
            self.test_model,
            self.test_ti_path,
            self.test_c2000_path,
            self.test_include_path,
            self.state,
            self.compiler,
            self.main4_nr_epwm_trigger_adc,
        )

        # Verify that `os.makedirs` is not called because the directory exists. Expected: `os.makedirs` is never invoked
        mock_makedirs.assert_not_called()

        # Verify that the `.cproject` file is opened in write mode. Expected: `open` is called once with the correct file path and write mode
        mock_file.assert_called_once_with(self.cproject_file, "w", encoding="utf-8")

        # Capture the actual content written to the file
        file_handle = mock_file()
        actual_content = file_handle.write.call_args[0][0]

        # Define the expected content of the `.cproject` file
        expected_content = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <?fileVersion 4.0.0?>
            <cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
                <storageModule configRelations="2" moduleId="org.eclipse.cdt.core.settings">
                    <cconfiguration id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750">
                        <storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750" moduleId="org.eclipse.cdt.core.settings" name="CPU1_RAM">
                            <macros>
                                <stringMacro name="INSTALLROOT_F2837XD" type="VALUE_PATH_DIR" value="${PROJECT_ROOT}/../../../../.."/>
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
                            <configuration artifactExtension="out" artifactName="${ProjName}" buildProperties="" cleanCommand="${CG_CLEAN_CMD}" description="RAM Build Configuration w/Debugger Support for CPU1" id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750" name="CPU1_RAM" parent="com.ti.ccstudio.buildDefinitions.C2000.Debug">
                                <folderInfo id="com.ti.ccstudio.buildDefinitions.C2000.Debug.2121059750." name="/" resourcePath="">
                                    <toolChain id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.DebugToolchain.1936615022" name="TI Build Tools" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.DebugToolchain" targetTool="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.linkerDebug.1604840405">
                                        <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.core.OPT_TAGS.1614280783" superClass="com.ti.ccstudio.buildDefinitions.core.OPT_TAGS" valueType="stringList">
                                            <listOptionValue builtIn="false" value="DEVICE_CONFIGURATION_ID=com.ti.ccstudio.deviceModel.C2000.GenericC28xxDevice"/>
                                            <listOptionValue builtIn="false" value="DEVICE_CORE_ID="/>
                                            <listOptionValue builtIn="false" value="DEVICE_ENDIANNESS=little"/>
                                            <listOptionValue builtIn="false" value="OUTPUT_FORMAT=COFF"/>
                                            <listOptionValue builtIn="false" value="RUNTIME_SUPPORT_LIBRARY=libc.a"/>
                                            <listOptionValue builtIn="false" value="CCS_MBS_VERSION=6.1.3"/>
                                            <listOptionValue builtIn="false" value="OUTPUT_TYPE=executable"/>
                                            <listOptionValue builtIn="false" value="PRODUCTS="/>
                                            <listOptionValue builtIn="false" value="PRODUCT_MACRO_IMPORTS={}"/>
                                        </option>
                                        <option id="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION.1659874217" superClass="com.ti.ccstudio.buildDefinitions.core.OPT_CODEGEN_VERSION" value="21.6.0.LTS" valueType="string"/>
                                        <targetPlatform id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.targetPlatformDebug.872252835" name="Platform" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.targetPlatformDebug"/>
                                        <builder buildPath="${BuildDirectory}" id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.builderDebug.523509514" name="GNU Make.CPU1_RAM" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.builderDebug"/>
                                        <tool id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.compilerDebug.1225049945" name="C2000 Compiler" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.compilerDebug">
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.SILICON_VERSION.76848770" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.SILICON_VERSION" value="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.SILICON_VERSION.28" valueType="enumerated"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.LARGE_MEMORY_MODEL.1426538618" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.LARGE_MEMORY_MODEL" value="true" valueType="boolean"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.UNIFIED_MEMORY.1204196634" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.UNIFIED_MEMORY" value="true" valueType="boolean"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.FLOAT_SUPPORT.912837455" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.FLOAT_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.FLOAT_SUPPORT.fpu32" valueType="enumerated"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.CLA_SUPPORT.467689498" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.CLA_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.CLA_SUPPORT.cla1" valueType="enumerated"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.TMU_SUPPORT.484008760" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.TMU_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.TMU_SUPPORT.tmu0" valueType="enumerated"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.VCU_SUPPORT.1379050903" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.VCU_SUPPORT" value="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.VCU_SUPPORT.vcu2" valueType="enumerated"/>

                                            <!-- Sezione Include Path -->
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.INCLUDE_PATH.1816198112" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.INCLUDE_PATH" valueType="includePath">
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/include"/>
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/include"/>
                                                <listOptionValue builtIn="false" value="C:/ti/ccs1110/ccs/tools/compiler/ti-cgt-c2000_21.6.0.LTS/include"/>
                                                <listOptionValue builtIn="false" value="C:/Users/user/Desktop/untitled_gen/untitled_project/include"/>
                                            </option>

                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DEBUGGING_MODEL.2023058995" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DEBUGGING_MODEL" value="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DEBUGGING_MODEL.SYMDEBUG__DWARF" valueType="enumerated"/>
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DEFINE.928837016" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DEFINE" valueType="definedSymbols">
                                                <listOptionValue builtIn="false" value="CPU1"/>
                                                <listOptionValue builtIn="false" value="_LAUNCHXL_F28379D"/>
                                                <listOptionValue builtIn="false" value="STATE=4"/>
                                                <listOptionValue builtIn="false" value="NREPWMTRIGGERADC=3"/>
                                            </option>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DISPLAY_ERROR_NUMBER.1888790822" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DISPLAY_ERROR_NUMBER" value="true" valueType="boolean"/>
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DIAG_WARNING.1826112291" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.DIAG_WARNING" valueType="stringList">
                                                <listOptionValue builtIn="false" value="225"/>
                                            </option>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.ABI.1734084811" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.ABI" value="com.ti.ccstudio.buildDefinitions.C2000_21.6.compilerID.ABI.coffabi" valueType="enumerated"/>
                                            <inputType id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__C_SRCS.935175564" name="C Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__C_SRCS"/>
                                            <inputType id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__CPP_SRCS.1754916874" name="C++ Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__CPP_SRCS"/>
                                            <inputType id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__ASM_SRCS.966474163" name="Assembly Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__ASM_SRCS"/>
                                            <inputType id="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__ASM2_SRCS.1331774997" name="Assembly Sources" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.compiler.inputType__ASM2_SRCS"/>
                                        </tool>

                                        <!-- Sezione Linker Config -->
                                        <tool id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.linkerDebug.1604840405" name="C2000 Linker" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exe.linkerDebug">
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.MAP_FILE.150192862" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.MAP_FILE" value="&quot;${ProjName}.map&quot;" valueType="string"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.OUTPUT_FILE.508871516" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.OUTPUT_FILE" value="${ProjName}.out" valueType="string"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.STACK_SIZE.794155856" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.STACK_SIZE" value="0x100" valueType="string"/>
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.LIBRARY.779473277" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.LIBRARY" valueType="libs">
                                                <listOptionValue builtIn="false" value="rts2800_fpu32.lib"/>
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd"/>
                                                <listOptionValue builtIn="false" value="C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd"/>
                                                <listOptionValue builtIn="false" value="libc.a"/>
                                            </option>
                                            <option IS_BUILTIN_EMPTY="false" IS_VALUE_EMPTY="false" id="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.SEARCH_PATH.1443810135" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.SEARCH_PATH" valueType="libPaths">
                                                <listOptionValue builtIn="false" value="${CG_TOOL_ROOT}/lib"/>
                                            </option>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.DISPLAY_ERROR_NUMBER.96471687" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.DISPLAY_ERROR_NUMBER" value="true" valueType="boolean"/>
                                            <option id="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.XML_LINK_INFO.1957298402" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.linkerID.XML_LINK_INFO" value="&quot;${ProjName}_linkInfo.xml&quot;" valueType="string"/>
                                            <inputType id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exeLinker.inputType__CMD_SRCS.1799253343" name="Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exeLinker.inputType__CMD_SRCS"/>
                                            <inputType id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exeLinker.inputType__CMD2_SRCS.478843577" name="Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exeLinker.inputType__CMD2_SRCS"/>
                                            <inputType id="com.ti.ccstudio.buildDefinitions.C2000_21.6.exeLinker.inputType__GEN_CMDS.1897434562" name="Generated Linker Command Files" superClass="com.ti.ccstudio.buildDefinitions.C2000_21.6.exeLinker.inputType__GEN_CMDS"/>
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

        # Split the actual and expected content into lines for comparison
        actual_lines = [line.strip() for line in actual_content.splitlines() if line.strip()]
        expected_lines = [line.strip() for line in expected_content.splitlines() if line.strip()]

        # Ensure the number of lines matches
        self.assertEqual(len(actual_lines), len(expected_lines), "Number of lines in the generated content does not match")

        # Verify each line matches
        for i, (actual_line, expected_line) in enumerate(zip(actual_lines, expected_lines), start=1):
            with self.subTest(line=i):
                self.assertEqual(actual_line, expected_line, f"Mismatch at line {i}")


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_define_created_correctly_for_state_4(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the `.cproject` file correctly includes the `STATE` and `NREPWMTRIGGERADC` defines.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `True`, simulating that the directory already exists.
        - The `os.makedirs` function is mocked to ensure it is not invoked since the directory is already present.
        - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
        - The written content of the `.cproject` file is checked to confirm that the `STATE` and `NREPWMTRIGGERADC` defines are correctly generated with the given values.

        """

        create_cproject_file(self.test_model, self.test_ti_path, self.test_c2000_path, self.test_include_path, self.state, self.compiler, self.main4_nr_epwm_trigger_adc)

        # Ensure that os.makedirs is not called because the directory exists. Expected: `mock_makedirs` should not be called
        mock_makedirs.assert_not_called()

        # Verify that the `.cproject` file is opened in write mode. Expected: `mock_file` should be called once with the correct path, mode, and encoding
        mock_file.assert_called_once_with(f"./{self.test_model}_project/.cproject", "w", encoding="utf-8")

        # Capture the content written to the file
        file_handle = mock_file()
        written_content = file_handle.write.call_args[0][0]

        # Verify that the `STATE` define is present in the written content
        # Expected: The content should include `<listOptionValue builtIn="false" value="STATE=<self.state>"/>`
        assert f'<listOptionValue builtIn="false" value="STATE={self.state}"/>' in written_content

        # Verify that the `NREPWMTRIGGERADC` define is present in the written content
        # Expected: The content should include `<listOptionValue builtIn="false" value="NREPWMTRIGGERADC=<self.main4_nr_epwm_trigger_adc>"/>`
        assert f'<listOptionValue builtIn="false" value="NREPWMTRIGGERADC={self.main4_nr_epwm_trigger_adc}"/>' in written_content


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_define_not_present_for_state_1(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the `.cproject` file excludes the conditional `NREPWMTRIGGERADC` define.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `True`, simulating that the directory already exists.
        - The `os.makedirs` function is mocked to ensure it is not invoked since the directory is already present.
        - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
        - The written content of the `.cproject` file is checked to confirm that the `STATE` define is correctly generated with the value `1`,
        and the conditional define `NREPWMTRIGGERADC` is excluded as `main4_nr_epwm_trigger_adc` is `None`.
        
        """

        state = 1
        main4_nr_epwm_trigger_adc = None

        create_cproject_file(self.test_model, self.test_ti_path, self.test_c2000_path, self.test_include_path, state, self.compiler, main4_nr_epwm_trigger_adc)

        # Ensure that os.makedirs is not called because the directory exists. Expected: The directory already exists, so no need to create it.
        mock_makedirs.assert_not_called()

        # Verify that the `.cproject` file is opened in write mode. Expected: The file should be opened for writing.
        mock_file.assert_called_once_with(f"./{self.test_model}_project/.cproject", "w", encoding="utf-8")

        # Capture the content written to the file
        file_handle = mock_file()
        written_content = file_handle.write.call_args[0][0]

        # Verify that the STATE define is present in the written content. Expected: The STATE define should be correctly generated.
        assert f'<listOptionValue builtIn="false" value="STATE={state}"/>' in written_content

        # Verify that the conditional define NREPWMTRIGGERADC is not present. Expected: NREPWMTRIGGERADC should not be included when its value is None.
        assert f'NREPWMTRIGGERADC' not in written_content


    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_combined_directory_and_file_creation(self, mock_file, mock_exists, mock_makedirs):

        """

        Verify that the directory is created, and the `.cproject` file is written correctly when the directory does not exist.

        Simulated Condition:
        - The `os.path.exists` function is mocked to return `False`, simulating that the directory does not exist.
        - The `os.makedirs` function is mocked to ensure the directory creation logic is invoked.
        - The `open` function is mocked to intercept and verify the `.cproject` file writing operation.
        - The written content of the `.cproject` file is checked to confirm that the `STATE` define is correctly generated and the
          conditional define `NREPWMTRIGGERADC` is included as `main4_nr_epwm_trigger_adc` is set to `3`.

        """

        project_dir = f"./{self.test_model}_project"
        cproject_file = f"{project_dir}/.cproject"

        create_cproject_file(self.test_model, self.test_ti_path, self.test_c2000_path, self.test_include_path, self.state, self.compiler, self.main4_nr_epwm_trigger_adc)

        # Verify that `os.makedirs` is called with the correct directory path. Expected: The directory is created since it does not exist.
        mock_makedirs.assert_called_once_with(project_dir)

        # Verify that the `.cproject` file is opened in write mode. Expected: The file is opened for writing.
        mock_file.assert_called_once_with(cproject_file, "w", encoding="utf-8")

        # Capture the content written to the `.cproject` file
        file_handle = mock_file()
        written_content = file_handle.write.call_args[0][0]

        # Verify that the `STATE` define is present in the content
        assert f'<listOptionValue builtIn="false" value="STATE={self.state}"/>' in written_content

        # Verify that the `NREPWMTRIGGERADC` define is present in the content
        assert f'<listOptionValue builtIn="false" value="NREPWMTRIGGERADC={self.main4_nr_epwm_trigger_adc}"/>' in written_content


if __name__ == "__main__":
    unittest.main()
