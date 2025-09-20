# frontend_src/src/styles.css
```css
/* Edix Editor Styles */
:root {
  --edix-primary: #3b82f6;
  --edix-primary-dark: #2563eb;
  --edix-secondary: #8b5cf6;
  --edix-success: #10b981;
  --edix-danger: #ef4444;
  --edix-warning: #f59e0b;
  --edix-bg: #ffffff;
  --edix-bg-secondary: #f9fafb;
  --edix-border: #e5e7eb;
  --edix-text: #111827;
  --edix-text-secondary: #6b7280;
  --edix-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --edix-radius: 0.375rem;
}

[data-theme="dark"] {
  --edix-bg: #1f2937;
  --edix-bg-secondary: #111827;
  --edix-border: #374151;
  --edix-text: #f9fafb;
  --edix-text-secondary: #9ca3af;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: var(--edix-text);
  background: var(--edix-bg);
  line-height: 1.6;
}

/* Layout */
.edix-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.edix-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.edix-header {
  background: var(--edix-bg);
  border-bottom: 1px solid var(--edix-border);
  padding: 0.75rem 1rem;
  flex-shrink: 0;
}

.edix-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.edix-sidebar {
  width: 250px;
  background: var(--edix-bg-secondary);
  border-right: 1px solid var(--edix-border);
  overflow-y: auto;
  flex-shrink: 0;
}

.edix-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.edix-panel {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--edix-border);
}

.edix-panel:last-child {
  border-right: none;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: var(--edix-bg);
  border: 1px solid var(--edix-border);
  border-radius: var(--edix-radius);
  color: var(--edix-text);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.toolbar-button:hover {
  background: var(--edix-bg-secondary);
}

.toolbar-button.active {
  background: var(--edix-primary);
  color: white;
  border-color: var(--edix-primary);
}

.toolbar-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Structure List */
.structure-list {
  padding: 1rem;
}

.structure-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--edix-border);
}

.structure-list-title {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--edix-text-secondary);
}

.structure-item {
  display: flex;
  align-items: center;
  padding: 0.625rem 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: var(--edix-radius);
  cursor: pointer;
  transition: background 0.2s;
}

.structure-item:hover {
  background: var(--edix-bg);
}

.structure-item.selected {
  background: var(--edix-primary);
  color: white;
}

/* Data Tree */
.data-tree {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--edix-bg);
}

.data-tree-header {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid var(--edix-border);
}

.search-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--edix-border);
  border-radius: var(--edix-radius);
  background: var(--edix-bg);
  color: var(--edix-text);
  font-size: 0.875rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--edix-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.data-tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

/* Tree Node */
.tree-node-wrapper {
  user-select: none;
}

.tree-node {
  display: flex;
  align-items: center;
  padding: 0.375rem 0.5rem;
  border-radius: var(--edix-radius);
  cursor: pointer;
  transition: background 0.2s;
}

.tree-node:hover {
  background: var(--edix-bg-secondary);
}

.tree-node.selected {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid var(--edix-primary);
}

.expand-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 0.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--edix-text-secondary);
}

.tree-node-label {
  flex: 1;
  font-size: 0.875rem;
  color: var(--edix-text);
}

.tree-node-actions {
  display: none;
  gap: 0.25rem;
}

.tree-node:hover .tree-node-actions {
  display: flex;
}

.tree-node-actions button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: var(--edix-radius);
  color: var(--edix-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tree-node-actions button:hover {
  background: var(--edix-bg);
  color: var(--edix-primary);
}

.tree-children {
  margin-left: 1rem;
}

/* Code Editor */
.code-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--edix-bg);
}

.code-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--edix-border);
}

.format-selector {
  display: flex;
  gap: 0.25rem;
  background: var(--edix-bg-secondary);
  padding: 0.25rem;
  border-radius: var(--edix-radius);
}

.format-selector button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: var(--edix-radius);
  color: var(--edix-text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.format-selector button.active {
  background: var(--edix-bg);
  color: var(--edix-primary);
}

.code-editor {
  flex: 1;
  position: relative;
  min-height: 0;
}

.code-editor-fallback {
  width: 100%;
  height: 100%;
  padding: 1rem;
  font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  border: none;
  resize: none;
  background: var(--edix-bg);
  color: var(--edix-text);
}

.validation-errors {
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--edix-danger);
  font-size: 0.875rem;
}

/* Schema Builder */
.schema-builder {
  padding: 1.5rem;
  overflow-y: auto;
}

.schema-property {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--edix-bg-secondary);
  border-radius: var(--edix-radius);
  border: 1px solid var(--edix-border);
}

.property-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.property-name {
  font-weight: 600;
  color: var(--edix-text);
}

.property-type {
  padding: 0.25rem 0.5rem;
  background: var(--edix-primary);
  color: white;
  border-radius: var(--edix-radius);
  font-size: 0.75rem;
  text-transform: uppercase;
}

.property-field {
  margin-bottom: 0.75rem;
}

.property-field label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: var(--edix-text-secondary);
}

.property-field input,
.property-field select,
.property-field textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--edix-border);
  border-radius: var(--edix-radius);
  background: var(--edix-bg);
  color: var(--edix-text);
  font-size: 0.875rem;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.empty-state p {
  margin-bottom: 1rem;
  color: var(--edix-text-secondary);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  border-radius: var(--edix-radius);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--edix-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--edix-primary-dark);
}

.btn-secondary {
  background: var(--edix-bg);
  border-color: var(--edix-border);
  color: var(--edix-text);
}

.btn-secondary:hover {
  background: var(--edix-bg-secondary);
}

.btn-danger {
  background: var(--edix-danger);
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

/* Loading Spinner */
.edix-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 1000;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--edix-border);
  border-top-color: var(--edix-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .edix-sidebar {
    position: fixed;
    left: -250px;
    height: 100%;
    z-index: 100;
    transition: left 0.3s;
  }
  
  .edix-sidebar.open {
    left: 0;
  }
  
  .edix-content {
    flex-direction: column;
  }
  
  .edix-panel {
    border-right: none;
    border-bottom: 1px solid var(--edix-border);
  }
}
```

# examples/schemas/menu.json
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Navigation Menu",
  "type": "object",
  "properties": {
    "label": {
      "type": "string",
      "title": "Menu Label",
      "description": "Display text for the menu item",
      "minLength": 1,
      "maxLength": 50
    },
    "url": {
      "type": "string",
      "title": "URL",
      "description": "Link destination",
      "format": "uri-reference"
    },
    "icon": {
      "type": "string",
      "title": "Icon",
      "description": "Icon identifier (e.g., 'home', 'user', 'settings')"
    },
    "target": {
      "type": "string",
      "title": "Target",
      "enum": ["_self", "_blank", "_parent", "_top"],
      "default": "_self"
    },
    "active": {
      "type": "boolean",
      "title": "Active",
      "description": "Whether this menu item is currently active",
      "default": true
    },
    "order": {
      "type": "integer",
      "title": "Order",
      "description": "Display order (lower numbers appear first)",
      "minimum": 0,
      "default": 0
    },
    "permissions": {
      "type": "array",
      "title": "Required Permissions",
      "description": "User must have one of these permissions to see this item",
      "items": {
        "type": "string"
      }
    },
    "children": {
      "type": "array",
      "title": "Children",
      "description": "Nested menu items",
      "items": {
        "$ref": "#"
      }
    },
    "meta": {
      "type": "object",
      "title": "Metadata",
      "description": "Additional custom properties",
      "additionalProperties": true
    }
  },
  "required": ["label"]
}
```

# examples/schemas/product.json
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Product",
  "type": "object",
  "properties": {
    "sku": {
      "type": "string",
      "title": "SKU",
      "pattern": "^[A-Z0-9-]+$",
      "minLength": 3,
      "maxLength": 20,
      "index": true
    },
    "name": {
      "type": "string",
      "title": "Product Name",
      "minLength": 1,
      "maxLength": 200
    },
    "description": {
      "type": "string",
      "title": "Description",
      "maxLength": 2000
    },
    "price": {
      "type": "number",
      "title": "Price",
      "minimum": 0,
      "multipleOf": 0.01
    },
    "currency": {
      "type": "string",
      "title": "Currency",
      "enum": ["USD", "EUR", "GBP", "PLN"],
      "default": "USD"
    },
    "stock": {
      "type": "integer",
      "title": "Stock Quantity",
      "minimum": 0,
      "default": 0
    },
    "category": {
      "type": "string",
      "title": "Category",
      "enum": ["Electronics", "Clothing", "Food", "Books", "Other"]
    },
    "tags": {
      "type": "array",
      "title": "Tags",
      "items": {
        "type": "string"
      },
      "uniqueItems": true
    },
    "images": {
      "type": "array",
      "title": "Images",
      "items": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "format": "uri"
          },
          "alt": {
            "type": "string"
          },
          "primary": {
            "type": "boolean",
            "default": false
          }
        },
        "required": ["url"]
      }
    },
    "attributes": {
      "type": "object",
      "title": "Product Attributes",
      "properties": {
        "weight": {
          "type": "number",
          "title": "Weight (kg)"
        },
        "dimensions": {
          "type": "object",
          "properties": {
            "length": { "type": "number" },
            "width": { "type": "number" },
            "height": { "type": "number" }
          }
        },
        "color": {
          "type": "string"
        },
        "material": {
          "type": "string"
        }
      }
    },
    "active": {
      "type": "boolean",
      "title": "Active",
      "default": true
    },
    "featured": {
      "type": "boolean",
      "title": "Featured Product",
      "default": false
    }
  },
  "required": ["sku", "name", "price"]
}
```

# examples/sample_data/menu.yaml
```yaml
- label: Home
  url: /
  icon: home
  order: 1
  
- label: Products
  url: /products
  icon: package
  order: 2
  children:
    - label: All Products
      url: /products/all
      
    - label: Categories
      url: /products/categories
      
    - label: Special Offers
      url: /products/offers
      icon: tag
      
- label: About
  url: /about
  icon: info
  order: 3
  children:
    - label: Company
      url: /about/company
      
    - label: Team
      url: /about/team
      
    - label: History
      url: /about/history
      
- label: Services
  url: /services
  icon: briefcase
  order: 4
  
- label: Contact
  url: /contact
  icon: mail
  order: 5
  
- label: Admin
  url: /admin
  icon: settings
  order: 99
  permissions:
    - admin
    - moderator
  children:
    - label: Dashboard
      url: /admin/dashboard
      
    - label: Users
      url: /admin/users
      permissions:
        - admin
        
    - label: Settings
      url: /admin/settings
```

# API.md - API Documentation
```markdown
# Edix API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently, the API does not require authentication. In production, implement JWT or OAuth2.

## Endpoints

### Structures

#### List all structures
```http
GET /api/structures
```

Response:
```json
[
  {
    "id": 1,
    "name": "menu",
    "schema": {...},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "meta": {}
  }
]
```

#### Create a new structure
```http
POST /api/structures
```

Request body:
```json
{
  "name": "products",
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "price": {"type": "number"}
    },
    "required": ["name", "price"]
  }
}
```

#### Get structure schema
```http
GET /api/structures/{structure_name}
```

### Data Operations

#### Get all data for a structure
```http
GET /api/structures/{structure_name}/data
```

Query parameters:
- `limit`: Maximum number of records (default: 100)
- `offset`: Number of records to skip (default: 0)
- `sort`: Field to sort by
- `order`: Sort order (asc/desc)
- `filter`: JSON filter object

#### Create new data entry
```http
POST /api/structures/{structure_name}/data
```

Request body:
```json
{
  "name": "Product Name",
  "price": 29.99,
  "active": true
}
```

#### Update data entry
```http
PUT /api/structures/{structure_name}/data/{id}
```

#### Delete data entry
```http
DELETE /api/structures/{structure_name}/data/{id}
```

### Import/Export

#### Export data
```http
POST /api/export/{format}
```

Formats: json, yaml, csv, xml, excel

Request body:
```json
{
  "structure_name": "menu",
  "filters": {}
}
```

#### Import data
```http
POST /api/import/{format}
```

Request body:
```json
{
  "structure_name": "menu",
  "data": "..."
}
```

### WebSocket

#### Connect to WebSocket
```
ws://localhost:8000/ws
```

Message types:

Subscribe to structure updates:
```json
{
  "type": "subscribe",
  "structure": "menu"
}
```

Broadcast data update:
```json
{
  "type": "update",
  "structure": "menu",
  "data": {...}
}
```

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## Rate Limiting

Default limits:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## CORS

By default, CORS is enabled for all origins. Configure in production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Examples

### cURL

Create structure:
```bash
curl -X POST http://localhost:8000/api/structures \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tasks",
    "schema": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "done": {"type": "boolean"}
      }
    }
  }'
```

Add data:
```bash
curl -X POST http://localhost:8000/api/structures/tasks/data \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete documentation",
    "done": false
  }'
```

### JavaScript/Fetch

```javascript
// Get all menu items
const response = await fetch('http://localhost:8000/api/structures/menu/data');
const menuItems = await response.json();

// Update menu item
await fetch('http://localhost:8000/api/structures/menu/data/1', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    label: 'Updated Home',
    url: '/',
    active: true
  })
});
```

### Python

```python
import requests

# Create structure
response = requests.post(
    'http://localhost:8000/api/structures',
    json={
        'name': 'config',
        'schema': {
            'type': 'object',
            'properties': {
                'key': {'type': 'string'},
                'value': {'type': 'string'}
            }
        }
    }
)

# Export data as YAML
response = requests.post(
    'http://localhost:8000/api/export/yaml',
    json={'structure_name': 'menu'}
)
yaml_data = response.json()['data']
```
```