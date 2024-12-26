
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch


"""
    
    Integration Tests for Plugin Execution

    These tests use a test.tmf template and a test.py plugin to verify the correct behavior of the run_plugin function, 
    ensuring proper module loading and execution of instructions. The following scenarios are tested:

    - test_run_plugin_output:             Verify that the `run_plugin` function correctly loads the module and executes the plugin, ensuring the proper execution of global-level instructions without calling any function.

                                          The test ensures that:
                                          - The module `test.py` is loaded correctly.
                                          - Only global-level instructions (print statements outside functions) are executed upon loading.

                                          Simulated Condition: Both `test.tmf` and `test.py` are accessible, and `test.py` contains a global instruction (e.g., a print statement) outside any function.
                                          Expected Output: "The test.py module was loaded successfully"
    
-  test_run_plugin_function_call:         Verify that the `run_plugin` function correctly loads the module and executes the plugin, ensuring the proper execution of global-level instructions without calling any function.

                                          The test ensures that:
                                          - The module `test.py` is loaded correctly.
                                          - The `test_function` within the module is executed as expected.

                                          Simulated Condition: Both `test.tmf` and `test.py` are accessible, and `test.py` contains a function named `test_function`.

                                          Expected Output: 
                                          - "The test.py module was loaded successfully"
                                          - "The test.py module was loaded successfully and the function test_function is called"

- test_run_plugin_nonexistent_function:  Verify that the `run_plugin` function handles the case where a specified function does not exist in the plugin.

                                         The test ensures that:
                                         - The module `test.py` is loaded correctly.
                                         - No exception is raised when attempting to call a non-existent function.
                                         - Global-level instructions (print statements outside functions) are still executed.

                                         Simulated Condition: Both `test.tmf` and `test.py` are accessible, and `test.py` does not contain a function named `nonexistent_function`.
                                         Expected Output: "The test.py module was loaded successfully"

"""


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'toolbox', 'supsisim', 'supsisim')))
from RCPgen import load_module, run_plugin

# Path to the directory where test.tmf and test.py are located
template_dir = os.path.join(os.environ.get('PYSUPSICTRL', ''), "CodeGen", "templates")


class TestPluginExecution(unittest.TestCase):

    def setUp(self):
        self.test_template = os.path.join(template_dir, "test.tmf")
        self.test_script = os.path.join(template_dir, "test.py")


    def test_run_plugin_output(self):

        """

        Verify that the `run_plugin` function correctly loads the module and executes the plugin, ensuring the proper execution of global-level instructions without calling any function.
        
        The test ensures that:
        - The module `test.py` is loaded correctly.
        - Only global-level instructions (print statements outside functions) are executed upon loading.

        Simulated Condition: Both `test.tmf` and `test.py` are accessible, and `test.py` contains a global instruction (e.g., a print statement) outside any function.
        Expected Output: "The test.py module was loaded successfully"

        """

        # Ensure template and script files exist
        self.assertTrue(os.path.exists(self.test_template), f"Template file {self.test_template} not found.")
        self.assertTrue(os.path.exists(self.test_script), f"Script file {self.test_script} not found.")

        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_plugin(model="test_model", template="test.tmf")
        
        output = mock_stdout.getvalue().strip()
        
        # Check the expected output
        self.assertIn("The test.py module was loaded successfully", output)


    def test_run_plugin_function_call(self):

        """

        Verify that the `run_plugin` function correctly loads the module and calls the specified function.

        The test ensures that:
        - The module `test.py` is loaded correctly.
        - The `test_function` within the module is executed as expected.

        Simulated Condition: Both `test.tmf` and `test.py` are accessible, and `test.py` contains a function named `test_function`.

        Expected Output: 
        - "The test.py module was loaded successfully"
        - "The test.py module was loaded successfully and the function test_function is called"

        """

        # Ensure template and script files exist
        self.assertTrue(os.path.exists(self.test_template), f"Template file {self.test_template} not found.")
        self.assertTrue(os.path.exists(self.test_script), f"Script file {self.test_script} not found.")

        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_plugin(model="test_model", template="test.tmf", function_name="test_function")
        
        output = mock_stdout.getvalue().strip()

        # Check the expected output
        self.assertIn("The test.py module was loaded successfully", output)
        self.assertIn("The test.py module was loaded successfully and the function test_function is called", output)


    def test_run_plugin_nonexistent_function(self):

        """

        Verify that the `run_plugin` function handles the case where a specified function does not exist in the plugin.

        The test ensures that:
        - The module `test.py` is loaded correctly.
        - No exception is raised when attempting to call a non-existent function.
        - Global-level instructions (print statements outside functions) are still executed.

        Simulated Condition: Both `test.tmf` and `test.py` are accessible, and `test.py` does not contain a function named `nonexistent_function`.
        Expected Output: "The test.py module was loaded successfully"

        """

        # Ensure template and script files exist
        self.assertTrue(os.path.exists(self.test_template), f"Template file {self.test_template} not found.")
        self.assertTrue(os.path.exists(self.test_script), f"Script file {self.test_script} not found.")

        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_plugin(model="test_model", template="test.tmf", function_name="nonexistent_function")
        
        output = mock_stdout.getvalue().strip()

        # Check the expected output
        self.assertIn("The test.py module was loaded successfully", output)

        # Verify that the string "The function nonexistent_function is called" is not present in the output
        self.assertNotIn("The function nonexistent_function is called", output)


if __name__ == "__main__":
    unittest.main()
