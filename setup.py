"""
    Writes a settings.py file to every module in the project
       - Input is from settings.txt
       -   Contains project dirs that need to be set
           (and possibly reset later)
"""

import os

# List of modules that require settings files
modules = ["tests", "corpus", "data", "tests", "classifiers", "tfIdf"]
root_dir = os.getcwd()

for module in modules:
    module_dir = os.path.join(root_dir, module)
    # Checks if the module exists
    if os.path.exists(module_dir):
        settings = os.path.join(root_dir, module, "settings.py")
        with open("settings.txt", "r") as proj_settings:
            with open(settings, "w") as mod_settings:
                for ps in proj_settings.readlines():
                    mod_settings.write(ps)
