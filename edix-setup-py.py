"""
Setup script for Edix package with automatic frontend building
"""
import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.install import install


def build_frontend():
    """Build frontend assets"""
    frontend_dir = Path(__file__).parent / "frontend_src"
    static_dir = Path(__file__).parent / "edix" / "static"
    
    # Create static directory if not exists
    static_dir.mkdir(parents=True, exist_ok=True)
    
    print("Building frontend assets...")
    
    # Check if npm is installed
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: npm not found. Using pre-built frontend assets.")
        return
    
    # Install npm dependencies
    if frontend_dir.exists():
        print("Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            check=False
        )
        
        # Build frontend
        print("Building frontend...")
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            check=False
        )
        
        if result.returncode == 0:
            print("Frontend built successfully!")
        else:
            print("Warning: Frontend build failed. Using fallback assets.")
    else:
        print("Frontend source not found. Using pre-built assets.")


class BuildPyCommand(build_py):
    """Custom build command to compile frontend"""
    def run(self):
        build_frontend()
        build_py.run(self)


class DevelopCommand(develop):
    """Custom develop command to compile frontend"""
    def run(self):
        build_frontend()
        develop.run(self)


class InstallCommand(install):
    """Custom install command to compile frontend"""
    def run(self):
        build_frontend()
        install.run(self)


# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")


setup(
    name="edix",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Universal data structure editor with dynamic SQL schema generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/edix",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "edix": [
            "static/**/*",
            "templates/**/*",
            "schemas/*.json",
        ],
    },
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "aiosqlite>=0.19.0",
        "jinja2>=3.1.0",
        "python-multipart>=0.0.6",
        "websockets>=11.0",
        "jsonschema>=4.19.0",
        "alembic>=1.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
            "ruff>=0.0.290",
        ],
        "export": [
            "openpyxl>=3.1.0",
            "lxml>=4.9.0",
            "toml>=0.10.2",
        ],
    },
    cmdclass={
        "build_py": BuildPyCommand,
        "develop": DevelopCommand,
        "install": InstallCommand,
    },
    entry_points={
        "console_scripts": [
            "edix=edix.__main__:main",
            "edix-server=edix.app:run_server",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
)