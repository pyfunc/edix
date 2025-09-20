import React, { useState, useEffect, useRef } from 'react';
import { ChevronRight, ChevronDown, Plus, Trash2, Save, Download, Upload, Database, FileJson, FileText, Table } from 'lucide-react';

const EdixEditor = () => {
  const [structures, setStructures] = useState([]);
  const [selectedStructure, setSelectedStructure] = useState(null);
  const [structureData, setStructureData] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [editMode, setEditMode] = useState('yaml');
  const [editContent, setEditContent] = useState('');
  const [validationError, setValidationError] = useState('');
  const [showSchemaEditor, setShowSchemaEditor] = useState(false);
  const [newStructureName, setNewStructureName] = useState('');
  const [schema, setSchema] = useState({
    type: 'object',
    properties: {
      name: { type: 'string', description: 'Name field' },
      value: { type: 'number', description: 'Numeric value' },
      active: { type: 'boolean', description: 'Active status' }
    },
    required: ['name']
  });

  // Mock API calls - replace with actual API
  const API_BASE = '/api';

  const loadStructures = async () => {
    // Mock data - replace with API call
    const mockStructures = [
      {
        id: 1,
        name: 'menu',
        schema: {
          type: 'object',
          properties: {
            label: { type: 'string' },
            url: { type: 'string' },
            children: { type: 'array', items: { type: 'object' } }
          }
        }
      },
      {
        id: 2,
        name: 'config',
        schema: {
          type: 'object',
          properties: {
            key: { type: 'string' },
            value: { type: 'string' },
            type: { type: 'string', enum: ['string', 'number', 'boolean'] }
          }
        }
      }
    ];
    setStructures(mockStructures);
  };

  const loadStructureData = async (structureName) => {
    // Mock data - replace with API call
    const mockData = [
      { id: 1, label: 'Home', url: '/', children: [] },
      { id: 2, label: 'About', url: '/about', children: [] },
      {
        id: 3,
        label: 'Products',
        url: '/products',
        children: [
          { id: 4, label: 'Software', url: '/products/software' },
          { id: 5, label: 'Hardware', url: '/products/hardware' }
        ]
      }
    ];
    setStructureData(mockData);
  };

  const saveData = async () => {
    try {
      let parsedData;
      if (editMode === 'json') {
        parsedData = JSON.parse(editContent);
      } else {
        // Simple YAML parser (in real app use js-yaml)
        parsedData = parseSimpleYaml(editContent);
      }
      
      // API call to save data
      console.log('Saving:', parsedData);
      setValidationError('');
      
      // Update local state
      if (selectedItem) {
        const updated = structureData.map(item =>
          item.id === selectedItem.id ? { ...item, ...parsedData } : item
        );
        setStructureData(updated);
      }
    } catch (error) {
      setValidationError(`Invalid ${editMode.toUpperCase()}: ${error.message}`);
    }
  };

  const parseSimpleYaml = (yaml) => {
    const lines = yaml.split('\n');
    const result = {};
    let currentIndent = 0;
    let currentObj = result;
    const stack = [result];

    lines.forEach(line => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;

      const indent = line.length - line.trimStart().length;
      const [key, ...valueParts] = trimmed.split(':');
      const value = valueParts.join(':').trim();

      if (value) {
        currentObj[key] = value.replace(/^["']|["']$/g, '');
      } else {
        currentObj[key] = {};
        stack.push(currentObj[key]);
        currentObj = currentObj[key];
      }
    });

    return result;
  };

  const toYaml = (obj, indent = 0) => {
    let yaml = '';
    const spaces = '  '.repeat(indent);
    
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'object' && !Array.isArray(value)) {
        yaml += `${spaces}${key}:\n${toYaml(value, indent + 1)}`;
      } else if (Array.isArray(value)) {
        yaml += `${spaces}${key}:\n`;
        value.forEach(item => {
          if (typeof item === 'object') {
            yaml += `${spaces}  -\n${toYaml(item, indent + 2).split('\n').map(l => '  ' + l).join('\n')}`;
          } else {
            yaml += `${spaces}  - ${item}\n`;
          }
        });
      } else {
        yaml += `${spaces}${key}: ${value}\n`;
      }
    }
    
    return yaml;
  };

  const createStructure = async () => {
    if (!newStructureName) return;
    
    try {
      // API call to create structure
      console.log('Creating structure:', newStructureName, schema);
      
      // Add to local state
      setStructures([...structures, {
        id: Date.now(),
        name: newStructureName,
        schema: schema
      }]);
      
      setNewStructureName('');
      setShowSchemaEditor(false);
    } catch (error) {
      setValidationError(`Failed to create structure: ${error.message}`);
    }
  };

  const TreeNode = ({ node, level = 0 }) => {
    const [expanded, setExpanded] = useState(false);
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div>
        <div
          className={`flex items-center p-2 hover:bg-gray-100 cursor-pointer ${
            selectedItem?.id === node.id ? 'bg-blue-100' : ''
          }`}
          style={{ paddingLeft: `${level * 20 + 10}px` }}
          onClick={() => {
            setSelectedItem(node);
            setEditContent(editMode === 'json' ? 
              JSON.stringify(node, null, 2) : 
              toYaml(node)
            );
          }}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              className="mr-2"
            >
              {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
          )}
          <span className="flex-1">{node.label || node.name || `Item ${node.id}`}</span>
        </div>
        {expanded && hasChildren && (
          <div>
            {node.children.map(child => (
              <TreeNode key={child.id} node={child} level={level + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  useEffect(() => {
    loadStructures();
  }, []);

  useEffect(() => {
    if (selectedStructure) {
      loadStructureData(selectedStructure.name);
    }
  }, [selectedStructure]);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar - Structure List */}
      <div className="w-64 bg-white border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold flex items-center">
            <Database className="mr-2" size={20} />
            Structures
          </h2>
        </div>
        <div className="p-4">
          <button
            onClick={() => setShowSchemaEditor(true)}
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            <Plus size={16} className="mr-2" />
            New Structure
          </button>
          <div className="mt-4 space-y-2">
            {structures.map(struct => (
              <button
                key={struct.id}
                onClick={() => setSelectedStructure(struct)}
                className={`w-full text-left px-3 py-2 rounded ${
                  selectedStructure?.id === struct.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'hover:bg-gray-100'
                }`}
              >
                {struct.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Middle Panel - Data Tree */}
      <div className="flex-1 flex">
        <div className="w-1/2 bg-white border-r border-gray-200">
          <div className="p-4 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-semibold">
              {selectedStructure ? `${selectedStructure.name} Data` : 'Select a structure'}
            </h3>
            <button
              onClick={() => {
                const newItem = { id: Date.now(), label: 'New Item' };
                setStructureData([...structureData, newItem]);
              }}
              className="p-2 hover:bg-gray-100 rounded"
              disabled={!selectedStructure}
            >
              <Plus size={16} />
            </button>
          </div>
          <div className="overflow-auto h-full">
            {structureData.map(item => (
              <TreeNode key={item.id} node={item} />
            ))}
          </div>
        </div>

        {/* Right Panel - Editor */}
        <div className="w-1/2 bg-white">
          <div className="p-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <div className="flex space-x-2">
                <button
                  onClick={() => setEditMode('json')}
                  className={`px-3 py-1 rounded ${
                    editMode === 'json' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
                  }`}
                >
                  <FileJson size={16} className="inline mr-1" />
                  JSON
                </button>
                <button
                  onClick={() => setEditMode('yaml')}
                  className={`px-3 py-1 rounded ${
                    editMode === 'yaml' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
                  }`}
                >
                  <FileText size={16} className="inline mr-1" />
                  YAML
                </button>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={saveData}
                  className="p-2 hover:bg-gray-100 rounded"
                  disabled={!selectedItem}
                >
                  <Save size={16} />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded">
                  <Download size={16} />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded">
                  <Upload size={16} />
                </button>
              </div>
            </div>
          </div>
          
          {validationError && (
            <div className="p-3 bg-red-50 text-red-700 border-b border-red-200">
              {validationError}
            </div>
          )}
          
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full h-full p-4 font-mono text-sm resize-none focus:outline-none"
            placeholder={selectedItem ? `Edit ${editMode.toUpperCase()} here...` : 'Select an item to edit'}
            disabled={!selectedItem}
            style={{ minHeight: '400px' }}
          />
        </div>
      </div>

      {/* Schema Editor Modal */}
      {showSchemaEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-2/3 max-h-[80vh] overflow-auto">
            <h2 className="text-xl font-semibold mb-4">Create New Structure</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Structure Name</label>
              <input
                type="text"
                value={newStructureName}
                onChange={(e) => setNewStructureName(e.target.value)}
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., products, settings, navigation"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Schema (JSON)</label>
              <textarea
                value={JSON.stringify(schema, null, 2)}
                onChange={(e) => {
                  try {
                    setSchema(JSON.parse(e.target.value));
                    setValidationError('');
                  } catch (err) {
                    setValidationError('Invalid JSON schema');
                  }
                }}
                className="w-full px-3 py-2 border rounded font-mono text-sm"
                rows={12}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <button
                onClick={() => {
                  setShowSchemaEditor(false);
                  setNewStructureName('');
                }}
                className="px-4 py-2 border rounded hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={createStructure}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                disabled={!newStructureName || validationError}
              >
                Create Structure
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EdixEditor;