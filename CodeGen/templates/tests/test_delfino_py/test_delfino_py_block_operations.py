
import os
import sys
import unittest
import tempfile
import shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))
from delfino import check_blocks_list, check_blocks_set, find_and_copy_files, check_epwm_block, find_matching_pwm_output, extract_adc_parameters


"""

This script contains unit tests for the following functions from 'delfino.py':
- `check_blocks_list`
- `check_blocks_set`
- `find_and_copy_files`
- `check_epwm_block`
- `find_matching_pwm_output`
- `extract_adc_parameters`

It tests various functionalities including block analysis, file copying, PWM output matching, and ADC parameter extraction.


- Test check_blocks_list function:  

    - test_check_blocks_list:                           Test the check_blocks_list function with simulated input blocks.
                                                        Simulated Condition: A list of Block objects is provided as input, each with an 'fcn' attribute. 
                                                                             The test verifies the function's ability to return all 'fcn' values, including duplicates.

- Test check_blocks_set function: 

    - test_check_blocks_set:                            Test the check_blocks_set function with simulated input blocks.
                                                        Simulated Condition: A list of Block objects is provided as input, each with an 'fcn' attribute. 
                                                                             The test verifies the function's ability to return a unique set of 'fcn' values.

- Test find_and_copy_files function:

    - test_find_and_copy_files:                         Test the find_and_copy_files function with simulated input files.
                                                        Simulated Condition: A set of function names is provided, and corresponding
                                                                             source and header files are searched, copied, and returned.

- Test check_epwm_block function:

    - test_check_epwm_block_missing:                    Test the check_epwm_block function when 'epwmblk' is missing.
                                                        Simulated Condition: The input list of function names does not contain 'epwmblk'.

    - test_check_epwm_block_present:                    Test the check_epwm_block function when 'epwmblk' is present.
                                                        Simulated Condition: The input list of function names contains at least one 'epwmblk'.

    - test_check_epwm_block_multiple:                   Test the check_epwm_block function when 'epwmblk' appears multiple times.
                                                        Simulated Condition: The input list of function names contains multiple 'epwmblk' occurrences.

- Test find_matching_pwm_output function:

    - test_find_matching_pwm_output_found:              Test the find_matching_pwm_output function when a matching block is found.
                                                        Simulated Condition: A block with the target function and PWM output exists in the list.

    - test_find_matching_pwm_output_not_found:          Test the find_matching_pwm_output function when no matching block is found.
                                                        Simulated Condition: No block in the list matches the target function and PWM output.

    - test_find_matching_pwm_output_partial_match:      Test the find_matching_pwm_output function when only the target function matches, but not the PWM output.
                                                        Simulated Condition: A block with the target function exists, but its PWM output does not match.

    - test_find_matching_pwm_output_empty_list:         Test the find_matching_pwm_output function with an empty list of blocks.
                                                        Simulated Condition: The input list of blocks is empty. 

- Test extract_adc_parameters function:

    - test_extract_adc_parameters_single_match:         Test the extract_adc_parameters function with a single matching block.
                                                        Simulated Condition: One block matches the target function and has `generateInterrupt` set to 1.

    - test_extract_adc_parameters_no_match:             Test the extract_adc_parameters function when no matching blocks are found.
                                                        Simulated Condition: No block matches the target function or has `generateInterrupt` set to 1.

    - test_extract_adc_parameters_multiple_matches:     Test the extract_adc_parameters function with multiple matching blocks.
                                                        Simulated Condition: Multiple blocks match the target function and have `generateInterrupt` set to 1.

    - test_extract_adc_parameters_empty_list:           Test the extract_adc_parameters function with an empty list of blocks.
                                                        Simulated Condition: The input list of blocks is empty.

    - test_extract_adc_parameters_no_interrupt:         Test the extract_adc_parameters function when no blocks have `generateInterrupt` set to 1.
                                                        Simulated Condition: The input list contains ADC blocks, but none have `generateInterrupt` set to 1.

"""


class Block:

    """

    Class representing a block with specific attributes.

    """

    def __init__(self, dimPin, dimPout, fcn, intPar, intParNames, name, no_fcn_call, nx, pin, pout, realPar, realParNames, str_value, sysPath, uy):

        """

        Initialize a Block object with specified attributes.

            Parameters:
            -----------
            dimPin       : list -> Dimensions of input pins.
            dimPout      : list -> Dimensions of output pins.
            fcn          : str  -> Function associated with the block.
            intPar       : list -> Integer parameters for the block.
            intParNames  : list -> Names for the integer parameters.
            name         : str  -> Name of the block.
            no_fcn_call  : bool -> Whether the block has no function call.
            nx           : list -> State-related attributes.
            pin          : list -> Input pin indices.
            pout         : list -> Output pin indices.
            realPar      : list -> Real (floating-point) parameters for the block.
            realParNames : list -> Names for the real parameters.
            str_value    : str  -> A string value associated with the block.
            sysPath      : str  -> System path associated with the block.
            uy           : int  -> Output update status.

        """

        self.dimPin = dimPin
        self.dimPout = dimPout
        self.fcn = fcn
        self.intPar = intPar
        self.intParNames = intParNames
        self.name = name
        self.no_fcn_call = no_fcn_call
        self.nx = nx
        self.pin = pin
        self.pout = pout
        self.realPar = realPar
        self.realParNames = realParNames
        self.str = str_value
        self.sysPath = sysPath
        self.uy = uy


# Create a list of Block objects for testing purposes
blocks = [
    Block([], [1.0], "adcblk", [0, 0, 0], [], "ADC_0", False, [0, 0], [], [1], [], [], "A", "/ADC", 0),
    Block([], [1.0], "adcblk", [2, 10, 1], [], "ADC0_0", False, [0, 0], [], [2], [], [], "B", "/ADC0", 0),
    Block([], [1.0], "inputGPIOblk", [6], [], "GPIO_INPUT_1", False, [0, 0], [], [3], [], [], "", "/GPIO_INPUT", 0),
    Block([], [1.0], "inputGPIOblk", [7], [], "GPIO_INPUT0_2", False, [0, 0], [], [4], [], [], "", "/GPIO_INPUT0", 0),
    Block([], [1.0], "inputGPIOblk", [8], [], "GPIO_INPUT1_3", False, [0, 0], [], [5], [], [], "", "/GPIO_INPUT1", 0),
    Block([1.0], [], "epwmblk", [5000], [], "ePWM_4", False, [0, 0], [4], [], [], [], "out1a", "/ePWM", 0),
    Block([1.0], [], "epwmblk", [2500], [], "ePWM0_5", False, [0, 0], [3], [], [], [], "out2b", "/ePWM0", 0),
]


#################################################################################################################################################
# Test check_blocks_list function 
#################################################################################################################################################

class TestCheckBlocksList(unittest.TestCase):


    def test_check_blocks_list(self):

        """
        
        Test the check_blocks_list function with simulated input blocks.
        Simulated Condition: A list of Block objects is provided as input, each with an 'fcn' attribute. 
                             The test verifies the function's ability to return all 'fcn' values, including duplicates.
        
        """

        expected_result = ["adcblk", "adcblk", "inputGPIOblk", "inputGPIOblk", "inputGPIOblk", "epwmblk", "epwmblk"]
        result = check_blocks_list(blocks)

        # Verify that the result matches the expected list of 'fcn' values. Expected: A list of function names ('fcn' values) including duplicates.
        self.assertEqual(result, expected_result)


#################################################################################################################################################
# Test check_blocks_set function 
#################################################################################################################################################

class TestCheckBlocksSet(unittest.TestCase):


    def test_check_blocks_set(self):

        """
        
        Test the check_blocks_set function with simulated input blocks.
        Simulated Condition: A list of Block objects is provided as input, each with an 'fcn' attribute. 
                             The test verifies the function's ability to return a unique set of 'fcn' values.
        
        """

        expected_result = {"adcblk", "inputGPIOblk", "epwmblk"}
        result = check_blocks_set(blocks)

        # Verify that the result matches the expected set of unique 'fcn' values. Expected: A set of unique function names ('fcn' values).
        self.assertEqual(result, expected_result)


#################################################################################################################################################
# Test find_and_copy_files function 
#################################################################################################################################################

class TestFindAndCopyFiles(unittest.TestCase):

    def setUp(self):

        """

        Setup temporary directories and mock files for testing.

        """

        # Create temporary directories to simulate the CodeGen source directory and destination directories for .c and .h files.
        self.temp_codegen_dir = tempfile.mkdtemp()
        self.temp_dest_c_dir = tempfile.mkdtemp()
        self.temp_dest_h_dir = tempfile.mkdtemp()

        # Mock files to create in the CodeGen directory
        self.mock_files = {
            "adcblk.c": "adcblk content",
            "adc.c": "adc content",
            "adc.h": "adc header content",
            "inputGPIOblk.c": "inputGPIOblk content",
            "button.c": "button content",
            "button.h": "button header content",
        }

        # Write the mock files to the temporary CodeGen directory with specified content.
        for file_name, content in self.mock_files.items():
            with open(os.path.join(self.temp_codegen_dir, file_name), 'w') as f:
                f.write(content)


    def tearDown(self):

        """
        
        Cleanup temporary directories and files created for the test case.

        """

        shutil.rmtree(self.temp_codegen_dir)
        shutil.rmtree(self.temp_dest_c_dir)
        shutil.rmtree(self.temp_dest_h_dir)


    def test_find_and_copy_files(self):

        """

        Test the find_and_copy_files function with simulated input files.
        Simulated Condition: A set of function names is provided, and corresponding
                             source and header files are searched, copied, and returned.

        """

        function_names = {"adcblk", "inputGPIOblk"}
        expected_result = {
            "adcblk": {
                "c_files": [os.path.join(self.temp_dest_c_dir, "adcblk.c"), os.path.join(self.temp_dest_c_dir, "adc.c")],
                "h_files": [os.path.join(self.temp_dest_h_dir, "adc.h")]
            },
            "inputGPIOblk": {
                "c_files": [os.path.join(self.temp_dest_c_dir, "inputGPIOblk.c"), os.path.join(self.temp_dest_c_dir, "button.c")],
                "h_files": [os.path.join(self.temp_dest_h_dir, "button.h")]
            },
        }

        result = find_and_copy_files(function_names, self.temp_codegen_dir, self.temp_dest_c_dir, self.temp_dest_h_dir)

        # Verify results. Expected: The result should match the expected_result dictionary.
        self.assertEqual(result, expected_result)

        # Ensure files are copied
        for func, paths in expected_result.items():
            for file_path in paths["c_files"]:

                # Check if `.c` files are copied to the destination directory.
                # Expected: Each `.c` file listed in `expected_result["c_files"]` exists in the destination directory.
                self.assertTrue(os.path.exists(file_path), f"C file for {func} not copied!")
            for file_path in paths["h_files"]:

                # Check if `.h` files are copied to the destination directory.
                # Expected: Each `.h` file listed in `expected_result["h_files"]` exists in the destination directory.
                self.assertTrue(os.path.exists(file_path), f"H file for {func} not copied!")


#################################################################################################################################################
# Test check_epwm_block function 
#################################################################################################################################################

class TestCheckEpwmBlock(unittest.TestCase):
    

    def test_check_epwm_block_missing(self):

        """

        Test the check_epwm_block function when 'epwmblk' is missing.
        Simulated Condition: The input list of function names does not contain 'epwmblk'.

        """

        functions_present_schema = ["adcblk", "inputGPIOblk"]
        result = check_epwm_block(functions_present_schema)

        # Verify that the function should return 1 to indicate an error. Expected: 1 (Error, 'epwmblk' is missing)
        self.assertEqual(result, 1)


    def test_check_epwm_block_present(self):

        """

        Test the check_epwm_block function when 'epwmblk' is present.
        Simulated Condition: The input list of function names contains at least one 'epwmblk'.

        """

        functions_present_schema = ["adcblk", "epwmblk", "inputGPIOblk"]
        result = check_epwm_block(functions_present_schema)

        # Verify that the function should return 2 to indicate success. Expected: 2 (Success, 'epwmblk' is present at least once)
        self.assertEqual(result, 2)


    def test_check_epwm_block_multiple(self):

        """

        Test the check_epwm_block function when 'epwmblk' appears multiple times.
        Simulated Condition: The input list of function names contains multiple 'epwmblk' occurrences.

        """

        functions_present_schema = ["epwmblk", "adcblk", "epwmblk", "inputGPIOblk", "epwmblk"]
        result = check_epwm_block(functions_present_schema)

        # Verify that the function should still return 2 to indicate success. Expected: 2 (Success, 'epwmblk' is present at least once, even if multiple times)
        self.assertEqual(result, 2)


#################################################################################################################################################
# Test find_matching_pwm_output function 
#################################################################################################################################################

class TestFindMatchingPwmOutput(unittest.TestCase):


    def test_find_matching_pwm_output_found(self):

        """

        Test the find_matching_pwm_output function when a matching block is found.
        Simulated Condition: A block with the target function and PWM output exists in the list.

        """

        target_function = "epwmblk"
        epwm_output = "out1a"
        result = find_matching_pwm_output(blocks, target_function, epwm_output)

        expected_result = (5000, "out1a")

        # Verify that the function should return the block's first integer parameter and string parameter.
        # Expected: The first integer parameter (5000) and the string parameter ('out1a') of the matching block.
        self.assertEqual(result, expected_result)


    def test_find_matching_pwm_output_not_found(self):

        """

        Test the find_matching_pwm_output function when no matching block is found.
        Simulated Condition: No block in the list matches the target function and PWM output.

        """

        target_function = "epwmblk"
        epwm_output = "out3a"
        result = find_matching_pwm_output(blocks, target_function, epwm_output)

        # Verify that the function return (None, None) because no block matches the criteria. Expected: (None, None)
        self.assertEqual(result, (None, None))


    def test_find_matching_pwm_output_partial_match(self):

        """

        Test the find_matching_pwm_output function when only the target function matches, but not the PWM output.
        Simulated Condition: A block with the target function exists, but its PWM output does not match.

        """

        target_function = "epwmblk"
        epwm_output = "out2a"  # Output does not exist
        result = find_matching_pwm_output(blocks, target_function, epwm_output)

        # Verify that the function return (None, None) because no block matches the criteria. Expected: (None, None)
        self.assertEqual(result, (None, None))


    def test_find_matching_pwm_output_empty_list(self):

        """

        Test the find_matching_pwm_output function with an empty list of blocks.
        Simulated Condition: The input list of blocks is empty.

        """

        result = find_matching_pwm_output([], "epwmblk", "out1a")

        # Verify that the function return (None, None) because the list is empty. Expected: (None, None)
        self.assertEqual(result, (None, None))


#################################################################################################################################################
# Test extract_adc_parameters function 
#################################################################################################################################################

class TestExtractAdcParameters(unittest.TestCase):


    def test_extract_adc_parameters_single_match(self):

        """

        Test the extract_adc_parameters function with a single matching block.
        Simulated Condition: One block matches the target function and has `generateInterrupt` set to 1.

        """

        target_function = "adcblk"
        result = extract_adc_parameters(blocks, target_function)

        expected_result = {"module": "B", "soc": 10, "channel": 2}

        # Verify that the function returns the correct ADC parameters for the single matching block. Expected: result and expected_result = {"module": "B", "soc": 10, "channel": 2}
        self.assertEqual(result, expected_result)


    def test_extract_adc_parameters_no_match(self):

        """

        Test the extract_adc_parameters function when no matching blocks are found.
        Simulated Condition: No block matches the target function.

        """

        target_function = "nonexistent_function"
        result = extract_adc_parameters(blocks, target_function)

        # Verify that the function returns -1 because no matching blocks are found. Expected: -1
        self.assertEqual(result, -1)


    def test_extract_adc_parameters_multiple_matches(self):

        """

        Test the extract_adc_parameters function with multiple matching blocks.
        Simulated Condition: Multiple blocks match the target function and have `generateInterrupt` set to 1.

        """

        # Add a duplicate block to simulate multiple matches
        blocks_with_duplicates = blocks + [
            Block([], [1.0], "adcblk", [3, 15, 1], [], "ADC_1", False, [0, 0], [], [3], [], [], "C", "/ADC1", 0)
        ]

        target_function = "adcblk"
        result = extract_adc_parameters(blocks_with_duplicates, target_function)

        # Verify that the function returns -2 because multiple matching blocks are found. Expected: -2
        self.assertEqual(result, -2)


    def test_extract_adc_parameters_empty_list(self):

        """

        Test the extract_adc_parameters function with an empty list of blocks.
        Simulated Condition: The input list of blocks is empty.

        """

        result = extract_adc_parameters([], "adcblk")

        # Verify that the function returns -1 because no blocks are provided. Expected: -1
        self.assertEqual(result, -1)


    def test_extract_adc_parameters_no_interrupt(self):

            """

            Test the extract_adc_parameters function when no blocks have `generateInterrupt` set to 1.
            Simulated Condition: The input list contains ADC blocks, but none have `generateInterrupt` set to 1.

            """

            blocks_without_interrupt = [
                Block([], [1.0], "adcblk", [2, 1, 0], [], "ADC_1", False, [0, 0], [], [2], [], [], "B", "/ADC1", 0),
                Block([], [1.0], "adcblk", [3, 2, 0], [], "ADC_2", False, [0, 0], [], [3], [], [], "C", "/ADC2", 0)
            ]
            target_function = "adcblk"
            result = extract_adc_parameters(blocks_without_interrupt, target_function)

            # Verify that the function returns -1 because no ADC block has `generateInterrupt` set to 1. Expected: -1
            self.assertEqual(result, -1)


if __name__ == "__main__":
    unittest.main()
