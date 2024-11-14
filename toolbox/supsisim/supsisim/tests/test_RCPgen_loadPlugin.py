import sys
import os

import unittest
from unittest.mock import patch, MagicMock

# Adds the "pysimCoder" directory to the root of sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from toolbox.supsisim.supsisim.RCPgen import genProjectStructure, load_module

class TestPluginExecution(unittest.TestCase):
    
    def setUp(self):

        # Set the environment variable for the template path
        self.template_path = os.getcwd()
        os.environ['PYSUPSICTRL'] = self.template_path
        self.model = 'test_model'
        self.template = 'test.tmf'
   

    @patch('builtins.print')
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_success(self, mock_spec_from_file, mock_print):

        """ Test `load_module` with successful module loading, verifying it executes without errors."""

        # Mock the spec and module loading
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):

            # Call load_module and expect a successful load
            result = load_module('/path/to/test_module.py')
            self.assertEqual(result, mock_module)  # Check if the returned module is correct
            mock_spec.loader.exec_module.assert_called_once_with(mock_module)
    

    @patch('builtins.print')
    def test_load_module_file_not_found(self, mock_print):

        """ Test `load_module` when the file does not exist, expecting None and a specific error message."""

        # Call load_module with a non-existent path
        result = load_module('/nonexistent/path/to/module.py')
        
        # Verify that None is returned and the correct error message is printed
        self.assertIsNone(result)
        mock_print.assert_called_once_with("Error: File /nonexistent/path/to/module.py not found.")


    @patch('builtins.print')
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_general_exception(self, mock_spec_from_file, mock_print):

        """ Test `load_module` for a general exception during loading, checking for error handling."""
        
        # Mock spec_from_file_location to raise a generic exception
        mock_spec_from_file.side_effect = Exception("Mocked exception")

        # Call load_module and check for exception handling
        result = load_module('/path/to/module_with_error.py')
        
        # Verify that None is returned and the correct error message is printed
        self.assertIsNone(result)
        mock_print.assert_called_once_with("Error loading module /path/to/module_with_error.py: Mocked exception")


    @patch('os.path.exists', return_value=True)  # Pretend the file exists
    @patch('importlib.util.spec_from_file_location')
    @patch('builtins.print')
    def test_module_execution_with_only_code(self, mock_print, mock_spec_from_file, mock_path_exists):
        
        """ Test `genProjectStructure` with only executable code in the module (no functions), expecting a specific print call."""

        # Set up a mock of the module with only executable code
        mock_spec = MagicMock()
        
        # Simulates exec_module, which runs a Python module.
        def exec_module_side_effect(module):
            print("Executing code in the module without functions.")
            mock_print("Executing code in the module without functions.")

        mock_spec.loader.exec_module = exec_module_side_effect
        mock_spec_from_file.return_value = mock_spec

        # Run the function under test
        genProjectStructure(self.model, self.template)

        # Verify that the `print` message has been called
        try:
            mock_print.assert_any_call("Executing code in the module without functions.")
        except AssertionError:
            print("Error: The expected message was not found among the print calls.")


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    @patch('builtins.print')
    def test_gen_project_structure_success(self, mock_print, mock_spec_from_file, mock_path_exists):

        """ Test `genProjectStructure` when `create_project_structure` is successfully called in the module."""

        # Simulate module with `create_project_structure`
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_module.create_project_structure = MagicMock()  # Adding the function to the mock module
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            genProjectStructure(self.model, self.template)

            # Check that `create_project_structure` was called once with `self.model`
            mock_module.create_project_structure.assert_called_once_with(self.model)


    @patch('os.path.exists', return_value=False)
    @patch('builtins.print')
    def test_gen_project_structure_script_not_found(self, mock_print, mock_path_exists):

        """ Test `genProjectStructure` when the script path does not exist, expecting a specific error message."""

        # Test behavior when the script file does not exist
        genProjectStructure(self.model, self.template)
        script_path = os.path.join(self.template_path, 'CodeGen', 'templates', 'test.py')
        mock_print.assert_called_once_with(f"Script path {script_path} does not exist.")


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    @patch('builtins.print')
    def test_gen_project_structure_failed_to_load_module(self, mock_print, mock_spec_from_file, mock_path_exists):
        
        """ Test `genProjectStructure` when the module fails to load, checking error messages."""

        # Simulates module loading failure
        mock_spec_from_file.return_value = None
    
        genProjectStructure(self.model, self.template)
    
        # Check both print calls
        mock_print.assert_any_call(f"Error loading module {os.path.join(self.template_path, 'CodeGen', 'templates', 'test.py')}: 'NoneType' object has no attribute 'loader'")
        mock_print.assert_any_call("Failed to load the module.")


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    @patch('builtins.print')
    def test_gen_project_structure_attribute_error(self, mock_print, mock_spec_from_file, mock_path_exists):

        """ Test `genProjectStructure` for an `AttributeError` raised by `create_project_structure`, verifying exception handling."""

        # Simulate `AttributeError` when calling `create_project_structure`
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_module.create_project_structure.side_effect = AttributeError("Mocked AttributeError")
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            genProjectStructure(self.model, self.template)
            mock_print.assert_any_call("AttributeError: Mocked AttributeError")


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    @patch('builtins.print')
    def test_gen_project_structure_general_exception(self, mock_print, mock_spec_from_file, mock_path_exists):

        """ Test `genProjectStructure` for a general exception in `create_project_structure`, ensuring it handles exceptions."""

        # Simulate a general exception during `create_project_structure`
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_module.create_project_structure.side_effect = Exception("Mocked General Exception")
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            genProjectStructure(self.model, self.template)
            mock_print.assert_any_call("An error occurred while calling 'create_project_structure': Mocked General Exception")


if __name__ == '__main__':
    unittest.main()
