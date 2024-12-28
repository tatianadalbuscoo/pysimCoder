
import unittest
from unittest.mock import patch
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))
from delfino import update_paths

r"""

- Test Suite for the `update_paths` Function

This test suite verifies the functionality of the `update_paths` function defined in the delfino.py file. 
The testsare designed to simulate different scenarios and ensure that the function behaves as expected under varying conditions.
The test suite uses mocks, such as patching os.path.join, to simulate path concatenation with forward slashes and ensure consistent cross-platform behavior.

    
    - test_update_paths_ti_cgt_22_6_1:       Verify that the `update_paths` function correctly generates paths for the compiler version `ti-cgt-c2000_22.6.1.LTS`.    
        
                                             Simulated Conditions:
                                             - The `os.path.join` function is patched to simulate path concatenation with forward slashes.
                                             This is done to ensure consistent behavior across different operating systems
                                             (e.g., Windows uses `\` while Linux use `/`).
                                             - The `ti_path` is set to `C:/ti`, the root folder containing TI tools.
                                             - The `c2000_path` is set to `C:/ti/c2000/C2000Ware_4_01_00_00`, representing the location of the C2000Ware library.
                                             - The `compiler` is set to `ti-cgt-c2000_22.6.1.LTS`, indicating the desired compiler version.

    - test_update_paths_ti_cgt_21_6_0:       Verify that the `update_paths` function correctly generates paths for the compiler version `ti-cgt-c2000_21.6.0.LTS`.

                                             Simulated Conditions:
                                             - The `os.path.join` function is patched to simulate path concatenation with forward slashes.
                                             This is done to ensure consistent behavior across different operating systems
                                             (e.g., Windows uses `\` while Linux use `/`).
                                             - The `ti_path` is set to `C:/ti`, the root folder containing TI tools.
                                             - The `c2000_path` is set to `C:/ti/c2000/C2000Ware_4_01_00_00`, representing the location of the C2000Ware library.
                                             - The `compiler` is set to `ti-cgt-c2000_21.6.0.LTS`, indicating the desired compiler version.

    - test_update_paths_invalid_compiler:    Verify that the `update_paths` function correctly handles an invalid compiler version.

                                             Simulated Conditions:
                                             - The `ti_path` is set to `C:/ti`, representing the root directory for TI tools.
                                             - The `c2000_path` is set to `C:/ti/c2000/C2000Ware_4_01_00_00`, indicating the path to the C2000Ware library.
                                             - The `compiler` is set to an invalid value (`invalid-compiler-version`), which is not supported by the function.

"""


#################################################################################################################################################
# Test update_paths function
#################################################################################################################################################

class TestUpdatePaths(unittest.TestCase):


    @patch("os.path.join", side_effect=lambda *args: "/".join(args))
    def test_update_paths_ti_cgt_22_6_1(self, mock_path_join):

        r"""

        Verify that the `update_paths` function correctly generates paths for the compiler version `ti-cgt-c2000_22.6.1.LTS`.

        Simulated Conditions:
        - The `os.path.join` function is patched to simulate path concatenation with forward slashes.
        This is done to ensure consistent behavior across different operating systems
        (e.g., Windows uses `\` while Linux use `/`).
        - The `ti_path` is set to `C:/ti`, the root folder containing TI tools.
        - The `c2000_path` is set to `C:/ti/c2000/C2000Ware_4_01_00_00`, representing the location of the C2000Ware library.
        - The `compiler` is set to `ti-cgt-c2000_22.6.1.LTS`, indicating the desired compiler version.
        
        """

        # Inputs for the test
        ti_path = "C:/ti"
        c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"
        compiler = "ti-cgt-c2000_22.6.1.LTS"

        # Expected paths dictionary based on the inputs
        expected_paths = {
            "linker_path1": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd",
            "linker_path2": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd",
            "first_headers_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/include",
            "second_headers_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/include",

            # compiler dependent path
            "third_headers_path": "C:/ti/ccs1281/ccs/tools/compiler/ti-cgt-c2000_22.6.1.LTS/include",
            "first_source_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/source",
            "second_source_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source",
        }

        result = update_paths(ti_path, c2000_path, compiler)

        # Verify that the result matches the expected dictionary. Expected: expected_paths
        self.assertEqual(result, expected_paths)


    @patch("os.path.join", side_effect=lambda *args: "/".join(args))
    def test_update_paths_ti_cgt_21_6_0(self, mock_path_join):

        r"""

        Verify that the `update_paths` function correctly generates paths for the compiler version `ti-cgt-c2000_21.6.0.LTS`.

        Simulated Conditions:
        - The `os.path.join` function is patched to simulate path concatenation with forward slashes.
        This is done to ensure consistent behavior across different operating systems
        (e.g., Windows uses `\` while Linux use `/`).
        - The `ti_path` is set to `C:/ti`, the root folder containing TI tools.
        - The `c2000_path` is set to `C:/ti/c2000/C2000Ware_4_01_00_00`, representing the location of the C2000Ware library.
        - The `compiler` is set to `ti-cgt-c2000_21.6.0.LTS`, indicating the desired compiler version.
        
        """    

        # Inputs for the test
        ti_path = "C:/ti"
        c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"
        compiler = "ti-cgt-c2000_21.6.0.LTS"

        # Expected paths dictionary based on the inputs
        expected_paths = {
            "linker_path1": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/cmd/2837xD_RAM_lnk_cpu1.cmd",
            "linker_path2": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/cmd/F2837xD_Headers_nonBIOS_cpu1.cmd",
            "first_headers_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/include",
            "second_headers_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/include",

            # compiler dependent path
            "third_headers_path": "C:/ti/ccs1110/ccs/tools/compiler/ti-cgt-c2000_21.6.0.LTS/include",
            "first_source_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/headers/source",
            "second_source_path": "C:/ti/c2000/C2000Ware_4_01_00_00/device_support/f2837xd/common/source",
        }

        result = update_paths(ti_path, c2000_path, compiler)

        # Verify that the result matches the expected dictionary. Expected: expected_paths
        self.assertEqual(result, expected_paths)


    def test_update_paths_invalid_compiler(self):

        """

        Verify that the `update_paths` function correctly handles an invalid compiler version.

        Simulated Conditions:
        - The `ti_path` is set to `C:/ti`, representing the root directory for TI tools.
        - The `c2000_path` is set to `C:/ti/c2000/C2000Ware_4_01_00_00`, indicating the path to the C2000Ware library.
        - The `compiler` is set to an invalid value (`invalid-compiler-version`), which is not supported by the function.

        """

        ti_path = "C:/ti"
        c2000_path = "C:/ti/c2000/C2000Ware_4_01_00_00"
        compiler = "invalid-compiler-version"

        # verify that the function raises an `UnboundLocalError` when provided with an invalid compiler version.
        # The error occurs because `third_headers_path` is not initialized for the invalid compiler. Expected: UnboundLocalError
        with self.assertRaises(UnboundLocalError):
            update_paths(ti_path, c2000_path, compiler)


if __name__ == "__main__":
    unittest.main()
