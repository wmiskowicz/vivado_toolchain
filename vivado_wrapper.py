import subprocess
import os
import shutil
import sys
import colorama
import glob
import argparse
import re

from pathlib import Path
from datetime import datetime
from time import perf_counter

from project_setup import *
from internals.file_manager import FileManager


class VivadoWrapper:
    def __init__(self):
      
        self.file_manager = FileManager()
        
        self.TOOLS_DIR = Path(__file__).resolve().parent
        
        self.bitstream_files = None

    def generate_bitstream(self):

        if not os.path.exists(self.file_manager.VIVADO_EXE):
            print(colorama.Fore.RED + f"Error: Vivado executable not found at {self.file_manager.VIVADO_EXE}.")
            sys.exit(1)
        self.file_manager.update_project_details_tcl()

        subprocess.run(["git", "clean", "-fXd", "fpga"], cwd=PROJECT_DIR)

        # Generate bitstream
        gen_bit_tcl   = os.path.join(self.TOOLS_DIR, "scripts", "generate_bitstream.tcl")
        command    = f'"{self.file_manager.VIVADO_EXE}" -mode tcl -source "{gen_bit_tcl}"'
        
        start_t = perf_counter()
        subprocess.run(command, shell=True, cwd=FPGA_DIR)
        stop_t = perf_counter()
        
        time_sec = int(stop_t-start_t)
        time_min = int(time_sec / 60)
        time_sec = time_sec % 60

        self.bitstream_files = self.file_manager.list_bit_files(os.path.join(FPGA_DIR, "build"))

        results_dir = os.path.join(PROJECT_DIR, "results")
        os.makedirs(results_dir, exist_ok=True)

        for bitstream_file in self.bitstream_files:
            shutil.copy(bitstream_file, results_dir)
        print(f"Copied bitstream(s) to {results_dir}")

        self.get_warning_summary()

        print(colorama.Fore.GREEN + f"Bitstream generated in {time_min} min. {time_sec} sec.")
      
    def program_fpga(self):
        vivado_bin = os.path.join(VIVADO_DIR, "bin")
        os.environ["PATH"] = vivado_bin + os.pathsep + os.environ["PATH"]

        self.bitstream_files = self.file_manager.list_bit_files(os.path.join(PROJECT_DIR, "results"))
        bitstream_file = self.bitstream_files[0] 
        tcl_script = os.path.join(self.TOOLS_DIR, "scripts", "program_fpga.tcl")


        command = f'{VIVADO_DIR}/vivado.bat -mode tcl -source "{tcl_script}" -tclargs "{bitstream_file}"'
        subprocess.run(command, shell=True)

        print(colorama.Fore.GREEN + f"Bitstream {bitstream_file} programmed successfully.")
        
    def clean(self):
        try:
            subprocess.run(["git", "clean", "-fdX"], cwd=PROJECT_DIR, check=True)
            print(colorama.Fore.GREEN + "Untracked files removed successfully.")
        except subprocess.CalledProcessError:
            print(colorama.Fore.RED + "Error: Failed to clean untracked files. Make sure this is a valid git repository.")
            sys.exit(1)
                 
    def get_warning_summary(self):
        
        build_search_path = os.path.join("fpga", "build")
        warning_summary_log = os.path.join("results", "warning_summary.log")

        SYNTH_IGNORE = re.compile(r"\[Constraints\s18-5210\]|\[Netlist\s29-345\]|\[Synth\s8-6014\]|\[Synth\s8-7129\]")
        IMPL_IGNORE = re.compile(r"replace_with_codes_to_be_ignored_only_when_justified")
        
        os.makedirs(os.path.dirname(warning_summary_log), exist_ok=True)


        with open(warning_summary_log, "w") as log:
            log.write("Warnings, critical warnings, and errors from synthesis and implementation\n")
            log.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # ---- SYNTHESIS ----
            log.write("----SYNTHESIS----\n")
            synth_logs = glob.glob(os.path.join(build_search_path, "*.runs", "synth_1", "runme.log"))

            if synth_logs:
                found_warnings = False
                with open(synth_logs[0], "r") as synth_log:
                    for line in synth_log:
                        if re.search(r"CRITICAL|WARNING|ERROR", line) and not SYNTH_IGNORE.search(line):
                            log.write(line)
                            found_warnings = True
                if not found_warnings:
                    log.write("CLEAR :)\n")
            else:
                log.write("No synthesis log file found!\n")

            log.write("\n----IMPLEMENTATION----\n")
            
            # ---- IMPLEMENTATION ----
            impl_logs = glob.glob(os.path.join(build_search_path, "*.runs", "impl_1", "runme.log"))

            if impl_logs:
                found_warnings = False
                with open(impl_logs[0], "r") as impl_log:
                    for line in impl_log:
                        if re.search(r"CRITICAL|WARNING|ERROR", line) and not IMPL_IGNORE.search(line):
                            log.write(line)
                            found_warnings = True
                if not found_warnings:
                    log.write("CLEAR :)\n")
            else:
                log.write("No implementation log file found!\n")


        with open(warning_summary_log, "r") as file:
            log_content = file.read()

        log_content = re.sub(r"[A-Za-z]:\\.*?\\fpga\\build\\", "", log_content)

        with open(warning_summary_log, "w") as file:
            file.write(log_content)

        print(f"Log summary saved to {warning_summary_log}")
        



def main():
    parser = argparse.ArgumentParser(
        description="Vivado Project Management Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-g", "--generate_bitstream",
        action="store_true",
        help="Generate bitstream for the project"
    )
    parser.add_argument(
        "-p", "--program_fpga",
        action="store_true",
        help="Program the FPGA with the generated bitstream"
    )
    parser.add_argument(
        "-c", "--clean",
        action="store_true",
        help="Clean the project directory"
    )
    parser.add_argument(
        "-w", "--warning_summary",
        action="store_true",
        help="Extracts warnings and errors from synthesis and implementation logs"
    )
    
    args = parser.parse_args()
    vivado = VivadoWrapper()
    
    
    if args.generate_bitstream:
        vivado.generate_bitstream()
    
    if args.program_fpga:
        vivado.program_fpga()
    
    if args.clean:
        vivado.clean()
    
    if args.warning_summary:
        vivado.get_warning_summary()
    

if __name__ == "__main__":
    main()
