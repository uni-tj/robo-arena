import os


def cls():
    """Clears the terminal (platform independent)"""
    os.system("cls" if os.name == "nt" else "clear")
