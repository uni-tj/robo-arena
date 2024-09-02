import os

import toml
from cx_Freeze import Executable, setup

# Load and parse the pyproject.toml file
with open("pyproject.toml", "r") as toml_file:
    pyproject_data = toml.load(toml_file)

# Extract information from pyproject.toml
project = pyproject_data["project"]
cx_freeze_options = pyproject_data.get("tool", {}).get("cx_freeze", {})

name = project["name"]
version = project["version"]
description = project.get("description", "")
packages = pyproject_data.get("tool", {}).get("setuptools", {}).get("packages", [])
package_dir = (
    pyproject_data.get("tool", {}).get("setuptools", {}).get("package-dir", {})
)
include_files = cx_freeze_options.get("include_files", [])

# Setup the cx_Freeze options
build_exe_options = {
    "packages": packages,
    "include_files": include_files,
}

# Create the executable
setup(
    name=name,
    version=version,
    description=description,
    options={"build_exe": build_exe_options},
    executables=[
        Executable(os.path.join(package_dir.get("", ""), "roboarena/index.py"))
    ],
)
