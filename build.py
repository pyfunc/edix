#!/usr/bin/env python3
"""
Standalone build script for Edix frontend assets
This is a convenience script that can be run independently of setup.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.cmd}")
        print(f"Exit code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def build_frontend_standalone():
    """Build the frontend assets (standalone version)"""
    print("Building frontend assets...")
    
    # Set up paths
    ROOT_DIR = Path(__file__).parent.absolute()
    PACKAGE_DIR = ROOT_DIR / "edix"
    FRONTEND_DIR = ROOT_DIR / "frontend_src"
    
    # Clean previous build
    static_dir = PACKAGE_DIR / "static"
    templates_dir = PACKAGE_DIR / "templates"
    
    if static_dir.exists():
        shutil.rmtree(static_dir)
    if templates_dir.exists():
        shutil.rmtree(templates_dir)
    
    # Create necessary directories
    static_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if Node.js and npm are installed
    try:
        node_version = run_command("node --version")
        npm_version = run_command("npm --version")
        print(f"Using Node.js {node_version.strip()} and npm {npm_version.strip()}")
    except FileNotFoundError:
        print("Error: Node.js and npm are required to build the frontend.")
        print("Please install Node.js from https://nodejs.org/ and try again.")
        sys.exit(1)
    
    # Install dependencies and build
    print("Installing frontend dependencies...")
    run_command("npm install", cwd=str(FRONTEND_DIR))
    
    print("Building frontend...")
    run_command("npm run build", cwd=str(FRONTEND_DIR))
    
    print("Frontend build completed successfully!")

def main():
    """Main function"""
    print("Starting Edix standalone build process...")
    print("Note: This is a standalone build script. For package installation, use 'pip install -e .'")
    print()
    
    build_frontend_standalone()
    
    print("\nBuild process completed successfully!")
    print("The frontend assets have been built and are ready for use.")

if __name__ == "__main__":
    main()
