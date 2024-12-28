
import os
import json
import sys
import unittest
from io import StringIO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))
from delfino import ConfigFile


"""

This test suite verifies the functionality of the ConfigFile class from delfino.py. 
It includes unit tests to validate individual methods in isolation, ensuring correctness and reliability. 
The tests cover initialization, file operations, and string representation, simulating various conditions to ensure robust validation and handle edge cases effectively. 
   
- Test ConfigFile class: 

    - test_initialization:        Verify that the `ConfigFile` class is initialized correctly.
                                  Simulated Condition: A `ConfigFile` object is initialized with a name ("test_config") and an extension ("json").
    
    - test_get_name:              Verify that the `get_name` method returns the correct file name with or without the extension based on the input parameter.
                                  Simulated Condition: A `ConfigFile` object is initialized with a name ("test_config") and an extension ("json").

    - test_exists:                Verify that the `exists` method correctly checks the presence of the configuration file.

                                  Simulated Conditions:
                                  - When the configuration file exists.
                                  - When the configuration file does not exist.
    
    - test_load:                  Verify that the `load` method correctly loads the contents of the configuration file.
                                
                                  Simulated Conditions:
                                  - The file does not exist, so it should return an empty dictionary.
                                  - The file exists, and the method should return the correct content.

    - test_save:                  Verify that the save method correctly writes the provided data to the configuration file in JSON format.
                                  
                                  Simulated Conditions:
                                  - Uses a ConfigFile object already initialized during setUp.
                                  - Saves data to the configuration file.
                                  - Verifies that the file exists and its contents match the saved data.

    - test_delete:                Verify that the `delete` method correctly removes the configuration file if it exists.
                                            
                                  Simulated Conditions:
                                  - Ensure the file exists before calling `delete`.
                                  - Verify the file is removed after calling `delete`.

    - test_str:                  Verify that the __str__ method provides the correct textual representation.
    
                                 Simulated Conditions:
                                 - The ConfigFile object is initialized with a name and extension.
                                 - Verify that the string representation matches the expected format.

"""


#################################################################################################################################################
# Test ConfigFile class 
#################################################################################################################################################

class TestConfigFile(unittest.TestCase):


    def setUp(self):

        """

        Set up test environment. Creates a dummy configuration file.

        """

        # The name of the test configuration file (without extension)
        self.test_name = "test_config"

        # Specify the file extension for the configuration file
        self.test_extension = "json"

        # Combine the name and extension to form the full file path
        self.test_file = f"{self.test_name}.{self.test_extension}"

        # Example configuration data
        self.config_data = {"key1": "value1", "key2": "value2"}

        # This represents the configuration file that will be tested
        self.config_file = ConfigFile(self.test_name, self.test_extension)


    def tearDown(self):

        """

        Clean up test environment. Deletes any created test files.

        """

        # Check if the test file exists and delete it to clean up the environment
        if os.path.exists(self.test_file):
            os.remove(self.test_file)


    def test_initialization(self):

        """

        Verify that the `ConfigFile` class is initialized correctly.
        Simulated Condition: A `ConfigFile` object is initialized with a name ("test_config") and an extension ("json").

        """

        # Verify that the `name` attribute is correctly set to "test_config"
        self.assertEqual(self.config_file.name, self.test_name)

        # Verify that the `extension` attribute is correctly set to "json"
        self.assertEqual(self.config_file.extension, self.test_extension)

        # Verify that the `path` attribute is correctly constructed as "test_config.json"
        self.assertEqual(self.config_file.path, self.test_file)


    def test_get_name(self):

        """

        Verify that the `get_name` method returns the correct file name with or without the extension based on the input parameter.
        Simulated Condition: A `ConfigFile` object is initialized with a name ("test_config") and an extension ("json").

        """

        # Verify that the method returns the correct file name with extension. Expected: "test_config.json"
        self.assertEqual(self.config_file.get_name(with_extension=True), self.test_file)

        # Verify that the method returns the correct file name without extension. Expected: "test_config"
        self.assertEqual(self.config_file.get_name(with_extension=False), self.test_name)

    
    def test_exists(self):

        """

        Verify that the `exists` method correctly checks the presence of the configuration file.

        Simulated Conditions:
        - When the configuration file exists.
        - When the configuration file does not exist.

        """

        # Ensure the file does not exist initially
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.assertFalse(self.config_file.exists())  # Expected: False

        # Create the test file
        with open(self.test_file, "w") as file:
            file.write(json.dumps(self.config_data))

        # Check if the file now exists. Expected: True
        self.assertTrue(self.config_file.exists())

        if os.path.exists(self.test_file):
            os.remove(self.test_file)


    def test_load(self):

        """

        Verify that the `load` method correctly loads the contents of the configuration file.

        Simulated Conditions:
        - The file does not exist, so it should return an empty dictionary.
        - The file exists, and the method should return the correct content.

        """

        # Ensure the file does not exist initially
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        # Verify that the `load` method returns an empty dictionary when the file does not exist. Expected: {}
        self.assertEqual(self.config_file.load(), {}) 

        # Create the test file with sample content
        with open(self.test_file, "w") as file:
            json.dump(self.config_data, file)

        # Verify that the `load` method returns the correct content when the file exists. Expected: self.config_data
        self.assertEqual(self.config_file.load(), self.config_data) 

        if os.path.exists(self.test_file):
            os.remove(self.test_file)


    def test_save(self):

        """

        Verify that the save method correctly writes the provided data to the configuration file in JSON format.

        Simulated Conditions:
        - Uses a ConfigFile object already initialized during setUp.
        - Saves data to the configuration file.
        - Verifies that the file exists and its contents match the saved data.

        """

        # Ensure the file does not exist initially
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        # Save the test data using the `save` method
        self.config_file.save(self.config_data)

        # Verify that the file exists after saving. Expected: True
        self.assertTrue(os.path.exists(self.test_file))

        # Verify that the content of the file matches the data saved
        with open(self.test_file, "r") as file:
            saved_data = json.load(file)
        self.assertEqual(saved_data, self.config_data)  # Expected: self.config_data

    
    def test_delete(self):

        """

        Verify that the `delete` method correctly removes the configuration file if it exists.

        Simulated Conditions:
        - Ensure the file exists before calling `delete`.
        - Verify the file is removed after calling `delete`.

        """

        self.config_file.save(self.config_data)

        # Verify that the file exists before deletion. Expected: True
        self.assertTrue(os.path.exists(self.test_file))

        self.config_file.delete()

        # Verify that the file no longer exists after deletion. Expected: False
        self.assertFalse(os.path.exists(self.test_file))


    def test_str(self):

        """

        Verify that the __str__ method provides the correct textual representation.

        Simulated Conditions:
        - The ConfigFile object is initialized with a name and extension.
        - Verify that the string representation matches the expected format.

        """

        expected_str = f"ConfigFile(name={self.test_name}, path={self.test_file})"

        # Assert the string representation matches the expected format. Expected: "ConfigFile(name=test_config, path=test_config.json)"
        self.assertEqual(str(self.config_file), expected_str)


if __name__ == "__main__":
    unittest.main()
