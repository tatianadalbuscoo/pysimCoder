import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
import os

# Adds the "pysimCoder" directory to the root of sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from toolbox.supsisim.supsisim.dialg import RTgenDlg

# Required to launch PyQt tests
app = QApplication([])

class TestRTgenDlg(unittest.TestCase):
    
    def setUp(self):
        self.dialog = RTgenDlg()

    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=True)
    @patch('toolbox.supsisim.supsisim.dialg.load_module')
    def test_configureScript_with_valid_module(self, mock_load_module, mock_isfile):

        """ Test configureScript with a valid module containing `press_configure_button`."""

        mock_module = MagicMock()
        mock_module.press_configure_button = MagicMock()
        mock_load_module.return_value = mock_module

        # Set a template name that would simulate a valid .py script
        self.dialog.template.setText('test_template.tmf')

        # Call the function under test
        self.dialog.configureScript()

        # Assert that load_module was called with the correct path
        template_path = os.environ.get('PYSUPSICTRL')
        script_path = os.path.join(template_path, 'CodeGen/templates', 'test_template.py')
        mock_load_module.assert_called_once_with(script_path)

        # Assert that `press_configure_button` in the loaded module was called
        mock_module.press_configure_button.assert_called_once()


    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=False)
    def test_configureScript_with_nonexistent_script(self, mock_isfile):

        """ Test configureScript when the .py script does not exist."""

        self.dialog.template.setText('nonexistent_template.tmf')

        with patch('builtins.print') as mock_print:
            self.dialog.configureScript()
            template_path = os.environ.get('PYSUPSICTRL')
            mock_print.assert_called_once_with(
                f"Script path {os.path.join(template_path, 'CodeGen/templates', 'nonexistent_template.py')} does not exist."
            )

    @patch('toolbox.supsisim.supsisim.dialg.os.path.isfile', return_value=True)
    @patch('toolbox.supsisim.supsisim.dialg.load_module', return_value=None)  # Simulate failure to load module
    def test_configureScript_failed_module_load(self, mock_load_module, mock_isfile):

        """Test configureScript when the module fails to load."""

        self.dialog.template.setText('failed_load_template.tmf')

        with patch('builtins.print') as mock_print:
            self.dialog.configureScript()
            mock_print.assert_called_once_with("Failed to load the module.")

if __name__ == '__main__':
    unittest.main()
