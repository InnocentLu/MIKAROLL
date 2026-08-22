import os
import sys
import subprocess
from PyInstaller.__main__ import run

def build():
    print(">>> Starting automated PyInstaller modern onedir pipeline...")
    
    # 1. Locate Conda DLLs
    conda_base = sys.prefix
    bin_dir = os.path.join(conda_base, "Library", "bin")
    
    tcl_dll = "tcl86t.dll"
    tk_dll = "tk86t.dll"
    tcl_data = "tcl8.6"
    tk_data = "tk8.6"
    
    extra_binaries = []
    
    if not os.path.exists(os.path.join(bin_dir, tcl_dll)):
        tcl_dll = "tcl90.dll"
        tk_dll = "tcl9tk90.dll"
        tcl_data = "tcl9.0"
        tk_data = "tk9.0"
        
        tommath = os.path.join(bin_dir, "libtommath.dll")
        if os.path.exists(tommath):
            extra_binaries.append(f'--add-binary={tommath};.')
        
    tcl_dll_path = os.path.join(bin_dir, tcl_dll)
    tk_dll_path = os.path.join(bin_dir, tk_dll)
    
    print(f">>> Found Tcl DLL: {tcl_dll_path}")
    print(f">>> Found Tk DLL: {tk_dll_path}")

    # Create a spec file manually or pass args
    args = [
        'main.py',
        '--name=MikaRoll',
        '--onedir',          # Modern onedir pipeline
        '--windowed',        # No console
        '--noconfirm',       # Overwrite output
        '--clean',           # Clean cache
        '--icon=image/icon.ico',
        # Data and hidden imports
        '--collect-data=tkinterdnd2',
        '--collect-data=customtkinter',
        '--collect-data=reportlab',
        '--collect-data=playwright',
        '--hidden-import=playwright',
        '--hidden-import=comtypes',
        '--hidden-import=reportlab',
        # Tcl/Tk data
        f'--add-data={os.path.join(conda_base, "Library", "lib", tcl_data)};tcl/{tcl_data}',
        f'--add-data={os.path.join(conda_base, "Library", "lib", tk_data)};tcl/{tk_data}',
        '--add-data=image;image',
        # Tcl/Tk binaries
        f'--add-binary={tcl_dll_path};.',
        f'--add-binary={tk_dll_path};.',
        # Disable UPX and use optimize=2
        '--noupx',
    ] + extra_binaries

    os.environ['PYTHONOPTIMIZE'] = '2'
    print(f">>> Running PyInstaller with args: {args}")
    run(args)
    
    print(">>> PyInstaller Build Complete!")

if __name__ == '__main__':
    build()
