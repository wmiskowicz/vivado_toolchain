# Author: Wojciech Miskowicz
#
# Description:
# Based on work of Piotr Kaczmarczyk, PhD, AGH University of Krakow.
# Remove untracked files from the project.
# To work properly, a git repository in the project directory is required.
# Run from the project root directory.

import os
import subprocess
import sys
import colorama

from setup import PROJECT_DIR

# Run git clean -fdX to remove untracked files
try:
    subprocess.run(["git", "clean", "-fdX"], cwd=PROJECT_DIR, check=True)
    print(colorama.Fore.GREEN + "Untracked files removed successfully.")
except subprocess.CalledProcessError:
    print(colorama.Fore.RED + "Error: Failed to clean untracked files. Make sure this is a valid git repository.")
    sys.exit(1)
