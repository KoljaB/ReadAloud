import subprocess
import sys
import importlib

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
    # If True, don't prompt again—just install missing packages automatically.
    install_all_missing = False

    for package in packages:
        module_name = package['module_name']
        attribute = package.get('attribute')
        install_name = package.get('install_name', module_name)
        version = package.get('version', '')

        try:
            # Try importing the module.
            imported_module = importlib.import_module(module_name)
            # If a specific attribute is required, try getting it.
            if attribute:
                getattr(imported_module, attribute)

        except (ImportError, AttributeError):
            # If we've already chosen "a", then we won't prompt again.
            if install_all_missing:
                user_choice = 'y'
            else:
                # Explain the options clearly to the user.
                print(f"'{module_name}' is missing.")
                print("Options:")
                print("  y: Yes, install this package now")
                print("  n: No, don't install and exit the program")
                print("  a: Yes to all, install now and don't ask again for missing packages")
                user_choice = input(f"Do you want to install '{install_name}'? (y/n/a): ").strip().lower()

            if user_choice not in ['y', 'n', 'a']:
                # If they type something else, treat it like 'n'.
                user_choice = 'n'

            if user_choice == 'n':
                print(f"'{install_name}' is required. Exiting...")
                sys.exit(1)
            elif user_choice == 'a':
                # Switch into auto-install mode for future missing packages.
                install_all_missing = True
                user_choice = 'y'

            # If we're installing now (either this one or all).
            if user_choice == 'y':
                try:
                    cmd = [sys.executable, "-m", "pip", "install"]
                    if version:
                        cmd.append(f"{install_name}{version}")
                    else:
                        cmd.append(install_name)

                    subprocess.check_call(cmd)
                    # Re-check after installation.
                    imported_module = importlib.import_module(module_name)
                    if attribute:
                        getattr(imported_module, attribute)
                    print(f"Installed '{install_name}' successfully.")
                except Exception as e:
                    print(f"Error installing '{install_name}': {e}")
                    sys.exit(1)


def check_torch_cuda():
    """
    Checks whether 'torch' is installed and CUDA is available. If CUDA isn't available,
    it checks if nvcc is installed (which implies CUDA is installed on the system).
    If so, it prompts the user to install torch 2.5.1 with either cu118 or cu121
    depending on the detected major CUDA version (11.x or 12.x). Otherwise, it
    offers to install the CPU-only version.
    """
    try:
        import torch
        # If torch is installed, check for CUDA
        if torch.cuda.is_available():
            print("Torch is installed and CUDA is available.")
            return
        else:
            print("Torch is installed, but CUDA isn't available.")
    except ImportError:
        print("Torch is not installed at all.")

    # If we reach here, either Torch isn't installed or CUDA isn't available in Torch
    # Let's see if nvcc is installed (which means CUDA is on the system)
    try:
        nvcc_output = subprocess.check_output(["nvcc", "--version"]).decode().lower()

        # Check for major CUDA version
        if "release 12." in nvcc_output:
            cuda_version_str = "cu121"
        elif "release 11.8" in nvcc_output:
            # If you only want to handle 11.8 specifically:
            cuda_version_str = "cu118"
        elif "release 11." in nvcc_output:
            # If you want any 11.x to map to cu118:
            cuda_version_str = "cu118"
        else:
            print("Couldn't detect a matching CUDA version (11.x or 12.x).")
            cuda_version_str = None
    except FileNotFoundError:
        # nvcc isn't found, so user doesn't have CUDA installed
        cuda_version_str = None

    if cuda_version_str:
        # Prompt to install the correct GPU-enabled torch
        user_input = input(
            f"CUDA seems to be installed (detected {cuda_version_str}). "
            f"Do you want to install torch==2.5.1+{cuda_version_str} with torchaudio==2.5.1? (y/n): "
        )
        if user_input.strip().lower() == 'y':
            try:
                pip_command = [
                    sys.executable, "-m", "pip", "install",
                    f"torch==2.5.1+{cuda_version_str}",
                    "torchaudio==2.5.1",
                    "--index-url", f"https://download.pytorch.org/whl/{cuda_version_str}"
                ]
                subprocess.check_call(pip_command)
                print(f"Successfully installed torch 2.5.1 with {cuda_version_str}.")
            except Exception as e:
                print(f"Failed to install torch with {cuda_version_str}: {e}")
                sys.exit(1)
        else:
            print("Skipping torch installation with CUDA.")
    else:
        # If we can't detect CUDA or it's not installed, offer CPU-only install
        user_input = input(
            "CUDA isn't installed or not recognized. "
            "Do you want to install the CPU-only version of torch==2.5.1? (y/n): "
        )
        if user_input.strip().lower() == 'y':
            try:
                pip_command = [sys.executable, "-m", "pip", "install", "torch==2.5.1", "torchaudio==2.5.1"]
                subprocess.check_call(pip_command)
                print("Successfully installed torch CPU-only version (2.5.1).")
            except Exception as e:
                print(f"Failed to install the CPU-only version of torch: {e}")
                sys.exit(1)
        else:
            print("Skipping torch installation altogether.")
