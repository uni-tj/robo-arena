from cx_Freeze import Executable, setup

setup(
    name="roboarena",
    version="0.1",
    packages=["roboarena"],
    include_package_data=True,
    executables=[Executable("src/roboarena/index.py")],
)
