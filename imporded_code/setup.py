import sys
import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = r'D:\software\Python\Anaconda3-5.1.0\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'D:\software\Python\Anaconda3-5.1.0\tcl\tk8.6'

# Dependencies are automatically detected, but it might need fine tuning.
options = {'packages': ["re","os","tkinter"]}

target = Executable(
        script="main.py",
        base="Win32GUI",
        icon="icon.ico"
)

setup(
        name="setup",
        version="1.0",
        description="the description",
    author="DuHua",
    options={"build_exe": options},
    executables=[target]
)
