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
import shutil


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
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_script}'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[('{app_dir}', 'app')],
    hiddenimports={get_platform_specific_settings()['hidden_imports']},
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
    name='ShippingApp',
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


def build_executable(onefile=False, debug=False, no_confirm=False):
    """Build the executable."""
    # Get platform info
    platform_name = platform.system()
    print(f"Building executable for {platform_name}...")
    print(f"Mode: {'Single file' if onefile else 'Directory'}")
    print(f"Debug: {'Enabled' if debug else 'Disabled'}")

    # Create a spec file
    spec_file = create_spec_file(platform_name, debug)

    # Build the command
    cmd = ['pyinstaller', '--log-level', 'DEBUG', '--clean', spec_file]

    print(f"Running command: {' '.join(cmd)}")
    
    # Run PyInstaller
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Error: PyInstaller build failed")
        sys.exit(1)

    # Create a launcher script for Linux/macOS
    if platform_name in ['Linux', 'Darwin']:
        launcher_script = os.path.join('dist', 'run_shipping_app.sh')
        with open(launcher_script, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('./ShippingApp\n')
        os.chmod(launcher_script, 0o755)
        print(f"\nCreated launcher script: {launcher_script}")

    print("\nExecutable built successfully!")
    print(f"Output can be found in: {os.path.abspath(os.path.join('dist', 'ShippingApp'))}")
    print(f"Build type: {'onefile' if onefile else 'directory'}, Platform: {platform_name}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Build the Shipping Application executable')
    parser.add_argument('--onefile', action='store_true', help='Create a single executable file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompts')
    args = parser.parse_args()

    build_executable(onefile=args.onefile, debug=args.debug, no_confirm=args.no_confirm)


if __name__ == '__main__':
    main()