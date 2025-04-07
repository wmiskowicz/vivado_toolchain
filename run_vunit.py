import sys
from pathlib import Path
from vunit import VUnit

PROJECT_PATH = Path(__file__).resolve().parent.parent.as_posix()
VUNIT_PATH = r"C:\Users\wojte\AppData\Local\Programs\Python\Python312\Lib\site-packages\vunit\verilog"


def main(argv=None):
    if argv is None:
        vu = VUnit.from_argv(compile_builtins=False)
    else:
        vu = VUnit.from_argv(argv=argv, compile_builtins=False)

    
    unisim_files = [
        r"C:\Xilinx\Vivado\2023.1\data\vhdl\src\unisims\*.vhd",
        f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/unisims/secureip/*.vhd",
        f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/*.vhd",
    ]
    u_lib = vu.add_library("unisim", allow_duplicate=True)
    
    for file in unisim_files:
        u_lib.add_source_files(file, allow_empty=True)

        


    source_files = [
        # r"C:\Xilinx\Vivado\2023.1\data\vhdl\src\unisims\*.vhd",
        # f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/unisims/primitive/IBUF.vhd",
        # f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/unisims/primitive/BUFG.vhd",
        # f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/unisims/primitive/BUFGCE.vhd",
        # f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/unisims/primitive/BUFH.vhd",
        # f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/unisims/primitive/MMCME2_ADV.vhd",
        f"C:/Xilinx/Vivado/2023.1/data/vhdl/src/*.vhd",
        f"{VUNIT_PATH}/*.sv",
        f"{PROJECT_PATH}/fpga/rtl/import/*.vhd",
        f"{PROJECT_PATH}/sim/common/logger_pkg.sv",
        f"{PROJECT_PATH}/rtl/z_game_setup/defuser.sv",
        f"{PROJECT_PATH}/sim/defuser/defuser_vunit_tb.sv",
        f"{PROJECT_PATH}/fpga/rtl/*.sv",
        f"{PROJECT_PATH}/fpga/rtl/*.v",
        f"{PROJECT_PATH}/rtl/**/*.sv",
        f"{PROJECT_PATH}/rtl/**/*.v",
        f"{PROJECT_PATH}/rtl/**/*.vhd",
        f"{PROJECT_PATH}/sim/top_memory_logic/top_memory_logic_tb_vunit.sv"
    ]

    lib = vu.add_library("testbench_lib", allow_duplicate=True)

    for file in source_files:
        lib.add_source_files(file, allow_empty=True)
        # u_lib.add_source_files(file, allow_empty=True)

    # vu.add_compile_option("activehdl.vlog_flags", ["-dbg", "-work testbench_lib", "-v2k5", "-l unisim"])
    vu.main()

if __name__ == "__main__":
    main()