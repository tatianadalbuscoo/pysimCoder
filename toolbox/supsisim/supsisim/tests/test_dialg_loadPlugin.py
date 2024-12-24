import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication


"""
Unit Tests for RTgenDlg Class

This file tests the `RTgenDlg` class, focusing on the `configureScript` method to handle `.tmf` templates
and their associated `.py` scripts.

    Mocks:
    ------
    Mocks are used extensively to isolate and test specific behaviors:
        - `os.path.isfile`: Simulates the presence or absence of `.py` files.
        - `run_plugin`: Simulates the behavior of the plugin execution, including handling cases where specific functions
          like `press_configure_button` may or may not exist.

    Tests:
    ------

    - `test_configureScript_with_valid_template`:            Ensures `run_plugin` is called when a valid `.tmf` template is set.
    - `test_configureScript_calls_press_configure_button`:   Validates that `press_configure_button` is executed if it exists.
    - `test_configureScript_without_press_configure_button`: Ensures the script runs globally if `press_configure_button` is not found.
    - `test_does_not_load_module_if_py_file_missing`:        Confirms no attempt to load a module if the `.py` file does not exist.

"""


# Adds the "pysimCoder" directory to the root of sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from toolbox.supsisim.supsisim.dialg import RTgenDlg

# Required to launch PyQt tests
app = QApplication([])

class TestRTgenDlg(unittest.TestCase):

    def setUp(self):
        self.dialog = RTgenDlg()

    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=True)
    @patch('toolbox.supsisim.supsisim.dialg.run_plugin')
    def test_configureScript_with_valid_template(self, mock_run_plugin, mock_isfile):

        """ Test configureScript with a valid template, ensuring run_plugin is called. """
        
        # Set a valid template name
        self.dialog.template.setText('test_template.tmf')

        self.dialog.configureScript()

        # Assert that run_plugin was called
        mock_run_plugin.assert_called_once_with(None, 'test_template.tmf', 'press_configure_button')


    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=True)
    @patch('toolbox.supsisim.supsisim.dialg.run_plugin')
    def test_configureScript_calls_press_configure_button(self, mock_run_plugin, mock_isfile):

        """ Test configureScript when the .py script contains `press_configure_button`. """

        # Set a valid template name
        self.dialog.template.setText('test_template.tmf')

        # Mock behavior for run_plugin to simulate presence of `press_configure_button`
        mock_function = MagicMock()
        mock_run_plugin.return_value = mock_function

        self.dialog.configureScript()

        # Assert that run_plugin was called
        mock_run_plugin.assert_called_once_with(None, 'test_template.tmf', 'press_configure_button')


    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=True)
    @patch('toolbox.supsisim.supsisim.dialg.run_plugin')
    def test_configureScript_without_press_configure_button(self, mock_run_plugin, mock_isfile):

        """ Test configureScript when the .py script does not contain `press_configure_button`. """

        # Set a valid template name
        self.dialog.template.setText('test_template.tmf')

        # Mock run_plugin to simulate the absence of `press_configure_button`
        def mock_run_plugin_side_effect(model, template_name, function_name):
            if function_name == 'press_configure_button':
                raise AttributeError("Mocked: Function 'press_configure_button' not found")

        mock_run_plugin.side_effect = mock_run_plugin_side_effect

        self.dialog.configureScript()

        # Verify that run_plugin was called twice:
        # - First with 'press_configure_button' (which raises AttributeError)
        # - Second with None (to execute the script globally)
        mock_run_plugin.assert_any_call(None, 'test_template.tmf', 'press_configure_button')
        mock_run_plugin.assert_any_call(None, 'test_template.tmf', None)

        # Ensure run_plugin was called exactly twice
        self.assertEqual(mock_run_plugin.call_count, 2)

    
    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=False)
    @patch('toolbox.supsisim.supsisim.dialg.load_module')
    def test_does_not_load_module_if_py_file_missing(self, mock_load_module, mock_isfile):

        """ Test that the module is not loaded if the .py file does not exist. """
        
        # Set the template name
        self.dialog.template.setText('nonexistent_template.tmf')

        self.dialog.configureScript()

        # Assert that load_module is never called
        mock_load_module.assert_not_called()


    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=False)
    @patch('toolbox.supsisim.supsisim.dialg.run_plugin')
    def test_does_not_load_module_if_py_file_missing(self, mock_run_plugin, mock_isfile):

        """ Test that run_plugin does not attempt to load a module if the .py file is missing. """
        
        # Set the template name where the associated .py script is missing
        self.dialog.template.setText('missing_template.tmf')

        self.dialog.configureScript()

        # Verify that run_plugin was called, but it immediately exited without invoking `load_module`
        mock_run_plugin.assert_called_once_with(None, 'missing_template.tmf', 'press_configure_button')

        # If `run_plugin` is mocked, and the .py file is missing, the mock should never attempt to load a module.
        self.assertFalse(mock_isfile.called, "os.path.isfile should not have been called for loading the module.")


if __name__ == '__main__':
    unittest.main()

