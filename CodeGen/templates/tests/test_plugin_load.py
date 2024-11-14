import os
import sys

# Add "toolbox/supsisim/supsisim" directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'toolbox', 'supsisim', 'supsisim')))
from RCPgen import load_module

# Path to templates where test.tmf and test.py are located
template_dir = os.path.join(os.environ.get('PYSUPSICTRL', ''), "CodeGen", "templates")

def test_load_plugin():
    
    """ Test to verify loading of the plugin test.py corresponding to test.tmf. """

    test_template = os.path.join(template_dir, "test.tmf")
    test_script = os.path.join(template_dir, "test.py")

    # Check that the template file exists
    assert os.path.exists(test_template), f"File template {test_template} non trovato."

    # Check that the script file exists
    assert os.path.exists(test_script), f"File script {test_script} non trovato."

    module = load_module(test_script)
    
    # Check that the module has been loaded correctly
    assert module is not None, "Error loading test.py module."


if __name__ == "__main__":
    test_load_plugin()
