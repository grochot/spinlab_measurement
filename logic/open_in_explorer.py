import os
import platform
import subprocess


def open_in_explorer(path_to_file):
    path_to_file = os.path.normpath(path_to_file)
    current_os = platform.system()

    if current_os == "Windows":
        subprocess.Popen(["explorer", "/select,", path_to_file])
    elif current_os == "Darwin":
        subprocess.Popen(["open", "-R", path_to_file])
    elif current_os == "Linux":
        subprocess.Popen(["xdg-open", os.path.dirname(path_to_file)])
    else:
        raise OSError(f"Unsupported operating system: {current_os}")
