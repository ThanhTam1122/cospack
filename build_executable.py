#!/usr/bin/env python3
"""
Script to build standalone executables for the Shipping Application.
This script uses PyInstaller to create executables for Windows, macOS, and Linux.
"""
import os
import sys
import platform
import subprocess
import argparse


def get_platform_specific_settings():
    """Get platform-specific settings for the build."""
    system = platform.system()
    settings = {
        'hidden_imports': [
            # FastAPI and dependencies
            'fastapi',
            'fastapi.middleware',
            'fastapi.middleware.cors',
            'pydantic',
            'pydantic_core',
            'pydantic_settings',
            'pydantic.json',
            'starlette',
            'starlette.middleware',
            'starlette.middleware.cors',
            'starlette.responses',
            'starlette.routing',
            'starlette.applications',
            'starlette.types',
            'starlette.datastructures',
            'starlette.background',
            'starlette.concurrency',
            'starlette.config',
            'starlette.exceptions',
            'starlette.staticfiles',
            'starlette.templating',
            'starlette.websockets',
            # Uvicorn and dependencies
            'uvicorn',
            'uvicorn.logging',
            'uvicorn.loops',
            'uvicorn.loops.auto',
            'uvicorn.protocols',
            'uvicorn.protocols.http',
            'uvicorn.protocols.http.auto',
            'uvicorn.protocols.websockets',
            'uvicorn.protocols.websockets.auto',
            'uvicorn.lifespan',
            'uvicorn.lifespan.on',
            'uvicorn.lifespan.off',
            'uvicorn.protocols.http.h11_impl',
            'uvicorn.protocols.http.httptools_impl',
            'uvicorn.protocols.websockets.websockets_impl',
            'uvicorn.protocols.websockets.wsproto_impl',
            # SQLAlchemy and database
            'sqlalchemy',
            'sqlalchemy.ext.declarative',
            'sqlalchemy.orm',
            'pymysql',
            'PySide6',
            'PySide6.sip',
            'PySide6.QtCore',
            'PySide6.QtGui',
            'PySide6.QtWidgets',
            'PySide6.QtNetwork',
            # App modules
            'app',
            'app.main',
            'app.database',
            'app.models',
            'app.routers',
            'app.schemas',
            'app.services',
            'app.utils'
        ]
    }
    return settings


def get_platform_specific_extensions():
    """Get platform-specific executable extensions and launcher extensions."""
    system = platform.system()
    if system == 'Windows':
        return {
            'exe_extension': '.exe',
            'launcher_extension': '.bat',
            'executable_name': 'ShippingApp.exe'
        }
    elif system == 'Darwin':  # macOS
        return {
            'exe_extension': '',
            'launcher_extension': '.command',
            'executable_name': 'ShippingApp'
        }
    else:  # Linux and others
        return {
            'exe_extension': '',
            'launcher_extension': '.sh',
            'executable_name': 'ShippingApp'
        }


def get_pyinstaller_command(onefile=False, debug=False):
    """Get the PyInstaller command based on the platform"""
    # Get the absolute path to the main.py file
    main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'main.py'))
    
    # Create spec directory if it doesn't exist
    os.makedirs('pyinstaller', exist_ok=True)
    
    # Create a spec file directly instead of using PyInstaller's spec file
    spec_file = os.path.join('pyinstaller', f'shipping_app_{platform.system().lower()}.spec')
    create_spec_file(platform.system(), debug)
    
    cmd = ['pyinstaller']
    
    if debug:
        cmd.extend(['--log-level', 'DEBUG'])
    
    cmd.extend(['--clean', spec_file])
    
    return cmd


def create_spec_file(platform, debug=False):
    """Create a PyInstaller spec file for the given platform."""
    # Get the absolute paths
    main_script = os.path.abspath('main.py')
    app_dir = os.path.abspath('app')
    
    # Fix path for Windows
    if platform == 'Windows':
        main_script = main_script.replace('\\', '\\\\')
        app_dir = app_dir.replace('\\', '\\\\')
    
    # Get platform-specific settings
    platform_ext = get_platform_specific_extensions()
    
    # Platform-specific additions to spec file
    platform_specific_imports = []
    
    if platform == 'Darwin':  # macOS
        platform_specific_imports = [
            'pymssql',  # Alternative SQL Server driver for macOS
            'sqlalchemy.dialects.mssql.pymssql',
            'pydantic_settings',
        ]
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_script}'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[("{app_dir}", "app")],
    hiddenimports={get_platform_specific_settings()['hidden_imports'] + platform_specific_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ShippingApp{platform_ext["exe_extension"]}',
    debug={debug},
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    # Create the pyinstaller directory if it doesn't exist
    os.makedirs('pyinstaller', exist_ok=True)

    # Write the spec file
    spec_file = os.path.join('pyinstaller', f'shipping_app_{platform.lower()}.spec')
    with open(spec_file, 'w') as f:
        f.write(spec_content)

    return spec_file


def create_launcher_script(platform):
    """Create a platform-specific launcher script."""
    platform_ext = get_platform_specific_extensions()
    launcher_name = f'run_shipping_app{platform_ext["launcher_extension"]}'
    launcher_path = os.path.join('dist', launcher_name)
    
    if platform == 'Windows':
        with open(launcher_path, 'w') as f:
            f.write('@echo off\n')
            f.write('start ShippingApp.exe\n')
    elif platform == 'Darwin':  # macOS
        with open(launcher_path, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('# macOS launcher script for Shipping App\n')
            f.write('DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"\n')
            f.write('cd "$DIR"\n')
            f.write('./ShippingApp\n')
        
        # Make it executable
        try:
            os.chmod(launcher_path, 0o755)
            print(f"Set executable permissions on {launcher_path}")
        except Exception as e:
            print(f"Warning: Failed to set executable permissions: {str(e)}")
            print("You may need to run: chmod +x dist/run_shipping_app.command")
            
        # Create an additional Info.plist file for macOS
        create_macos_info_plist()
    else:  # Linux and others
        with open(launcher_path, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('./ShippingApp\n')
        os.chmod(launcher_path, 0o755)
    
    return launcher_path


def create_macos_info_plist():
    """Create Info.plist file for macOS app bundling."""
    plist_path = os.path.join('dist', 'Info.plist')
    
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Shipping App</string>
    <key>CFBundleExecutable</key>
    <string>ShippingApp</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.company.shippingapp</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>ShippingApp</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
'''
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    print(f"Created Info.plist at {plist_path}")
    return plist_path


def setup_wine_environment():
    """Setup Wine environment for Windows builds on Linux."""
    if not os.path.exists(os.path.expanduser('~/.wine')):
        print("Wine environment not detected. Setting up Wine environment...")
        try:
            # Check if Wine is installed
            subprocess.run(['wine', '--version'], check=True, stdout=subprocess.PIPE)
            print("Wine is installed, initializing Wine environment...")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Wine is not installed. Please install Wine:")
            print("sudo apt update && sudo apt install wine64")
            sys.exit(1)

    # Check if Python is installed in Wine
    wine_python_path = os.path.expanduser('~/.wine/drive_c/Python39/python.exe')
    if not os.path.exists(wine_python_path):
        print(f"Python not found in Wine at {wine_python_path}")
        print("You need to install Python in Wine. Download and install using:")
        print("wget https://www.python.org/ftp/python/3.9.10/python-3.9.10-amd64.exe")
        print("wine python-3.9.10-amd64.exe /quiet InstallAllUsers=1 PrependPath=1")
        sys.exit(1)

    # Check if PyInstaller is installed in Wine Python
    try:
        result = subprocess.run(['wine', 'python', '-m', 'pip', 'list'], 
                               stdout=subprocess.PIPE, check=True, text=True)
        if 'pyinstaller' not in result.stdout.lower():
            print("PyInstaller not found in Wine Python. Installing...")
            subprocess.run(['wine', 'python', '-m', 'pip', 'install', 'pyinstaller'], check=True)
            print("PyInstaller installed in Wine Python.")
    except subprocess.CalledProcessError:
        print("Error checking or installing PyInstaller in Wine Python.")
        print("Try installing manually: wine python -m pip install pyinstaller")
        sys.exit(1)

    print("Wine environment is ready for Windows builds.")
    return True


def build_executable(onefile=False, debug=False, no_confirm=False, target_platform=None):
    """Build the executable."""
    # Get platform info
    host_platform = platform.system()
    platform_name = target_platform or host_platform
    
    if target_platform:
        print(f"Cross-compiling from {host_platform} to {target_platform}")
        
    # Setup Wine environment if cross-compiling to Windows from Linux
    if host_platform == 'Linux' and target_platform == 'Windows':
        setup_wine_environment()
    
    # Get extensions based on target platform
    if target_platform == 'Windows':
        platform_ext = {
            'exe_extension': '.exe',
            'launcher_extension': '.bat',
            'executable_name': 'ShippingApp.exe'
        }
    elif target_platform == 'Darwin':
        platform_ext = {
            'exe_extension': '',
            'launcher_extension': '.command',
            'executable_name': 'ShippingApp'
        }
    elif target_platform == 'Linux':
        platform_ext = {
            'exe_extension': '',
            'launcher_extension': '.sh',
            'executable_name': 'ShippingApp'
        }
    else:
        platform_ext = get_platform_specific_extensions()
    
    # Check if app directory exists
    app_dir = os.path.abspath('app')
    if not os.path.exists(app_dir):
        print(f"Error: App directory '{app_dir}' not found. Make sure you're in the correct directory.")
        if not no_confirm:
            proceed = input("Continue anyway? (y/n): ").lower() == 'y'
            if not proceed:
                sys.exit(1)
    
    print(f"Building executable for {platform_name}...")
    print(f"Mode: {'Single file' if onefile else 'Directory'}")
    print(f"Debug: {'Enabled' if debug else 'Disabled'}")

    # Create a spec file
    spec_file = create_spec_file(platform_name, debug)

    # Build the command - use python -m pyinstaller instead of direct pyinstaller command
    if host_platform == 'Linux' and target_platform == 'Windows':
        # Using Wine to run Python
        cmd = ['wine', 'python', '-m', 'PyInstaller']
    else:
        # Using native Python
        cmd = [sys.executable, '-m', 'PyInstaller']
    
    if debug:
        cmd.extend(['--log-level', 'DEBUG'])
    
    cmd.extend(['--clean', spec_file])

    print(f"Running command: {' '.join(cmd)}")
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: PyInstaller build failed with return code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: PyInstaller or Python not found. Make sure they are installed and in your PATH.")
        if host_platform == 'Linux' and target_platform == 'Windows':
            print("\nFor Wine builds, you need to:")
            print("1. Install Wine: sudo apt install wine64")
            print("2. Install Python in Wine: wine python-3.9.10-amd64.exe")
            print("3. Install PyInstaller in Wine: wine pip install pyinstaller")
        sys.exit(1)

    # Create platform-specific launcher script
    launcher_path = create_launcher_script(platform_name)
    print(f"\nCreated launcher script: {launcher_path}")

    print("\nExecutable built successfully!")
    print(f"Output can be found in: {os.path.abspath(os.path.join('dist', platform_ext['executable_name']))}")
    print(f"Build type: {'onefile' if onefile else 'directory'}, Platform: {platform_name}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Build the Shipping Application executable')
    parser.add_argument('--onefile', action='store_true', help='Create a single executable file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompts')
    parser.add_argument('--target', choices=['Windows', 'Linux', 'Darwin'], 
                        help='Target platform (Windows, Linux, Darwin/macOS)')
    args = parser.parse_args()

    build_executable(onefile=args.onefile, debug=args.debug, no_confirm=args.no_confirm, 
                    target_platform=args.target)


if __name__ == '__main__':
    main()