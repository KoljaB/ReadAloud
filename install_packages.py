"""
Package and CUDA Dependency Checker Module

This module offers two main functions to manage and verify dependencies:
1. check_and_install_packages(packages):
   - Iterates through a list of package specifications (each a dictionary with keys like 'module_name',
     'attribute', 'install_name', and 'version') and checks if each package is installed.
   - If a package or its required attribute is missing, it prompts the user with three options:
       • 'y' to install the package immediately,
       • 'n' to skip installation and exit,
       • 'a' to install the current and any future missing packages without further prompts.
   - It then uses pip (via a subprocess call) to install the missing package and re-verifies the installation.

2. check_torch_cuda():
   - Checks if the PyTorch library ('torch') is installed and whether CUDA support is available.
   - If torch is installed but CUDA isn't available, it looks for the NVIDIA CUDA compiler (nvcc) to determine
     if CUDA is installed system-wide and infers the CUDA version (e.g., 11.x or 12.x).
   - Based on the detected CUDA version, it prompts the user to install the corresponding GPU-enabled version of torch (2.5.1)
     with either cu118 or cu121 support, or to install the CPU-only version if CUDA is not found or not desired.
"""

import subprocess
import time
import sys
import importlib

# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
RESET = "\033[0m"

def check_and_install_packages(packages):
    """
    Checks if each package in 'packages' is installed. If not, it asks if you want to install it.
    The prompt has three options:
      - 'y': Install now.
      - 'n': Do not install and exit the program.
      - 'a': Install this package (and any future missing packages) without asking again.

    Parameters:
    - packages: A list of dictionaries, each containing:
        - 'module_name': The name you'd use with 'import X'.
        - 'attribute': (Optional) A specific attribute or class needed from the module.
        - 'install_name': The name used when running 'pip install ...'.
        - 'version': (Optional) A version string like '==1.2.3' or '>=1.0'.
    """
    print(f"{CYAN}Starting dependency check for required packages...{RESET}")
    # If True, don't prompt again—just install missing packages automatically.
    install_all_missing = False

    for package in packages:
        module_name = package['module_name']
        attribute = package.get('attribute')
        install_name = package.get('install_name', module_name)
        version = package.get('version', '')

        print(f"{BLUE}Checking package '{module_name}'...{RESET}")
        try:
            # Try importing the module.
            imported_module = importlib.import_module(module_name)
            # If a specific attribute is required, try getting it.
            if attribute:
                getattr(imported_module, attribute)
            print(f"{GREEN}Module '{module_name}' is already installed and ready to use.{RESET}")
            continue  # Move to the next package if everything is fine.
        except (ImportError, AttributeError):
            print(f"{YELLOW}Module '{module_name}' or required attribute is missing.{RESET}")

            # If we've already chosen "a", then we won't prompt again.
            if install_all_missing:
                user_choice = 'y'
            else:
                # Explain the options clearly to the user.
                print(f"{CYAN}Installation Options for '{module_name}':{RESET}")
                print("  y: Yes, install this package now")
                print("  n: No, don't install and exit the program")
                print("  a: Yes to all, install now and don't ask again for missing packages")
                user_choice = input(f"{BLUE}Do you want to install '{install_name}'? (y/n/a): {RESET}").strip().lower()

            if user_choice not in ['y', 'n', 'a']:
                # If they type something else, treat it like 'n'.
                user_choice = 'n'

            if user_choice == 'n':
                print(f"{RED}'{install_name}' is required. Exiting...{RESET}")
                sys.exit(1)
            elif user_choice == 'a':
                # Switch into auto-install mode for future missing packages.
                install_all_missing = True
                user_choice = 'y'

            # If we're installing now (either this one or all).
            if user_choice == 'y':
                try:
                    print(f"{CYAN}Attempting to install '{install_name}'...{RESET}")
                    cmd = [sys.executable, "-m", "pip", "install"]
                    if version:
                        cmd.append(f"{install_name}{version}")
                    else:
                        cmd.append(install_name)

                    subprocess.check_call(cmd)
                    print(f"{GREEN}Installed '{install_name}' successfully.{RESET}")
                except Exception as e:
                    print(f"{RED}Error installing '{install_name}': {e}{RESET}")
                    sys.exit(1)
    print(f"{GREEN}All required packages have been checked.{RESET}\n")


def check_torch_cuda():
    """
    Checks whether 'torch' is installed and CUDA is available. If CUDA isn't available,
    it checks if nvcc is installed (which implies CUDA is installed on the system).
    If so, it prompts the user to install torch 2.5.1 with either cu118 or cu121
    depending on the detected major CUDA version (11.x or 12.x). Otherwise, it
    offers to install the CPU-only version.
    """
    print(f"{CYAN}Checking for PyTorch and CUDA support...{RESET}")
    try:
        import torch
        # If torch is installed, check for CUDA
        if torch.cuda.is_available():
            print(f"{GREEN}Torch is installed and CUDA is available.{RESET}")
            return
        else:
            print(f"{YELLOW}Torch is installed, but CUDA isn't available according to torch.cuda.is_available().{RESET}")
    except ImportError:
        print(f"{YELLOW}Torch is not installed at all.{RESET}")

    # If we reach here, either Torch isn't installed or CUDA isn't available in Torch
    # Let's see if nvcc is installed (which means CUDA is on the system)
    try:
        print(f"{BLUE}Checking for NVIDIA CUDA compiler (nvcc)...{RESET}")
        nvcc_output = subprocess.check_output(["nvcc", "--version"]).decode().lower()
        print(f"{GREEN}nvcc found. Parsing CUDA version from nvcc output...{RESET}")

        # Check for major CUDA version
        if "release 12." in nvcc_output:
            cuda_version_str = "cu121"
        elif "release 11.8" in nvcc_output:
            cuda_version_str = "cu118"
        elif "release 11." in nvcc_output:
            cuda_version_str = "cu118"
        else:
            print(f"{YELLOW}Couldn't detect a matching CUDA version (11.x or 12.x) from nvcc output.{RESET}")
            cuda_version_str = None
    except FileNotFoundError:
        # nvcc isn't found, so user doesn't have CUDA installed
        print(f"{YELLOW}nvcc not found. CUDA may not be installed on this system.{RESET}")
        cuda_version_str = None

    if cuda_version_str:
        # Prompt to install the correct GPU-enabled torch
        user_input = input(
            f"{BLUE}CUDA seems to be installed (detected {cuda_version_str}). "
            f"Do you want to install torch==2.5.1+{cuda_version_str} with torchaudio==2.5.1? (y/n): {RESET}"
        )
        if user_input.strip().lower() == 'y':
            try:
                print(f"{CYAN}Installing torch 2.5.1 with {cuda_version_str} support...{RESET}")
                pip_command = [
                    sys.executable, "-m", "pip", "install",
                    f"torch==2.5.1+{cuda_version_str}",
                    "torchaudio==2.5.1",
                    "--index-url", f"https://download.pytorch.org/whl/{cuda_version_str}"
                ]
                subprocess.check_call(pip_command)
                print(f"{GREEN}Successfully installed torch 2.5.1 with {cuda_version_str}.{RESET}")
            except Exception as e:
                print(f"{RED}Failed to install torch with {cuda_version_str}: {e}{RESET}")
                sys.exit(1)
        else:
            print(f"{CYAN}Skipping torch installation with CUDA support as per user request.{RESET}")
    else:
        # If we can't detect CUDA or it's not installed, offer CPU-only install
        user_input = input(
            f"{BLUE}CUDA isn't installed or not recognized. "
            "Do you want to install the CPU-only version of torch==2.5.1? (y/n): {RESET}"
        )
        if user_input.strip().lower() == 'y':
            try:
                print(f"{CYAN}Installing torch 2.5.1 (CPU-only version)...{RESET}")
                pip_command = [sys.executable, "-m", "pip", "install", "torch==2.5.1", "torchaudio==2.5.1"]
                subprocess.check_call(pip_command)
                print(f"{GREEN}Successfully installed torch CPU-only version (2.5.1).{RESET}")
            except Exception as e:
                print(f"{RED}Failed to install the CPU-only version of torch: {e}{RESET}")
                sys.exit(1)
        else:
            print(f"{CYAN}Skipping torch installation altogether as per user choice.{RESET}")
