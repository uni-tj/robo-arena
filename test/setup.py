from setuptools import Extension, setup

import pybind11
from pybind11.setup_helpers import Pybind11Extension

ext_modules = [
    Pybind11Extension(
        "line_module",
        ["line_module.cpp"],
        # Any extra compile arguments can be added here
        extra_compile_args=["/std:c++17"],  # For MSVC
    ),
]

setup(
    name="line_module",
    version="0.1",
    ext_modules=ext_modules,
    zip_safe=False,
)
