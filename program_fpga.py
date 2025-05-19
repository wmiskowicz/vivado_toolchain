# Author: Wojciech Miskowicz
#
# Description:
# Based on work of Piotr Kaczmarczyk, PhD, AGH University of Krakow.
# Load a bitstream to a Xilinx FPGA using Vivado in tcl mode.

import os
import glob
import subprocess
import sys
import colorama

from setup import VIVADO_DIR, PROJECT_DIR

colorama.init(autoreset=True)

vivado_bin = os.path.join(VIVADO_DIR, "bin")
os.environ["PATH"] = vivado_bin + os.pathsep + os.environ["PATH"]


bitstream_files = glob.glob(os.path.join(PROJECT_DIR, "results", "*.bit"))

if not bitstream_files:
    print(colorama.Fore.RED + "Error: No .bit file found in the results directory.")
    sys.exit(1)

bitstream_file = bitstream_files[0] 
tcl_script = os.path.join(PROJECT_DIR, "fpga", "scripts", "program_fpga.tcl")


command = f'{VIVADO_DIR}/vivado.bat -mode tcl -source "{tcl_script}" -tclargs "{bitstream_file}"'
subprocess.run(command, shell=True)

print(colorama.Fore.GREEN + f"Bitstream {bitstream_file} programmed successfully.")
