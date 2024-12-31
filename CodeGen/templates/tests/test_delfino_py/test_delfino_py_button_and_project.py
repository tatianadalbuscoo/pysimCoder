
import os
import sys
import unittest
from unittest.mock import patch, MagicMock,  call
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))
from delfino import press_configure_button, create_project_structure


"""

This test suite primarily focuses on two functions: `press_configure_button` and `create_project_structure`.

- press_configure_button:
    - Tests ensure that this function executes its steps in the correct order, validates parameters, and interacts correctly with its dependencies.

- create_project_structure:
    - Since this function is more complex, testing is limited to key elements such as directory creation and verifying the essential call to the check_wsl_environment function.
    - Due to its complexity and reliance on graphical interfaces (e.g., `QApplication`, `QMessageBox`, and `ProjectConfigWindow`), comprehensive testing of graphical components was avoided for simplicity and time constraints.
    - Future improvements can include isolating and mocking the graphical interactions to increase test coverage.
   

- Test press_configure_button function: 

    - test_press_configure_button_order:                            Test that press_configure_button executes its instructions in the correct order and validates the parameters passed to each function.

                                                                    Simulated Conditions:
                                                                    - `check_wsl_environment` is expected to be called first to verify the WSL environment.
                                                                    - `open_config_window` returns True, simulating that the configuration window was confirmed.
                                                                    - `general_config.load` returns a mock configuration dictionary with valid paths and a compiler version.
                                                                    - `check_paths` validates the paths (`ti_path`, `c2000Ware_path`, `compiler_version`) returned by `general_config.load`.
                                                                    - `QApplication` is mocked to simulate the presence of a running application instance.

- Test create_project_structure function:

    - test_create_project_structure_creates_required_directories:   Test that `create_project_structure` correctly creates the required directories.

                                                                    Simulated Conditions:
                                                                    - `os.makedirs` is mocked to verify that directories are created at the correct paths.
                                                                    - `os.path.join` is mocked to simulate the generation of directory paths.
                                                                    - `os.path.exists` is mocked to simulate the existence of required files or directories.
                                                                    - All external dependencies (e.g., `general_config`, `QMessageBox`, `ProjectConfigWindow`) 
                                                                      are mocked to remove reliance on real implementations.

    - test_create_project_structure_calls_check_wsl_environment:    Test that `create_project_structure` calls `check_wsl_environment`.

                                                                    Simulated Conditions:
                                                                    - `check_wsl_environment` is mocked to verify that it is called.
                                                                    - Other dependencies are mocked to isolate the behavior of `check_wsl_environment`.
                                                                    - Directory creation and configuration loading are also simulated.

"""


#################################################################################################################################################
# Test press_configure_button function
#################################################################################################################################################

class TestPressConfigureButton(unittest.TestCase):


    @patch('delfino.check_wsl_environment')
    @patch('delfino.open_config_window')
    @patch('delfino.general_config.load')
    @patch('delfino.check_paths')
    @patch('delfino.QApplication')
    def test_press_configure_button_order(self, mock_qapplication, mock_check_paths, mock_config_load, mock_open_config_window, mock_check_wsl):

        """

        Test that press_configure_button executes its instructions in the correct order and validates the parameters passed to each function.

        Simulated Conditions:
        ----------------------
        - `check_wsl_environment` is expected to be called first to verify the WSL environment.
        - `open_config_window` returns True, simulating that the configuration window was confirmed.
        - `general_config.load` returns a mock configuration dictionary with valid paths and a compiler version.
        - `check_paths` validates the paths (`ti_path`, `c2000Ware_path`, `compiler_version`) returned by `general_config.load`.
        - `QApplication` is mocked to simulate the presence of a running application instance.

        """

        # Mock setup
        mock_open_config_window.return_value = True
        mock_config_load.return_value = {
            'ti_path': '/mock/ti_path',
            'c2000Ware_path': '/mock/c2000Ware_path',
            'compiler_version': 'mock_compiler'
        }

        press_configure_button()

        # Check WSL environment. Expected: Called once
        mock_check_wsl.assert_called_once()

        # Open config window. Expected: Called once
        mock_open_config_window.assert_called_once()

        # Load saved config. Expected: Called once
        mock_config_load.assert_called_once()

        # Validate paths with config. Expected: ParametersMatched
        mock_check_paths.assert_called_once_with('/mock/ti_path', '/mock/c2000Ware_path', 'mock_compiler')

        expected_order = [
            call(),
            call(),
            call(),
            call('/mock/ti_path', '/mock/c2000Ware_path', 'mock_compiler')
        ]

        actual_order = [
            mock_check_wsl.call_args,
            mock_open_config_window.call_args,
            mock_config_load.call_args,
            mock_check_paths.call_args
        ]

        # Verify the order of function calls. Expected: Matched order
        self.assertEqual(expected_order, actual_order)


#################################################################################################################################################
# Test create_project_structure function
#################################################################################################################################################

class TestCreateProjectStructure(unittest.TestCase):


    @patch('delfino.open')
    @patch('delfino.ProjectConfigWindow')
    @patch('delfino.QMessageBox')
    @patch('delfino.create_cproject_file')
    @patch('delfino.create_project_file')
    @patch('delfino.create_ccsproject_file')
    @patch('delfino.find_and_copy_files')
    @patch('delfino.shutil')
    @patch('delfino.os')
    @patch('delfino.general_config')
    @patch('delfino.check_blocks_list')
    @patch('delfino.check_blocks_set')
    def test_create_project_structure_creates_required_directories(
        self,
        mock_check_blocks_set,
        mock_check_blocks_list,
        mock_general_config,
        mock_os,
        mock_shutil,
        mock_find_and_copy_files,
        mock_create_ccsproject_file,
        mock_create_project_file,
        mock_create_cproject_file,
        mock_QMessageBox,
        mock_ProjectConfigWindow,
        mock_open,
    ):

        """

        Test that `create_project_structure` correctly creates the required directories.

        Simulated Conditions:
        - `os.makedirs` is mocked to verify that directories are created at the correct paths.
        - `os.path.join` is mocked to simulate the generation of directory paths.
        - `os.path.exists` is mocked to simulate the existence of required files or directories.
        - All external dependencies (e.g., `general_config`, `QMessageBox`, `ProjectConfigWindow`) 
          are mocked to remove reliance on real implementations.

        """

        # Mock the behavior of ProjectConfigWindow
        mock_config_window_instance = MagicMock()
        mock_config_window_instance.get_current_state.return_value = 1
        mock_ProjectConfigWindow.return_value = mock_config_window_instance

        # Mock the loading of general_config
        mock_general_config.load.return_value = {
            "ti_path": "/mock/ti_path",
            "c2000Ware_path": "/mock/c2000Ware_path",
            "compiler_version": "mock_compiler",
        }
        mock_general_config.path = "/mock/config/path"

        # Mock open_project_config_window
        mock_open_project_config_window = MagicMock()
        mock_open_project_config_window.return_value = {
            "timer_period": 1000,
            "epwm_output_mode1": "out1a",
            "epwm_output_mode2": None,
        }

        # Mock check_blocks_set and check_blocks_list
        mock_check_blocks_set.return_value = {"function1", "function2"}
        mock_check_blocks_list.return_value = ["block1", "block2"]

        # Mock OS operations
        mock_os.path.exists.return_value = True
        mock_os.makedirs = MagicMock()
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.dirname.return_value = "/mock/parent_dir"

        # Mock shutil.move
        mock_shutil.move = MagicMock()

        # Mock file opening
        mock_open.return_value = MagicMock()

        # Mock the hardcoded path
        pysimcoder_path = "/mock/pysimcoder"

        create_project_structure("mock_model", ["block1", "block2"])

        # Verify that makedirs was called with the correct directory paths
        expected_calls = [
            call("./mock_model_project/src", exist_ok=True),            # Expected: Source directory
            call("./mock_model_project/include", exist_ok=True),        # Expected: Include directory
            call("./mock_model_project/targetConfigs", exist_ok=True),  # Expected: targetConfigs directory
        ]
        mock_os.makedirs.assert_has_calls(expected_calls, any_order=True)


    @patch('delfino.open')
    @patch('delfino.ProjectConfigWindow')
    @patch('delfino.QMessageBox')
    @patch('delfino.create_cproject_file')
    @patch('delfino.create_project_file')
    @patch('delfino.create_ccsproject_file')
    @patch('delfino.find_and_copy_files')
    @patch('delfino.shutil')
    @patch('delfino.os')
    @patch('delfino.general_config')
    @patch('delfino.check_blocks_list')
    @patch('delfino.check_blocks_set')
    @patch('delfino.check_wsl_environment')
    def test_create_project_structure_calls_check_wsl_environment(
        self,
        mock_check_wsl_environment,
        mock_check_blocks_set,
        mock_check_blocks_list,
        mock_general_config,
        mock_os,
        mock_shutil,
        mock_find_and_copy_files,
        mock_create_ccsproject_file,
        mock_create_project_file,
        mock_create_cproject_file,
        mock_QMessageBox,
        mock_ProjectConfigWindow,
        mock_open,
    ):

        """

        Test that `create_project_structure` calls `check_wsl_environment`.

        Simulated Conditions:
        - `check_wsl_environment` is mocked to verify that it is called.
        - Other dependencies are mocked to isolate the behavior of `check_wsl_environment`.
        - Directory creation and configuration loading are also simulated.

        """

        # Mock the behavior of ProjectConfigWindow
        mock_config_window_instance = MagicMock()
        mock_config_window_instance.get_current_state.return_value = 1
        mock_ProjectConfigWindow.return_value = mock_config_window_instance

        # Mock the loading of general_config
        mock_general_config.load.return_value = {
            "ti_path": "/mock/ti_path",
            "c2000Ware_path": "/mock/c2000Ware_path",
            "compiler_version": "mock_compiler",
        }
        mock_general_config.path = "/mock/config/path"

        # Mock open_project_config_window
        mock_open_project_config_window = MagicMock()
        mock_open_project_config_window.return_value = {
            "timer_period": 1000,
            "epwm_output_mode1": "out1a",
            "epwm_output_mode2": None,
        }

        # Mock check_blocks_set and check_blocks_list
        mock_check_blocks_set.return_value = {"function1", "function2"}
        mock_check_blocks_list.return_value = ["block1", "block2"]

        # Mock OS operations
        mock_os.path.exists.return_value = True
        mock_os.makedirs = MagicMock()
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.dirname.return_value = "/mock/parent_dir"

        # Mock shutil.move
        mock_shutil.move = MagicMock()

        # Mock file opening
        mock_open.return_value = MagicMock()

        # Mock the hardcoded path
        pysimcoder_path = "/mock/pysimcoder"

        create_project_structure("mock_model", ["block1", "block2"])

        # Verify that check_wsl_environment was called. Expected: check_wsl_environment is called once
        mock_check_wsl_environment.assert_called_once()


if __name__ == "__main__":
    unittest.main()
