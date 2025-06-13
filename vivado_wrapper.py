import subprocess
import os
import shutil
import sys
import colorama
import glob
import argparse
import re
from datetime import datetime

from project_setup import VIVADO_DIR, PROJECT_DIR
from internals.file_manager import FileManager


class VivadoWrapper:
    def __init__(self):
      
        self.file_manager = FileManager()

    def generate_bitstream(self):
      vivado_executable = os.path.join(VIVADO_DIR, "vivado.bat")

      if not os.path.exists(vivado_executable):
        print(colorama.Fore.RED + f"Error: Vivado executable not found at {vivado_executable}.")
        sys.exit(1)       # (1) Update the .tcl file with fresh list of sources
      self.file_manager.update_generate_bitstream_tcl()

      # (2) Clean untracked files in the fpga directory
      subprocess.run(["git", "clean", "-fXd", "fpga"], cwd=PROJECT_DIR)

      # (3) Run Vivado in TCL mode to generate the bitstream
      fpga_dir   = os.path.join(PROJECT_DIR, "fpga")
      main_tcl   = os.path.join(fpga_dir, "scripts", "generate_bitstream.tcl")
      command    = f'"{vivado_executable}" -mode tcl -source "{main_tcl}"'
      subprocess.run(command, shell=True, cwd=fpga_dir)

      # (4) Copy generated bitstream to results directory
      bitstream_files = self.file_manager.list_bit_files(os.path.join(fpga_dir, "build"))
      if not bitstream_files:
          print(colorama.Fore.RED + "Error: No bitstream (.bit) file found in fpga/build.")
          sys.exit(1)

      results_dir = os.path.join(PROJECT_DIR, "results")
      os.makedirs(results_dir, exist_ok=True)

      for bitstream_file in bitstream_files:
          shutil.copy(bitstream_file, results_dir)
      print(f"Copied bitstream(s) to {results_dir}")

      self.get_warning_summary()

      print(colorama.Fore.GREEN + "Bitstream generation and logging completed successfully.")
      
    def program_fpga(self):
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
        
    def clean(self):
        try:
            subprocess.run(["git", "clean", "-fdX"], cwd=PROJECT_DIR, check=True)
            print(colorama.Fore.GREEN + "Untracked files removed successfully.")
        except subprocess.CalledProcessError:
            print(colorama.Fore.RED + "Error: Failed to clean untracked files. Make sure this is a valid git repository.")
            sys.exit(1)
            
            
    def get_warning_summary(self):
        
        PROJECT_PATH = os.path.join("fpga", "build")
        LOG_FILE = os.path.join("results", "warning_summary.log")

        SYNTH_IGNORE = re.compile(r"\[Constraints\s18-5210\]|\[Netlist\s29-345\]")
        IMPL_IGNORE = re.compile(r"replace_with_codes_to_be_ignored_only_when_justified")
        
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


        with open(LOG_FILE, "w") as log:
            log.write("Warnings, critical warnings, and errors from synthesis and implementation\n")
            log.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # ---- SYNTHESIS ----
            log.write("----SYNTHESIS----\n")
            synth_logs = glob.glob(os.path.join(PROJECT_PATH, "*.runs", "synth_1", "runme.log"))

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
            impl_logs = glob.glob(os.path.join(PROJECT_PATH, "*.runs", "impl_1", "runme.log"))

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


        with open(LOG_FILE, "r") as file:
            log_content = file.read()

        log_content = re.sub(r"[A-Za-z]:\\.*?\\fpga\\build\\", "", log_content)

        with open(LOG_FILE, "w") as file:
            file.write(log_content)

        print(f"Log summary saved to {LOG_FILE}")



def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Vivado Project Management Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Add arguments
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
    
    # Parse arguments
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
