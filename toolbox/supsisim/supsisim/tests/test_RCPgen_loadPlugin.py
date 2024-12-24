import sys
import os
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock


"""

Unit Tests for RCPgen.py Functions

This file contains unit tests for the `load_module` and `run_plugin` functions 
in the RCPgen.py file. These tests ensure the functions behave correctly under various conditions 
and exceptions. The following scenarios are tested:


1. `load_module`:

   - `test_load_module_file_not_found`:           Ensures `None` is returned when the specified file does not exist.
   - `test_load_module_success`:                  Confirms that a valid module is successfully loaded when the file exists.
   - `test_load_module_file_not_found_exception`: Verifies that `FileNotFoundError` is handled, and the correct error message is output.
   - `test_load_module_exceptions_handling`:      Ensures that exceptions (`FileNotFoundError`, `ImportError`, generic exceptions) are handled without crashing the application.
   - `test_load_module_import_error`:             Tests that `ImportError` is caught and the appropriate error message is output.
   - `test_load_module_generic_exception`:        Confirms that generic exceptions are caught and the correct error message is output.


2. `run_plugin`:

    - `test_run_plugin_script_not_found`:          Ensures that no action is taken and no output is generated when the script file is missing.
    - `test_run_plugin_with_function_success`:     Confirms that a specified function is executed successfully when it exists.
    - `test_run_plugin_function_not_found`:        Verifies that the script executes without errors if the specified function is not found.
    - `test_run_plugin_function_raises_exception`: Tests that exceptions (`AttributeError`, `TypeError`, general exceptions, and `EnvironmentError`) raised during function execution are handled without crashing the application.
    - `test_run_plugin_environment_error`:         Ensures `EnvironmentError` is caught and outputs the appropriate error message.
    - `test_run_plugin_attribute_error`:           Validates that `AttributeError` is caught and outputs the appropriate error message.
    - `test_run_plugin_type_error`:                Checks that `TypeError` is caught and outputs the appropriate error message.
    - `test_run_plugin_general_exception`:         Ensures general exceptions are caught and outputs the appropriate error message.

Each test uses mocking to simulate various scenarios and validate the output and behavior of the functions.

"""


# Adjust the path to include the "pysimCoder" directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from toolbox.supsisim.supsisim.RCPgen import load_module, run_plugin

class TestPluginExecution(unittest.TestCase):

    def setUp(self):
        self.template_path = os.getcwd()
        os.environ['PYSUPSICTRL'] = self.template_path
        self.model = 'test_model'
        self.template = 'test.tmf'


    @patch('os.path.exists', return_value=False)
    def test_load_module_file_not_found(self, mock_path_exists):

        """ Test that load_module returns None if the file does not exist. """

        result = load_module('/nonexistent/path/to/module.py')
        self.assertIsNone(result)


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_success(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module load_module successfully loads a module when the file exists and is valid. """

        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            result = load_module('/path/to/test_module.py')
            self.assertEqual(result, mock_module)
            mock_spec.loader.exec_module.assert_called_once_with(mock_module)


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_file_not_found_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module returns None and outputs the correct error message 
        when the file does not exist. """

        mock_spec_from_file.side_effect = FileNotFoundError("Mocked FileNotFoundError")
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = load_module('/path/to/nonexistent_module.py')
            self.assertIsNone(result)
            self.assertIn("Error: File /path/to/nonexistent_module.py not found.", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_exceptions_handling(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module handles all exceptions without crashing the application. """

        # Simulate FileNotFoundError during module import
        with patch('importlib.util.module_from_spec', side_effect=FileNotFoundError("Mocked FileNotFoundError")):
            result = load_module('/path/to/nonexistent_module.py')
            self.assertIsNone(result)

        # Simulate ImportError during module import
        with patch('importlib.util.module_from_spec', side_effect=ImportError("Mocked ImportError")):
            result = load_module('/path/to/faulty_module.py')
            self.assertIsNone(result)

        # Simulate a generic Exception during module import
        with patch('importlib.util.module_from_spec', side_effect=Exception("Mocked Generic Exception")):
            result = load_module('/path/to/faulty_module.py')
            self.assertIsNone(result)


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_import_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module handles ImportError and outputs the correct error message. """

        mock_spec_from_file.side_effect = ImportError("Mocked ImportError")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = load_module('/path/to/invalid_module.py')
            self.assertIsNone(result)
            self.assertIn("ImportError: Mocked ImportError", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_load_module_generic_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that load_module handles generic exceptions and outputs the correct error message. """

        mock_spec_from_file.side_effect = Exception("Mocked Generic Exception")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = load_module('/path/to/faulty_module.py')
            self.assertIsNone(result)
            self.assertIn("Error loading module /path/to/faulty_module.py: Mocked Generic Exception", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=False)
    def test_run_plugin_script_not_found(self, mock_path_exists):

        """ Test that run_plugin does nothing if the script does not exist. """

        # No exceptions or outputs expected if the script does not exist.
        # Because the plugin (.py) may or may not be there.

        run_plugin(self.model, self.template)


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_function_not_found(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin does nothing if the function is not found. """

        # Even if the specified function is not found, the script's code outside functions is executed. 

        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            run_plugin(self.model, self.template, function_name='non_existent_function')
            

    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_with_function_success(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin executes a specified function successfully. """

        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_module.some_function = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            run_plugin(self.model, self.template, function_name='some_function', function_args={'arg1': 'value1'})
            mock_module.some_function.assert_called_once_with(arg1='value1')


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_function_raises_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that run_plugin handles exceptions raised by the function without crashing the application. """
    
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):

            # AttributeError
            mock_module.some_function = MagicMock(side_effect=AttributeError("Mocked AttributeError"))
            run_plugin(self.model, self.template, function_name='some_function')
            # No crash expected

            # TypeError
            mock_module.some_function = MagicMock(side_effect=TypeError("Mocked TypeError"))
            run_plugin(self.model, self.template, function_name='some_function')
            # No crash expected

            # General Exception
            mock_module.some_function = MagicMock(side_effect=Exception("Mocked General Exception"))
            run_plugin(self.model, self.template, function_name='some_function')
            # No crash expected

            # EnvironmentError
            with patch('os.environ.get', side_effect=EnvironmentError("Mocked EnvironmentError")):
                run_plugin(self.model, self.template, function_name='some_function')
                # No crash expected for EnvironmentError

            # FileNotFoundError (simulating a missing template file)
            with patch('os.path.exists', return_value=False):
                run_plugin(self.model, self.template)
                # No crash expected for missing script


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_environment_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that EnvironmentError is handled correctly and its message is output to the console. """

        with patch('os.environ.get', side_effect=EnvironmentError("Mocked EnvironmentError")), patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_plugin(self.model, self.template)
            self.assertIn("EnvironmentError: Mocked EnvironmentError", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_attribute_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that AttributeError is handled correctly and its message is output to the console. """

        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            mock_module.some_function = MagicMock(side_effect=AttributeError("Mocked AttributeError"))
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_plugin(self.model, self.template, function_name='some_function')
                self.assertIn("AttributeError: Mocked AttributeError", mock_stdout.getvalue())


    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_type_error(self, mock_spec_from_file, mock_path_exists):

        """ Test that TypeError is handled correctly and its message is output to the console. """

        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            mock_module.some_function = MagicMock(side_effect=TypeError("Mocked TypeError"))
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_plugin(self.model, self.template, function_name='some_function')
                self.assertIn("TypeError: Mocked TypeError", mock_stdout.getvalue())

    @patch('os.path.exists', return_value=True)
    @patch('importlib.util.spec_from_file_location')
    def test_run_plugin_general_exception(self, mock_spec_from_file, mock_path_exists):

        """ Test that a general Exception is handled correctly and its message is output to the console. """

        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_spec.loader.exec_module = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        with patch('importlib.util.module_from_spec', return_value=mock_module):
            mock_module.some_function = MagicMock(side_effect=Exception("Mocked General Exception"))
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_plugin(self.model, self.template, function_name='some_function')
                self.assertIn("An unexpected error occurred while calling 'some_function': Mocked General Exception", mock_stdout.getvalue())

    @patch('os.path.exists', return_value=False)
    def test_run_plugin_script_not_found(self, mock_path_exists):

        """ Test that run_plugin handles a missing script correctly with no output to the console. """

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_plugin(self.model, self.template)
            self.assertEqual(mock_stdout.getvalue(), "")

if __name__ == '__main__':
    unittest.main()
