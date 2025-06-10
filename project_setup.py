import os
from project_setup import *

PROJECT_NAME = "Saper_new"
TOP_MODULE   = "top_vga_basys3"
TARGET_FPGA  = "xc7a35tcpg236-1"

# -------------------------------------------------------------------------
# Search locations
# -------------------------------------------------------------------------
THIS_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR     = os.path.abspath(os.path.join(THIS_SCRIPT_DIR, ".."))
FPGA_DIR        = os.path.join(PROJECT_DIR, "fpga")

VIVADO_DIR=r"C:\Xilinx\Vivado\2023.1\bin"
VIVADO_SETUP=r"C:\Xilinx\Vivado\2023.1\settings64.bat"

FPGA_CONSTRAINTS_DIR = os.path.join(FPGA_DIR, "constraints")
FPGA_RTL_DIR         = os.path.join(FPGA_DIR, "rtl")
TOP_RTL_DIR          = os.path.join(PROJECT_DIR, "rtl")

MEM_INIT_DIR         = os.path.join(PROJECT_DIR, "rtl")

OUTPUT_TCL = os.path.join(FPGA_DIR, "scripts", "project_details.tcl")


