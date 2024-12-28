
import sys
import os
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from toolbox.supsisim.supsisim.RCPgen import load_module, run_plugin, genCode


"""

Unit Tests for RCPgen.py Functions

This file contains unit tests for the `load_module` and `run_plugin` functions 
in the RCPgen.py file. These tests ensure the functions behave correctly under various conditions 
and exceptions. The following scenarios are tested:


1. `load_module`:

   - `test_load_module_file_not_found`:              Test that load_module returns None if the file does not exist.
                                                     Simulated condition: The file specified by module_path is not present on the filesystem.

   - `test_load_module_success`:                     Test that load_module successfully loads a module when the file exists and is valid.
                                                     Simulated condition: The specified file exists on the filesystem and is a valid Python module.

   - `test_load_module_file_not_found_exception`:    Test that load_module returns None and outputs the correct error message when the file does not exist.
                                                     Simulated condition: The file exists but is removed or inaccessible before loading.
                                                     Expected error message: "Error: File /path/to/nonexistent_module.py not found."
    
   - `test_load_module_import_error`:                Test that load_module returns None and outputs the correct error message when an ImportError occurs.
                                                     Simulated condition: The specified file exists on the filesystem, but the module import fails due to invalid content or missing dependencies.
                                                     Expected error message: "ImportError: Mocked ImportError"

   - `test_load_module_generic_exception`:           Test that load_module returns None and outputs the correct error message when a generic exception occurs
                                                     Simulated condition: The specified file exists on the filesystem, but an unexpected error occurs during module loading.
                                                     Expected error message: "Error loading module /path/to/faulty_module.py: Mocked Generic Exception"

2. `run_plugin`:

    - `test_run_plugin_script_not_found`:            Test that run_plugin does nothing (does not generate exceptions) and produces no output if the script does not exist.
                                                     Simulated condition: The specified plugin file (.py) does not exist on the filesystem.

    - `test_run_plugin_with_function_success`:       Test that run_plugin does nothing (does not generate exceptions) if the specified function is not found in the plugin.
                                                     The script's global code (outside of functions) is executed, but no errors are raised.
                                                     Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function does not exist in the module.
    
    - `test_run_plugin_function_not_found`:          Test that run_plugin successfully executes a specified function present in the plugin.
                                                     Simulated condition: The specified plugin file (.py) exists and is loaded. The requested function is defined in the module and is executed with the provided arguments.

    - `test_run_plugin_environment_error`:           Test that run_plugin handles an EnvironmentError and outputs the correct error message to the console.
                                                     Simulated condition: An issue occurs while accessing the environment variable required for locating the plugin.
                                                     Expected error message: "EnvironmentError: Mocked EnvironmentError"

    - test_run_plugin_general_unexpected_exception : Test that run_plugin handles a general unexpected Exception at the top level and outputs the correct error message to the console.
                                                     Simulated condition: An unexpected error occurs during the initial setup or processing of the plugin script, before any function execution begins.
                                                     Expected error message: "An unexpected error occurred: Mocked Top-Level Exception"

    - `test_run_plugin_attribute_error`:             Test that run_plugin handles an AttributeError and outputs the correct error message to the console.
                                                     Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function raises an AttributeError during execution.
                                                     Expected error message: "AttributeError: Mocked AttributeError"

    - `test_run_plugin_type_error`:                  Test that run_plugin handles a TypeError and outputs the correct error message to the console.
                                                     Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function raises a TypeError during execution.
                                                     Expected error message: "TypeError: Mocked TypeError"

    - `test_run_plugin_general_exception`:           Test that run_plugin handles a general Exception and outputs the correct error message to the console.
                                                     Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function raises an unexpected Exception during execution.
                                                     Expected error message: "An unexpected error occurred while calling 'some_function': Mocked General Exception"


Each test uses mocking to simulate various scenarios and validate the output and behavior of the functions.

"""


class TestPluginExecution(unittest.TestCase):

    def setUp(self):
        self.template_path = os.getcwd()
        os.environ['PYSUPSICTRL'] = self.template_path
        self.model = 'test_model'
        self.template = 'test.tmf'


    @patch('os.path.exists', return_value=False)
    def test_load_module_file_not_found(self, mock_path_exists):

        """ Test that load_module returns None if the file does not exist. """
        """ Simulated condition: The file specified by module_path is not present on the filesystem. """

        result = load_module('/nonexistent/path/to/module.py')

        # Assert that the function returns None since the file does not exist
        self.assertIsNone(result)


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_success(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module successfully loads a module when the file exists and is valid. """
        """ Simulated condition: The specified file exists on the filesystem and is a valid Python module. """

        # Create mock objects for the spec and module
        mock_spec = MagicMock()
        mock_module = MagicMock()

        # Mock the exec_module method
        mock_spec.loader.exec_module = MagicMock()

        # Return the mocked spec
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            result = load_module('/path/to/test_module.py')

            # Assert that the loaded module matches the mock module
            self.assertEqual(result, mock_module)

            # Assert that the loader's exec_module method was called once with the mock module
            mock_spec.loader.exec_module.assert_called_once_with(mock_module)


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_file_not_found_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module returns None and outputs the correct error message when the file does not exist. """
        """ Simulated condition: The file exists but is removed or inaccessible before loading. """
        """ Expected error message: "Error: File /path/to/nonexistent_module.py not found." """

        # Simulate a FileNotFoundError when trying to create the module spec
        mock_spec_from_file.side_effect = FileNotFoundError("Mocked FileNotFoundError")
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = load_module('/path/to/nonexistent_module.py')

            # Assert that the function returns None
            self.assertIsNone(result)

            # Assert that the correct error message is printed
            self.assertIn("Error: File /path/to/nonexistent_module.py not found.", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_import_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module returns None and outputs the correct error message when an ImportError occurs. """
        """ Simulated condition: The specified file exists on the filesystem, but the module import fails due to invalid content or missing dependencies. """
        """ Expected error message: "ImportError: Mocked ImportError" """

        # Simulate an ImportError when trying to create the module specification.
        mock_spec_from_file.side_effect = ImportError("Mocked ImportError")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = load_module('/path/to/invalid_module.py')

            # Assert that the function returns None
            self.assertIsNone(result)

            # Assert that the correct error message is printed
            self.assertIn("ImportError: Mocked ImportError", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_generic_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module returns None and outputs the correct error message when a generic exception occurs. """
        """ Simulated condition: The specified file exists on the filesystem, but an unexpected error occurs during module loading. """
        """ Expected error message: "Error loading module /path/to/faulty_module.py: Mocked Generic Exception" """
        
        # Simulate an unexpected error when creating the module specification.
        mock_spec_from_file.side_effect = Exception("Mocked Generic Exception")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = load_module('/path/to/faulty_module.py')

            # Assert that the function returns None
            self.assertIsNone(result)

            # Assert that the correct error message is printed
            self.assertIn("Error loading module /path/to/faulty_module.py: Mocked Generic Exception", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=False)
    def test_run_plugin_script_not_found(self, mock_path_exists):

        """ Test that run_plugin does nothing (does not generate exceptions) and produces no output if the script does not exist. """
        """ Simulated condition: The specified plugin file (.py) does not exist on the filesystem. """

        # No exceptions or outputs expected if the script does not exist.
        # Because the plugin (.py) may or may not be there.

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_plugin(self.model, self.template)

        # Verify that no exceptions were raised and the console output is empty
        self.assertEqual(mock_stdout.getvalue(), "")


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_function_not_found(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin does nothing (does not generate exceptions). if the specified function is not found in the plugin. """
        """ The script's global code (outside of functions) is executed, but no errors are raised. """
        """ Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function does not exist in the module. """

        # Simulate the module specification and loader for the plugin
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            run_plugin(self.model, self.template, function_name='non_existent_function')

            # Assert that the module's global code was executed
            mock_spec.loader.exec_module.assert_called_once_with(mock_module)

            # Assert no exceptions are raised
            self.assertTrue(True)


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_with_function_success(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin successfully executes a specified function present in the plugin. """
        """ Simulated condition: The specified plugin file (.py) exists and is loaded. The requested function is defined in the module and is executed with the provided arguments. """

        # Mock the specification object for the plugin module
        mock_spec = MagicMock()

        # Mock the module object and its function
        mock_module = MagicMock()
        mock_module.some_function = MagicMock()

        # Mock the exec_module method to simulate loading the module
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            run_plugin(self.model, self.template, function_name='some_function', function_args={'arg1': 'value1'})

            # Assert that the specified function in the module was called exactly once with the correct arguments
            mock_module.some_function.assert_called_once_with(arg1='value1')


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_environment_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin handles an EnvironmentError and outputs the correct error message to the console. """
        """ Simulated condition: An issue occurs while accessing the environment variable required for locating the plugin. """
        """ Expected error message: "EnvironmentError: Mocked EnvironmentError" """

        # Simulate an EnvironmentError when trying to access the environment variable and capture the standard output to verify the error message
        with patch('os.environ.get', side_effect=EnvironmentError("Mocked EnvironmentError")), patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_plugin(self.model, self.template)

            # Assert that the correct error message is printed
            self.assertIn("EnvironmentError: Mocked EnvironmentError", mock_stdout.getvalue())

    
    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_general_unexpected_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin handles a general unexpected Exception at the top level and outputs the correct error message to the console. """
        """ Simulated condition: An unexpected error occurs during the initial setup or processing of the plugin script, before any function execution begins. """
        """ Expected error message: "An unexpected error occurred: Mocked Top-Level Exception" """

        # Simulate a valid module loading
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):

            # Simulate an exception occurring at the top level of the run_plugin function
            with patch('os.path.join', side_effect=Exception("Mocked Top-Level Exception")), \
                 patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            
                # Attempt to execute run_plugin
                run_plugin(self.model, self.template)
            
                # Assert that the correct error message is printed
                self.assertIn("An unexpected error occurred: Mocked Top-Level Exception", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_attribute_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin handles an AttributeError and outputs the correct error message to the console. """
        """ Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function raises an AttributeError during execution. """
        """ Expected error message: "AttributeError: Mocked AttributeError" """

        # Mock the module specification and loader for the plugin
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock() # Simulate successful execution of the module loader
        mock_spec_from_file.return_value = mock_spec

        # Simulate the creation of the module from the specification
        with patch('importlib.util.module_from_spec', return_value=mock_module):
            
            # Simulate a function in the module that raises an AttributeError when called
            mock_module.some_function = MagicMock(side_effect=AttributeError("Mocked AttributeError"))

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_plugin(self.model, self.template, function_name='some_function')

                # Assert that the correct error message is printed
                self.assertIn("AttributeError: Mocked AttributeError", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_type_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin handles a TypeError and outputs the correct error message to the console.  """
        """ Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function raises a TypeError during execution. """
        """ Expected error message: "TypeError: Mocked TypeError" """

        # Mock the module specification and loader for the plugin
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        # Simulate the successful creation of the module from the specification
        with patch('importlib.util.module_from_spec', return_value=mock_module):

            # Simulate a TypeError being raised by the specified function in the plugin
            mock_module.some_function = MagicMock(side_effect=TypeError("Mocked TypeError"))

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_plugin(self.model, self.template, function_name='some_function')

                # Assert that the correct error message is printed
                self.assertIn("TypeError: Mocked TypeError", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_general_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin handles a general Exception and outputs the correct error message to the console. """
        """ Simulated condition: The specified plugin file (.py) exists and is loaded, but the requested function raises an unexpected Exception during execution. """
        """ Expected error message: "An unexpected error occurred while calling 'some_function': Mocked General Exception" """

        # Simulate the module specification and loader for the plugin
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        # Simulate the successful creation of the module from the specification
        with patch('importlib.util.module_from_spec', return_value=mock_module):

            # Simulate an unexpected exception being raised by the requested function
            mock_module.some_function = MagicMock(side_effect=Exception("Mocked General Exception"))
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_plugin(self.model, self.template, function_name='some_function')

                # Assert that the correct error message is printed
                self.assertIn("An unexpected error occurred while calling 'some_function': Mocked General Exception", mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
