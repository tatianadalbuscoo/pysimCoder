
import os
import json
import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QDialog
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))
from delfino import open_config_window, ConfigWindow, open_project_config_window, ProjectConfigWindow


"""

    This test suite verifies the functionality of the graphical interface functions 
    `open_config_window` and `open_project_config_window` defined in delfino.py.

    It includes unit tests that use mocking to isolate and simulate user interactions 
    with graphical components, ensuring correctness and reliability without requiring a real graphical environment.

    The tests cover the following scenarios:
    - Initialization and behavior of `open_config_window`, ensuring it returns the correct results for accepted or rejected dialogs.
    - Collection and validation of configuration data from `open_project_config_window`, including edge cases for different user inputs.
    - Simulation of the dialog behavior (`Accepted` or `Rejected`) to verify both positive and negative outcomes.

    By simulating the graphical interface, this test suite provides robust validation of the core logic.

- Test open_config_window function:
    
    - test_open_config_window_accepted:         Verify that the `open_config_window` function correctly returns `True` when the dialog is accepted.
                                    
                                                Simulated Conditions:
                                                - The `QApplication` instance does not exist and needs to be created.
                                                - The `ConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).

    - test_open_config_window_rejected:         Verify that the `open_config_window` function correctly returns `False` when the dialog is rejected.
    
                                                Simulated Conditions:
                                                - The `QApplication` instance does not exist and needs to be created. Expected: A new instance of `QApplication` is initialized.
                                                - The `ConfigWindow` dialog is opened and the user rejects the dialog (`QDialog.Rejected`). Expected: The function returns `False`.

- Test open_project_config_window function:

    - test_open_project_config_window_state1:   Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 1 with Timer and valid period (state 1).
                                
                                                Simulated Conditions:
                                                - The `QApplication` instance does not exist and needs to be created.
                                                - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
                                                - The `mode_combo` widget is set to "1" (Mode 1).
                                                - The `peripheral_combo` widget is set to "Timer".
                                                - The `timer_period_input` widget contains "1000".
                                                - No ePWM options are selected for Mode 1.

    - test_open_project_config_window_state2:   Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 1 with ePWM output (State 2).

                                                Simulated Conditions:
                                                - The `QApplication` instance does not exist and needs to be created.
                                                - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
                                                - The `mode_combo` widget is set to "1" (Mode 1).
                                                - The `peripheral_combo` widget is set to "ePWM".
                                                - The `timer_period_input` widget is empty.
                                                - The `epwm_output_combo_mode1` widget is set to "out1a".
                                                - No output is selected for Mode 2.

    - test_open_project_config_window_state3:   Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 2 with Timer and valid period (State 3).

                                                Simulated Conditions:
                                                - The `QApplication` instance does not exist and needs to be created.
                                                - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
                                                - The `mode_combo` widget is set to "2" (Mode 2).
                                                - The `trigger_adc_combo` widget is set to "Timer".
                                                - The `timer_period_input` widget contains "2000".
                                                - No peripheral is selected for Mode 1.
                                                - No ePWM output is selected for Mode 2.

    - test_open_project_config_window_state4:   Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 2 with ePWM output (State 4).

                                                Simulated Conditions:
                                                - The `QApplication` instance does not exist and needs to be created.
                                                - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
                                                - The `mode_combo` widget is set to "2" (Mode 2).
                                                - The `trigger_adc_combo` widget is set to "ePWM".
                                                - The `timer_period_input` widget is empty.
                                                - No peripheral is selected for Mode 1.
                                                - The `epwm_output_combo_mode2` widget is set to "out2b".
                                                - No ePWM output is selected for Mode 1.

    - test_open_project_config_window_rejected: Verify that the `open_project_config_window` function correctly returns `None` when the dialog is rejected.

                                                Simulated Conditions:
                                                - The `QApplication` instance does not exist and needs to be created.
                                                - The `ProjectConfigWindow` dialog is opened and the user rejects the dialog (`QDialog.Rejected`).

"""


#################################################################################################################################################
# Test open_config_window function
#################################################################################################################################################

class TestOpenConfigWindow(unittest.TestCase):


    @patch("delfino.QApplication")
    @patch("delfino.ConfigWindow")
    def test_open_config_window_accepted(self, mock_config_window_class, mock_qapplication_class):

        """

        Verify that the `open_config_window` function correctly returns `True` when the dialog is accepted.

        Simulated Conditions:
        - The `QApplication` instance does not exist and needs to be created.
        - The `ConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).

        """

        # Mock QApplication instance
        mock_qapplication_instance = MagicMock()
        mock_qapplication_class.instance.return_value = None  # Simulate no existing QApplication
        mock_qapplication_class.return_value = mock_qapplication_instance

        # Mock ConfigWindow instance
        mock_config_window_instance = MagicMock()
        mock_config_window_instance.exec.return_value = QDialog.Accepted
        mock_config_window_class.return_value = mock_config_window_instance

        result = open_config_window()

        # Ensure QApplication was created. Expected: QApplication is created once.
        mock_qapplication_class.assert_called_once()

        # Ensure ConfigWindow was created. Expected: ConfigWindow is instantiated once.
        mock_config_window_class.assert_called_once()

        # Ensure exec was called. Expected: The exec method of ConfigWindow is called once.
        mock_config_window_instance.exec.assert_called_once()

        # Ensure result is True for QDialog.Accepted. Expected: The function returns True when the dialog is accepted.
        self.assertTrue(result)


    @patch("delfino.QApplication")
    @patch("delfino.ConfigWindow")
    def test_open_config_window_rejected(self, mock_config_window_class, mock_qapplication_class):

        """

        Verify that the `open_config_window` function correctly returns `False` when the dialog is rejected.

        Simulated Conditions:
        - The `QApplication` instance does not exist and needs to be created. Expected: A new instance of `QApplication` is initialized.
        - The `ConfigWindow` dialog is opened and the user rejects the dialog (`QDialog.Rejected`). Expected: The function returns `False`.

        """

        # Mock QApplication instance
        mock_qapplication_instance = MagicMock()
        mock_qapplication_class.instance.return_value = None  # Simulate no existing QApplication
        mock_qapplication_class.return_value = mock_qapplication_instance

        # Mock ConfigWindow instance
        mock_config_window_instance = MagicMock()
        mock_config_window_instance.exec.return_value = QDialog.Rejected
        mock_config_window_class.return_value = mock_config_window_instance

        result = open_config_window()

        # Ensure QApplication was created. Expected: QApplication is created once.
        mock_qapplication_class.assert_called_once()

        # Ensure ConfigWindow was created. Expected: ConfigWindow is instantiated once.
        mock_config_window_class.assert_called_once()

        # Ensure exec was called. Expected: The exec method of ConfigWindow is called once.
        mock_config_window_instance.exec.assert_called_once()

        # Ensure result is False for QDialog.Rejected. Expected: The function returns False when the dialog is rejected.
        self.assertFalse(result)


#################################################################################################################################################
# Test open_project_config_window function
#################################################################################################################################################

class TestOpenProjectConfigWindow(unittest.TestCase):


    # State 1
    @patch("delfino.QApplication")
    @patch("delfino.ProjectConfigWindow")
    def test_open_project_config_window_state1(self, mock_project_config_window_class, mock_qapplication_class):

        """

            Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 1 with Timer and valid period (state 1).

            Simulated Conditions:
            - The `QApplication` instance does not exist and needs to be created.
            - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
            - The `mode_combo` widget is set to "1" (Mode 1).
            - The `peripheral_combo` widget is set to "Timer".
            - The `timer_period_input` widget contains "1000".
            - No ePWM options are selected for Mode 1.

        """

        # Mock QApplication instance
        mock_qapplication_instance = MagicMock()
        mock_qapplication_class.instance.return_value = None  # Simulate no existing QApplication
        mock_qapplication_class.return_value = mock_qapplication_instance

        # Mock ProjectConfigWindow instance for State 1
        mock_project_config_window_instance = MagicMock()
        mock_project_config_window_instance.exec.return_value = QDialog.Accepted
        mock_project_config_window_instance.mode_combo.currentText.return_value = "1"
        mock_project_config_window_instance.peripheral_combo.currentText.return_value = "Timer"
        mock_project_config_window_instance.timer_period_input.text.return_value = "1000"
        mock_project_config_window_instance.epwm_output_combo_mode1.currentText.return_value = None
        mock_project_config_window_class.return_value = mock_project_config_window_instance

        model = "test_model"
        result = open_project_config_window(model)

        # Verify that the returned configuration matches the expected values for State 1
        expected_config = {
            "mode": "1",
            "peripheral": "Timer",
            "trigger_adc": None,
            "timer_period": "1000",
            "epwm_output_mode1": None,
            "epwm_output_mode2": None,
        }
        self.assertEqual(result, expected_config)


    # State 2
    @patch("delfino.QApplication")
    @patch("delfino.ProjectConfigWindow")
    def test_open_project_config_window_state2(self, mock_project_config_window_class, mock_qapplication_class):

        """

        Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 1 with ePWM output (State 2).

        Simulated Conditions:
        - The `QApplication` instance does not exist and needs to be created.
        - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
        - The `mode_combo` widget is set to "1" (Mode 1).
        - The `peripheral_combo` widget is set to "ePWM".
        - The `timer_period_input` widget is empty.
        - The `epwm_output_combo_mode1` widget is set to "out1a".
        - No output is selected for Mode 2.

        """

        # Mock QApplication instance
        mock_qapplication_instance = MagicMock()
        mock_qapplication_class.instance.return_value = None
        mock_qapplication_class.return_value = mock_qapplication_instance

        # Mock ProjectConfigWindow instance for State 2
        mock_project_config_window_instance = MagicMock()
        mock_project_config_window_instance.exec.return_value = QDialog.Accepted
        mock_project_config_window_instance.mode_combo.currentText.return_value = "1"
        mock_project_config_window_instance.peripheral_combo.currentText.return_value = "ePWM"
        mock_project_config_window_instance.timer_period_input.text.return_value = ""
        mock_project_config_window_instance.epwm_output_combo_mode1.currentText.return_value = "out1a"
        mock_project_config_window_class.return_value = mock_project_config_window_instance

        model = "test_model"
        result = open_project_config_window(model)

        # Verify that the returned configuration matches the expected values for State 2
        expected_config = {
            "mode": "1",
            "peripheral": "ePWM",
            "trigger_adc": None,
            "timer_period": None,
            "epwm_output_mode1": "out1a",
            "epwm_output_mode2": None,
        }
        self.assertEqual(result, expected_config)


    # State 3
    @patch("delfino.QApplication")
    @patch("delfino.ProjectConfigWindow")
    def test_open_project_config_window_state3(self, mock_project_config_window_class, mock_qapplication_class):

        """

        Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 2 with Timer and valid period (State 3).

        Simulated Conditions:
        - The `QApplication` instance does not exist and needs to be created.
        - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
        - The `mode_combo` widget is set to "2" (Mode 2).
        - The `trigger_adc_combo` widget is set to "Timer".
        - The `timer_period_input` widget contains "2000".
        - No peripheral is selected for Mode 1.
        - No ePWM output is selected for Mode 2.

        """

        # Mock QApplication instance
        mock_qapplication_instance = MagicMock()
        mock_qapplication_class.instance.return_value = None
        mock_qapplication_class.return_value = mock_qapplication_instance

        # Mock ProjectConfigWindow instance for State 3
        mock_project_config_window_instance = MagicMock()
        mock_project_config_window_instance.exec.return_value = QDialog.Accepted
        mock_project_config_window_instance.mode_combo.currentText.return_value = "2"
        mock_project_config_window_instance.trigger_adc_combo.currentText.return_value = "Timer"
        mock_project_config_window_instance.timer_period_input.text.return_value = "2000"
        mock_project_config_window_instance.epwm_output_combo_mode2.currentText.return_value = None
        mock_project_config_window_class.return_value = mock_project_config_window_instance

        model = "test_model"
        result = open_project_config_window(model)

        # Verify that the returned configuration matches the expected values for State 3
        expected_config = {
            "mode": "2",
            "peripheral": None,
            "trigger_adc": "Timer",
            "timer_period": "2000",
            "epwm_output_mode1": None,
            "epwm_output_mode2": None,
        }
        self.assertEqual(result, expected_config)


    # State 4
    @patch("delfino.QApplication")
    @patch("delfino.ProjectConfigWindow")
    def test_open_project_config_window_state4(self, mock_project_config_window_class, mock_qapplication_class):

        """

        Verify that the `open_project_config_window` function correctly returns the expected configuration data for Mode 2 with ePWM output (State 4).

        Simulated Conditions:
        - The `QApplication` instance does not exist and needs to be created.
        - The `ProjectConfigWindow` dialog is opened and the user accepts the dialog (`QDialog.Accepted`).
        - The `mode_combo` widget is set to "2" (Mode 2).
        - The `trigger_adc_combo` widget is set to "ePWM".
        - The `timer_period_input` widget is empty.
        - No peripheral is selected for Mode 1.
        - The `epwm_output_combo_mode2` widget is set to "out2b".
        - No ePWM output is selected for Mode 1.

        """

        # Mock QApplication instance
        mock_qapplication_instance = MagicMock()
        mock_qapplication_class.instance.return_value = None
        mock_qapplication_class.return_value = mock_qapplication_instance

        # Mock ProjectConfigWindow instance for State 4
        mock_project_config_window_instance = MagicMock()
        mock_project_config_window_instance.exec.return_value = QDialog.Accepted
        mock_project_config_window_instance.mode_combo.currentText.return_value = "2"
        mock_project_config_window_instance.trigger_adc_combo.currentText.return_value = "ePWM"
        mock_project_config_window_instance.timer_period_input.text.return_value = ""
        mock_project_config_window_instance.epwm_output_combo_mode2.currentText.return_value = "out2b"
        mock_project_config_window_class.return_value = mock_project_config_window_instance

        # Call the function under test
        model = "test_model"
        result = open_project_config_window(model)

        # Verify that the returned configuration matches the expected values for State 4
        expected_config = {
            "mode": "2",
            "peripheral": None,
            "trigger_adc": "ePWM",
            "timer_period": None,
            "epwm_output_mode1": None,
            "epwm_output_mode2": "out2b",
        }
        self.assertEqual(result, expected_config)


    @patch("delfino.QApplication")
    @patch("delfino.ProjectConfigWindow")
    def test_open_project_config_window_rejected(self, mock_project_config_window_class, mock_qapplication_class):

        """

        Verify that the `open_project_config_window` function correctly returns `None` when the dialog is rejected.

        Simulated Conditions:
        - The `QApplication` instance does not exist and needs to be created.
        - The `ProjectConfigWindow` dialog is opened and the user rejects the dialog (`QDialog.Rejected`).

        """

        mock_qapplication_instance = MagicMock()
        mock_qapplication_class.instance.return_value = None
        mock_qapplication_class.return_value = mock_qapplication_instance

        mock_project_config_window_instance = MagicMock()
        mock_project_config_window_instance.exec.return_value = QDialog.Rejected
        mock_project_config_window_class.return_value = mock_project_config_window_instance

        model = "test_model"
        result = open_project_config_window(model)

        # Ensure the function returns None for QDialog.Rejected
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

