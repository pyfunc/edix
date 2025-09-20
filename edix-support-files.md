# MANIFEST.in
```
include README.md
include LICENSE
include requirements.txt
recursive-include edix/static *
recursive-include edix/templates *
recursive-include edix/schemas *.json
```

# README.md
```markdown
# Edix - Universal Data Structure Editor

[![PyPI version](https://badge.fury.io/py/edix.svg)](https://badge.fury.io/py/edix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Edix is a powerful, universal data structure editor that dynamically creates SQL tables from JSON schemas and provides a web-based interface for managing structured data.

## Features

- 🎯 **Dynamic Schema Management** - Define data structures using JSON Schema
- 🗄️ **Automatic SQL Generation** - Creates SQLite tables from your schemas
- 🌐 **Web-Based Editor** - Modern React interface for data management
- 📝 **Multi-Format Support** - Import/export JSON, YAML, CSV, XML
- 🔌 **Easy Integration** - Embed in existing web applications
- 🚀 **Real-time Updates** - WebSocket support for live data synchronization
- 📦 **Self-Contained** - Frontend bundled with Python package

## Installation

```bash
pip install edix
```

For development with extra features:
```bash
pip install edix[export,dev]
```

## Quick Start

### 1. Start the Server

```bash
edix serve
```

Open http://localhost:8000 in your browser.

### 2. Command Line Interface

```bash
# Initialize database
edix init --db mydata.db

# Start server with custom settings
edix serve --host 0.0.0.0 --port 8080

# Export data
edix export --format json --file data.json --structure menu

# Import data
edix import --format yaml --file data.yaml
```

### 3. Python API

```python
from edix import app, run_server

# Run server programmatically
run_server(host="127.0.0.1", port=8000)
```

### 4. Integration with FastAPI

```python
from fastapi import FastAPI
from edix import app as edix_app

main_app = FastAPI()
main_app.mount("/editor", edix_app)
```

## Schema Definition

Define your data structures using JSON Schema:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Item name",
      "maxLength": 100
    },
    "price": {
      "type": "number",
      "minimum": 0
    },
    "active": {
      "type": "boolean",
      "default": true
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["name", "price"]
}
```

## Embedding in Existing Sites

```html
<!-- Embed editor in your page -->
<iframe src="http://localhost:8000/embed/products" 
        width="100%" 
        height="600">
</iframe>
```

Or use the JavaScript API:

```javascript
const editor = new EdixEditor({
  container: '#editor-container',
  structure: 'products',
  apiUrl: 'http://localhost:8000/api'
});
```

## API Endpoints

- `GET /api/structures` - List all structures
- `POST /api/structures` - Create new structure
- `GET /api/structures/{name}/data` - Get structure data
- `POST /api/structures/{name}/data` - Insert data
- `PUT /api/structures/{name}/data/{id}` - Update data
- `DELETE /api/structures/{name}/data/{id}` - Delete data
- `POST /api/export/{format}` - Export data
- `POST /api/import/{format}` - Import data

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/edix
cd edix

# Install development dependencies
pip install -e .[dev]

# Build frontend
cd frontend_src
npm install
npm run build

# Run tests
pytest tests/
```

## Configuration

Create `edix.yaml` for configuration:

```yaml
database:
  path: ./data/edix.db
  
server:
  host: 0.0.0.0
  port: 8000
  
export:
  formats:
    - json
    - yaml
    - csv
    - xml
    - excel
```

## Examples

### Menu Structure
```python
menu_schema = {
    "type": "object",
    "properties": {
        "label": {"type": "string"},
        "url": {"type": "string"},
        "icon": {"type": "string"},
        "children": {
            "type": "array",
            "items": {"$ref": "#"}
        }
    }
}
```

### Configuration Store
```python
config_schema = {
    "type": "object",
    "properties": {
        "key": {"type": "string", "pattern": "^[A-Z_]+$"},
        "value": {"type": "string"},
        "environment": {
            "type": "string",
            "enum": ["development", "staging", "production"]
        }
    }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://edix.readthedocs.io
- Issues: https://github.com/yourusername/edix/issues
- Discussions: https://github.com/yourusername/edix/discussions
```

# edix/templates/editor.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .monaco-editor { min-height: 400px; }
        .tree-node { transition: all 0.2s; }
        .tree-node:hover { background-color: #f3f4f6; }
        .tree-node.selected { background-color: #dbeafe; }
    </style>
</head>
<body>
    <div id="root"></div>
    
    <script src="/static/app.js"></script>
    
    <!-- Alternative: Use CDN for React if not bundled -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    
    <script>
        // Initialize Edix Editor
        window.EdixConfig = {
            apiUrl: '/api',
            wsUrl: 'ws://localhost:8000/ws',
            embedMode: {{ 'true' if embed_mode else 'false' }}
        };
    </script>
</body>
</html>
```

# frontend_src/package.json
```json
{
  "name": "edix-frontend",
  "version": "1.0.0",
  "description": "Frontend for Edix universal data editor",
  "main": "src/index.js",
  "scripts": {
    "start": "webpack serve --mode development",
    "build": "webpack --mode production",
    "watch": "webpack --mode development --watch"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.263.1",
    "js-yaml": "^4.1.0",
    "monaco-editor": "^0.44.0"
  },
  "devDependencies": {
    "@babel/core": "^7.23.0",
    "@babel/preset-env": "^7.23.0",
    "@babel/preset-react": "^7.22.0",
    "babel-loader": "^9.1.3",
    "css-loader": "^6.8.1",
    "html-webpack-plugin": "^5.5.3",
    "style-loader": "^3.3.3",
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1"
  }
}
```

# frontend_src/webpack.config.js
```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, '../edix/static'),
    filename: 'app.js',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      filename: '../templates/editor.html'
    })
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    compress: true,
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
};
```

# LICENSE
```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```