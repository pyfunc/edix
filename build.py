#!/usr/bin/env python3
"""
Build script for Edix frontend assets
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

def install_dependencies():
    """Install frontend dependencies"""
    print("Installing frontend dependencies...")
    run_command("npm install", cwd=str(FRONTEND_DIR))

def build_frontend():
    """Build the frontend assets"""
    print("Building frontend assets...")
    
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
    
    # Build the frontend
    run_command("npm run build", cwd=str(FRONTEND_DIR))
    
    print("Frontend build completed successfully!")

def main():
    """Main function"""
    print("Starting Edix build process...")
    
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
    install_dependencies()
    build_frontend()
    
    print("\nBuild process completed successfully!")
    print("You can now install the package using: pip install -e .")

if __name__ == "__main__":
    # Set up paths
    ROOT_DIR = Path(__file__).parent.absolute()
    PACKAGE_DIR = ROOT_DIR / "edix"
    FRONTEND_DIR = ROOT_DIR / "frontend_src"
    
    main()
