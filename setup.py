from cx_Freeze import Executable, setup

setup(
    name="roboarena",
    version="0.1",
    description="RoboArena Game",
    executables=[
        Executable("src/roboarena/index.py")
    ],  # Update with the correct entry point
)
