import os
import shutil
import subprocess
import zipfile

PLUGIN_NAME = "SkyDeck-QGIS-Plugin"
LIBS_DIR = os.path.join(PLUGIN_NAME, "libs")

REQUIRED_PACKAGES = [
    'PyJWT==2.10.1',
    'azure-storage-blob==12.24.1',
    'PyQt5==5.15.11',
    'PyQtWebEngine==5.15.7',
    'pip-system-certs==4.0'
]

def clean_previous_build():
    if os.path.exists(LIBS_DIR):
        print(f"Removing old libs folder: {LIBS_DIR}")
        shutil.rmtree(LIBS_DIR)

def install_dependencies():
    print("Installing dependencies to libs folder...")
    subprocess.check_call([
        'pip', 'install', '--target', LIBS_DIR, *REQUIRED_PACKAGES, '--no-cache-dir'
    ])
    print("Dependencies installed.")

def clean_libs_folder():
    print("Cleaning unnecessary files from libs...")
    for root, dirs, files in os.walk(LIBS_DIR):
        for dirname in list(dirs):
            if dirname.endswith(('.dist-info', '__pycache__', 'tests', 'test')):
                dir_path = os.path.join(root, dirname)
                print(f"Removing: {dir_path}")
                shutil.rmtree(dir_path)


def main():
    print("Building QGIS Plugin Package...")
    clean_previous_build()
    install_dependencies()
    clean_libs_folder()

if __name__ == '__main__':
    main()