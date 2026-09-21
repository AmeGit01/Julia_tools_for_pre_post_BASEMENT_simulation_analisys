#!/usr/bin/env python

import os
import shutil
from pathlib import Path

def get_source_directory():
    # DEFAULT PATH 
    default_path = Path("/home/amedeo/Documents/Julia_tools_for_pre_post_BASEMENT_simulation_analisys")
    
    print(f"📂 Default script storage path:\n   {default_path}")
    
    # Ask for user confirmation
    user_input = input("Is the path correct? [Press ENTER to confirm, or enter a new path]: ").strip()
    
    if not user_input:
        # If the user presses only Enter, use the default path
        return default_path
    else:
        # If the user entered a new path, convert it handling the OS correctly
        # (using Path automatically handles \ or / separators depending on Windows/Linux)
        return Path(user_input)
    
def initialize_project():
    # 1. Define the fixed folder structure of your project
    directories = [
        "inputs",
        "outputs",
        "outputs/figures",
        "outputs/reports",
        "py_src",
        "src"
    ]
    
    # Get the current folder where the script is executed
    current_dir = Path.cwd()
    print(f"🚀 Initializing project in: {current_dir}\n")

    # 2. Copy updated scripts from your central repository
    jl_scripts = "src"
    py_scripts = "py_src"
    source_scripts_dir = get_source_directory()
    source_scripts_dir_jl = source_scripts_dir / jl_scripts
    source_scripts_dir_py = source_scripts_dir / py_scripts
    dest_scripts_dir_jl = current_dir / jl_scripts
    dest_scripts_dir_py = current_dir / py_scripts
    
    # 3. Create the folders
    for dir_path in directories:
        full_path = current_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created folder: {dir_path}")

    if source_scripts_dir_py.exists():
        print("\nCopying updated scripts...")
        for script_file in source_scripts_dir_py.glob("*.py"):          
            if script_file.name == "Julia_tool_initializer.py":
                continue
            shutil.copy(script_file, dest_scripts_dir_py)
            print(f"   ↳ Copied: {script_file.name}")
        print("\n✨ Project initialized and scripts updated successfully!")
    else:
        print(f"\n⚠️ Warning: Could not find the scripts folder at: {source_scripts_dir_py}")

    if source_scripts_dir_jl.exists():
        print("\nCopying updated scripts...")
        for script_file in source_scripts_dir_jl.glob("*.jl"):
            shutil.copy(script_file, dest_scripts_dir_jl)
            print(f"   ↳ Copied: {script_file.name}")
        print("\n✨ Project initialized and scripts updated successfully!")
    else:
        print(f"\n⚠️ Warning: Could not find the scripts folder at: {source_scripts_dir_jl}")


if __name__ == "__main__":
    initialize_project()