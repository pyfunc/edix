#!/bin/bash
# install.sh - Edix installer script

echo "========================================="
echo "       Edix Universal Editor Setup       "
echo "========================================="
echo

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check Node.js (optional for frontend development)
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✅ Node.js version: $node_version"
else
    echo "⚠️  Node.js not found (optional, needed only for frontend development)"
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv edix_env

# Activate virtual environment
source edix_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Edix from PyPI
echo
echo "Installing Edix..."
pip install edix

# Or install from source (if local)
# pip install -e .

# Initialize database
echo
echo "Initializing database..."
edix init

# Create configuration file
echo
echo "Creating configuration file..."
cat > edix.yaml << EOF
database:
  path: ./edix.db
  
server:
  host: 127.0.0.1
  port: 8000
  
cors:
  origins: ["*"]
  
export:
  formats: ["json", "yaml", "csv", "xml"]
  
logging:
  level: info
EOF

echo "✅ Configuration saved to edix.yaml"

# Create systemd service (optional)
if [ "$1" == "--service" ]; then
    echo
    echo "Creating systemd service..."
    sudo cat > /etc/systemd/system/edix.service << EOF
[Unit]
Description=Edix Universal Data Editor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/edix_env/bin"
ExecStart=$(pwd)/edix_env/bin/edix serve
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable edix
    echo "✅ Systemd service created"
fi

echo
echo "========================================="
echo "       Installation Complete! 🎉         "
echo "========================================="
echo
echo "To start Edix:"
echo "  source edix_env/bin/activate"
echo "  edix serve"
echo
echo "Then open http://localhost:8000 in your browser"
echo
echo "For help:"
echo "  edix --help"
echo