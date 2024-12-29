
import os
import sys
import unittest
from unittest.mock import patch
from collections import namedtuple
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))

# Importing the entire delfino module to ensure that the global variable `isInWSL` retains its context when modified by the `check_wsl_environment` function
import delfino


"""

This file contains unit tests for various path conversion functions and the environment detection function
defined in the delfino.py file. The tests cover different scenarios to ensure correctness and robustness
of the `check_wsl_environment`, `convert_path_for_wsl`, and `convert_path_for_windows` functions.


- Test check_wsl_environment function:  

    - test_wsl_environment_detected:            Verify that `check_wsl_environment` correctly detects a WSL environment.
                                                Simulated Condition: The `os.uname().release` contains the substring 'microsoft'.

    - test_native_linux_environment:            Verify that `check_wsl_environment` correctly detects a native Linux environment.  
                                                Simulated Condition: The `os.uname().release` does not contain the substring 'microsoft'.

- Test convert_path_for_wsl function:

    - test_convert_windows_path_to_wsl:         Verify that a standard Windows path is correctly converted to a WSL-compatible path.
                                                Simulated Condition: The `isInWSL` global variable is set to `True`, indicating the environment is running in WSL.

    - test_convert_path_from_non_c_drive:       Verify that a Windows path from a non-C drive (e.g., D:) is correctly converted.
                                                Simulated Condition: The `isInWSL` global variable is set to `True`, indicating the environment is running in WSL.

    - test_convert_path_already_unix_format:    Verify that a Unix-style path remains unchanged.
                                                Simulated Condition: The `isInWSL` global variable is set to `True`, indicating the environment is running in WSL.

    - test_convert_path_not_in_wsl:             Verify that the path remains unchanged when not in a WSL environment.
                                                Simulated Condition: The `isInWSL` global variable is set to `False`, indicating the environment is not running in WSL.

    - test_empty_path:                          Verify that an empty path returns an empty string.
                                                Simulated Condition: The function is called with an empty string, which should return an empty string regardless of the environment.

- Test convert_path_for_windows function:

    - test_convert_wsl_to_windows_path:         Verify that a WSL path is correctly converted to a Windows-compatible path.
                                                Simulated Condition: The `isInWSL` global variable is set to `True`, and the input is a valid WSL path.

    - test_convert_non_wsl_path:                Verify that a non-WSL path remains unchanged.
                                                Simulated Condition: The `isInWSL` global variable is set to `True`, but the input path is not in WSL format.

    - test_not_in_wsl_environment:              Verify that the path remains unchanged when not in a WSL environment.
                                                Simulated Condition: The `isInWSL` global variable is set to `False`.

    - test_empty_path:                          Verify that an empty path returns an empty string.
                                                Simulated Condition: The function is called with an empty string.

    - test_convert_wsl_path_from_d_drive:       Verify that a WSL path from the D drive is correctly converted to a Windows-compatible path.  
                                                Simulated Condition: The `isInWSL` global variable is set to `True`, and the input path is located on the D drive.

"""


#################################################################################################################################################
# Test check_wsl_environment function 
#################################################################################################################################################

class TestCheckWSLEnvironment(unittest.TestCase):


    @patch('os.uname')
    def test_wsl_environment_detected(self, mock_uname):

        """

        Verify that `check_wsl_environment` correctly detects a WSL environment.
        Simulated Condition: The `os.uname().release` contains the substring 'microsoft'.

        """

        # Create a mock object similar to `os.uname_result`
        # Simulate the system environment as a WSL release
        UnameResult = namedtuple('UnameResult', ['sysname', 'nodename', 'release', 'version', 'machine'])
        mock_uname.return_value = UnameResult(
            sysname='Linux',                                # System name
            nodename='mock-node',                           # Node name
            release='5.4.72-microsoft-standard',            # Release containing 'microsoft' to mimic WSL
            version='#1 SMP Fri Oct 23 12:16:45 UTC 2020',  # Version details
            machine='x86_64'                                # Machine architecture
        )

        delfino.check_wsl_environment()

        # Verify that the global variable isInWSL is set to True, indicating WSL was detected. Expected: isInWSL = True
        self.assertTrue(delfino.isInWSL)


    @patch('os.uname')
    def test_native_linux_environment(self, mock_uname):

        """

        Verify that `check_wsl_environment` correctly detects a native Linux environment.
        Simulated Condition: The `os.uname().release` does not contain the substring 'microsoft'.

        """

        # Create a mock object similar to `os.uname_result`
        # This simulates a native Linux environment (not WSL).
        UnameResult = namedtuple('UnameResult', ['sysname', 'nodename', 'release', 'version', 'machine'])
        mock_uname.return_value = UnameResult(
            sysname='Linux',                                 # System name
            nodename='mock-node',                            # Node name
            release='5.4.72-generic',                        # A release name that does not indicate WSL
            version='#1 SMP Fri Oct 23 12:16:45 UTC 2020',   # Kernel version
            machine='x86_64'                                 # Machine architecture
        )

        delfino.check_wsl_environment()

        # Verify that the global variable isInWSL is set to False, indicating a native Linux environment was detected. Expected: isInWSL = False
        self.assertFalse(delfino.isInWSL)


#################################################################################################################################################
# Test convert_path_for_wsl function 
#################################################################################################################################################

class TestConvertPathForWSL(unittest.TestCase):


    @patch('delfino.isInWSL', True)  # Simulate running in WSL
    def test_convert_windows_path_to_wsl(self):

        """

        Verify that a standard Windows path is correctly converted to a WSL-compatible path.
        Simulated Condition: The `isInWSL` global variable is set to `True`, indicating the environment is running in WSL.

        """

        windows_path = "C:\\Users\\user\\path\\to\\file.c"
        expected_wsl_path = "/mnt/c/Users/user/path/to/file.c"

        # Expected: "/mnt/c/Users/user/path/to/file.c"
        self.assertEqual(delfino.convert_path_for_wsl(windows_path), expected_wsl_path)


    @patch('delfino.isInWSL', True)  # Simulate running in WSL
    def test_convert_path_from_non_c_drive(self):

        """

        Verify that a Windows path from a non-C drive (e.g., D:) is correctly converted.
        Simulated Condition: The `isInWSL` global variable is set to `True`, indicating the environment is running in WSL.

        """

        windows_path = "D:\\Projects\\test\\code.py"
        expected_wsl_path = "/mnt/d/Projects/test/code.py"

        # Expected: "/mnt/d/Projects/test/code.py"
        self.assertEqual(delfino.convert_path_for_wsl(windows_path), expected_wsl_path)


    @patch('delfino.isInWSL', True)  # Simulate running in WSL
    def test_convert_path_already_unix_format(self):

        """

        Verify that a Unix-style path remains unchanged.
        Simulated Condition: The `isInWSL` global variable is set to `True`, indicating the environment is running in WSL.

        """

        unix_path = "/mnt/c/Users/user/path/to/file.c"

        # Expected: "/mnt/c/Users/user/path/to/file.c"
        self.assertEqual(delfino.convert_path_for_wsl(unix_path), unix_path)


    @patch('delfino.isInWSL', False)  # Simulate not running in WSL
    def test_convert_path_not_in_wsl(self):

        """

        Verify that the path remains unchanged when not in a WSL environment.
        Simulated Condition: The `isInWSL` global variable is set to `False`, indicating the environment is not running in WSL.

        """

        windows_path = "C:\\Users\\user\\path\\to\\file.c"

        # Expected: "C:\\Users\\user\\path\\to\\file.c"
        self.assertEqual(delfino.convert_path_for_wsl(windows_path), windows_path)


    def test_empty_path(self):

        """

        Verify that an empty path returns an empty string.
        Simulated Condition: The function is called with an empty string, which should return an empty string regardless of the environment.

        """

        empty_path = ""

        # Expected: ""
        self.assertEqual(delfino.convert_path_for_wsl(empty_path), "")


#################################################################################################################################################
# Test convert_path_for_windows function 
#################################################################################################################################################

class TestConvertPathForWindows(unittest.TestCase):


    @patch('delfino.isInWSL', True)  # Simulate running in WSL
    def test_convert_wsl_to_windows_path(self):

        """

        Verify that a WSL path is correctly converted to a Windows-compatible path.
        Simulated Condition: The `isInWSL` global variable is set to `True`, and the input is a valid WSL path.

        """

        wsl_path = "/mnt/c/Users/user/path/to/file.c"
        expected_windows_path = "C:/Users/user/path/to/file.c"

        # Expected: "C:/Users/user/path/to/file.c"
        self.assertEqual(delfino.convert_path_for_windows(wsl_path), expected_windows_path)


    @patch('delfino.isInWSL', True)  # Simulate running in WSL
    def test_convert_non_wsl_path(self):
        
        """

        Verify that a non-WSL path remains unchanged.
        Simulated Condition: The `isInWSL` global variable is set to `True`, but the input path is not in WSL format.

        """

        non_wsl_path = "/home/user/documents/file.c"

        # Expected: "/home/user/documents/file.c"
        self.assertEqual(delfino.convert_path_for_windows(non_wsl_path), non_wsl_path)


    @patch('delfino.isInWSL', False)  # Simulate not running in WSL
    def test_not_in_wsl_environment(self):

        """

        Verify that the path remains unchanged when not in a WSL environment.
        Simulated Condition: The `isInWSL` global variable is set to `False`.

        """
        wsl_path = "/mnt/c/Users/user/path/to/file.c"

        # Expected: "/mnt/c/Users/user/path/to/file.c"
        self.assertEqual(delfino.convert_path_for_windows(wsl_path), wsl_path)


    def test_empty_path(self):

        """

        Verify that an empty path returns an empty string.
        Simulated Condition: The function is called with an empty string.

        """
        empty_path = ""

        # Expected: ""
        self.assertEqual(delfino.convert_path_for_windows(empty_path), "")


    @patch('delfino.isInWSL', True)  # Simulate running in WSL
    def test_convert_wsl_path_from_d_drive(self):

        """

        Verify that a WSL path from the D drive is correctly converted to a Windows-compatible path.  
        Simulated Condition: The `isInWSL` global variable is set to `True`, and the input path is located on the D drive.

        """

        wsl_path = "/mnt/d/Projects/Development/Code/file.py"
        expected_windows_path = "D:/Projects/Development/Code/file.py"

        # Expected: "D:/Projects/Development/Code/file.py"
        self.assertEqual(delfino.convert_path_for_windows(wsl_path), expected_windows_path)


if __name__ == "__main__":
    unittest.main()
