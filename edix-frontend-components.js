// frontend_src/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// frontend_src/src/App.jsx
import React, { useState, useEffect } from 'react';
import Editor from './components/Editor';
import StructureList from './components/StructureList';
import DataTree from './components/DataTree';
import SchemaBuilder from './components/SchemaBuilder';
import { EdixProvider } from './context/EdixContext';
import { WebSocketProvider } from './context/WebSocketContext';

function App() {
  const [config] = useState(window.EdixConfig || {
    apiUrl: '/api',
    wsUrl: 'ws://localhost:8000/ws',
    embedMode: false
  });

  return (
    <EdixProvider config={config}>
      <WebSocketProvider url={config.wsUrl}>
        <div className="edix-app">
          <Editor />
        </div>
      </WebSocketProvider>
    </EdixProvider>
  );
}

export default App;

// frontend_src/src/components/Editor.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useEdix } from '../context/EdixContext';
import { useWebSocket } from '../context/WebSocketContext';
import StructureList from './StructureList';
import DataTree from './DataTree';
import CodeEditor from './CodeEditor';
import SchemaBuilder from './SchemaBuilder';
import Toolbar from './Toolbar';
import { 
  Database, FileJson, FileText, Save, Download, 
  Upload, Plus, Settings, Eye, Code 
} from 'lucide-react';
import * as yaml from 'js-yaml';

const Editor = () => {
  const { 
    structures, 
    selectedStructure, 
    selectedData,
    loading,
    saveData,
    deleteData 
  } = useEdix();
  
  const { sendMessage, lastMessage } = useWebSocket();
  
  const [viewMode, setViewMode] = useState('split'); // split, tree, code, schema
  const [editFormat, setEditFormat] = useState('yaml');
  const [editContent, setEditContent] = useState('');
  const [isDirty, setIsDirty] = useState(false);
  const [validationErrors, setValidationErrors] = useState([]);

  useEffect(() => {
    if (lastMessage) {
      handleWebSocketMessage(lastMessage);
    }
  }, [lastMessage]);

  const handleWebSocketMessage = (message) => {
    if (message.type === 'data_update') {
      // Refresh data if it's for current structure
      if (message.structure === selectedStructure?.name) {
        // Trigger refresh
      }
    }
  };

  const handleSave = async () => {
    try {
      let data;
      if (editFormat === 'json') {
        data = JSON.parse(editContent);
      } else if (editFormat === 'yaml') {
        data = yaml.load(editContent);
      }
      
      await saveData(data);
      setIsDirty(false);
      
      // Broadcast update via WebSocket
      sendMessage({
        type: 'update',
        structure: selectedStructure.name,
        data: data
      });
    } catch (error) {
      setValidationErrors([error.message]);
    }
  };

  const handleExport = async (format) => {
    const response = await fetch(`${config.apiUrl}/export/${format}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        structure_name: selectedStructure?.name 
      })
    });
    
    const result = await response.json();
    
    // Download file
    const blob = new Blob([result.data], { 
      type: format === 'json' ? 'application/json' : 'text/plain' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedStructure.name}.${format}`;
    a.click();
  };

  return (
    <div className="edix-editor">
      <div className="edix-header">
        <Toolbar 
          onSave={handleSave}
          onExport={handleExport}
          isDirty={isDirty}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />
      </div>
      
      <div className="edix-body">
        <div className="edix-sidebar">
          <StructureList />
        </div>
        
        <div className="edix-content">
          {viewMode === 'split' && (
            <>
              <div className="edix-panel">
                <DataTree />
              </div>
              <div className="edix-panel">
                <CodeEditor
                  content={editContent}
                  onChange={(content) => {
                    setEditContent(content);
                    setIsDirty(true);
                  }}
                  format={editFormat}
                  onFormatChange={setEditFormat}
                  errors={validationErrors}
                />
              </div>
            </>
          )}
          
          {viewMode === 'tree' && <DataTree fullWidth />}
          
          {viewMode === 'code' && (
            <CodeEditor
              content={editContent}
              onChange={(content) => {
                setEditContent(content);
                setIsDirty(true);
              }}
              format={editFormat}
              onFormatChange={setEditFormat}
              errors={validationErrors}
              fullWidth
            />
          )}
          
          {viewMode === 'schema' && (
            <SchemaBuilder 
              structure={selectedStructure}
            />
          )}
        </div>
      </div>
      
      {loading && (
        <div className="edix-loading">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
};

export default Editor;

// frontend_src/src/components/DataTree.jsx
import React, { useState, useMemo } from 'react';
import { ChevronRight, ChevronDown, Plus, Trash2, Edit2, Copy } from 'lucide-react';
import { useEdix } from '../context/EdixContext';

const DataTree = ({ fullWidth = false }) => {
  const { 
    structureData, 
    selectedItem, 
    setSelectedItem,
    addItem,
    deleteItem,
    updateItem 
  } = useEdix();
  
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [editingNode, setEditingNode] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const toggleExpand = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const filteredData = useMemo(() => {
    if (!searchTerm) return structureData;
    
    const filterTree = (nodes) => {
      return nodes.filter(node => {
        const matchesSearch = JSON.stringify(node)
          .toLowerCase()
          .includes(searchTerm.toLowerCase());
        
        if (node.children && node.children.length > 0) {
          node.children = filterTree(node.children);
          return matchesSearch || node.children.length > 0;
        }
        
        return matchesSearch;
      });
    };
    
    return filterTree([...structureData]);
  }, [structureData, searchTerm]);

  const TreeNode = ({ node, level = 0 }) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedItem?.id === node.id;
    const isEditing = editingNode === node.id;
    const [editValue, setEditValue] = useState(node.label || node.name || '');

    const handleEdit = () => {
      if (isEditing) {
        updateItem(node.id, { ...node, label: editValue });
        setEditingNode(null);
      } else {
        setEditingNode(node.id);
      }
    };

    const handleKeyPress = (e) => {
      if (e.key === 'Enter') {
        handleEdit();
      } else if (e.key === 'Escape') {
        setEditingNode(null);
        setEditValue(node.label || node.name || '');
      }
    };

    return (
      <div className="tree-node-wrapper">
        <div 
          className={`tree-node ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 20 + 8}px` }}
          onClick={() => !isEditing && setSelectedItem(node)}
        >
          {hasChildren && (
            <button
              className="expand-btn"
              onClick={(e) => {
                e.stopPropagation();
                toggleExpand(node.id);
              }}
            >
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
          )}
          
          {isEditing ? (
            <input
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={handleKeyPress}
              onBlur={() => setEditingNode(null)}
              autoFocus
              className="tree-node-input"
            />
          ) : (
            <span className="tree-node-label">
              {node.label || node.name || `Item ${node.id}`}
            </span>
          )}
          
          <div className="tree-node-actions">
            <button onClick={handleEdit} title="Edit">
              <Edit2 size={14} />
            </button>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                addItem(node.id);
              }} 
              title="Add child"
            >
              <Plus size={14} />
            </button>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                deleteItem(node.id);
              }} 
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>
        
        {isExpanded && hasChildren && (
          <div className="tree-children">
            {node.children.map(child => (
              <TreeNode key={child.id} node={child} level={level + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`data-tree ${fullWidth ? 'full-width' : ''}`}>
      <div className="data-tree-header">
        <input
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <button 
          onClick={() => addItem(null)} 
          className="add-root-btn"
          title="Add root item"
        >
          <Plus size={16} />
        </button>
      </div>
      
      <div className="data-tree-content">
        {filteredData.map(node => (
          <TreeNode key={node.id} node={node} />
        ))}
        
        {filteredData.length === 0 && (
          <div className="empty-state">
            <p>No data available</p>
            <button onClick={() => addItem(null)} className="btn btn-primary">
              Add first item
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataTree;

// frontend_src/src/components/CodeEditor.jsx
import React, { useEffect, useRef } from 'react';
import { FileJson, FileText, AlertCircle } from 'lucide-react';
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';

const CodeEditor = ({ 
  content, 
  onChange, 
  format, 
  onFormatChange, 
  errors = [],
  fullWidth = false 
}) => {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  useEffect(() => {
    if (editorRef.current && !monacoRef.current) {
      monacoRef.current = monaco.editor.create(editorRef.current, {
        value: content,
        language: format === 'json' ? 'json' : 'yaml',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        wordWrap: 'on'
      });

      monacoRef.current.onDidChangeModelContent(() => {
        onChange(monacoRef.current.getValue());
      });
    }

    return () => {
      monacoRef.current?.dispose();
    };
  }, []);

  useEffect(() => {
    if (monacoRef.current) {
      const model = monacoRef.current.getModel();
      monaco.editor.setModelLanguage(model, format === 'json' ? 'json' : 'yaml');
    }
  }, [format]);

  useEffect(() => {
    if (monacoRef.current && content !== monacoRef.current.getValue()) {
      monacoRef.current.setValue(content);
    }
  }, [content]);

  // Fallback to textarea if Monaco fails
  const FallbackEditor = () => (
    <textarea
      value={content}
      onChange={(e) => onChange(e.target.value)}
      className="code-editor-fallback"
      spellCheck={false}
    />
  );

  return (
    <div className={`code-editor-container ${fullWidth ? 'full-width' : ''}`}>
      <div className="code-editor-header">
        <div className="format-selector">
          <button
            className={format === 'json' ? 'active' : ''}
            onClick={() => onFormatChange('json')}
          >
            <FileJson size={16} />
            JSON
          </button>
          <button
            className={format === 'yaml' ? 'active' : ''}
            onClick={() => onFormatChange('yaml')}
          >
            <FileText size={16} />
            YAML
          </button>
        </div>
      </div>
      
      {errors.length > 0 && (
        <div className="validation-errors">
          {errors.map((error, i) => (
            <div key={i} className="error-message">
              <AlertCircle size={14} />
              {error}
            </div>
          ))}
        </div>
      )}
      
      <div className="code-editor" ref={editorRef}>
        {!monacoRef.current && <FallbackEditor />}
      </div>
    </div>
  );
};

export default CodeEditor;

// frontend_src/src/context/EdixContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const EdixContext = createContext();

export const useEdix = () => {
  const context = useContext(EdixContext);
  if (!context) {
    throw new Error('useEdix must be used within EdixProvider');
  }
  return context;
};

export const EdixProvider = ({ children, config }) => {
  const [structures, setStructures] = useState([]);
  const [selectedStructure, setSelectedStructure] = useState(null);
  const [structureData, setStructureData] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiCall = async (endpoint, options = {}) => {
    const url = `${config.apiUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  };

  const loadStructures = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/structures');
      setStructures(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadStructureData = async (structureName) => {
    setLoading(true);
    try {
      const data = await apiCall(`/structures/${structureName}/data`);
      setStructureData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveData = async (data) => {
    const endpoint = selectedItem 
      ? `/structures/${selectedStructure.name}/data/${selectedItem.id}`
      : `/structures/${selectedStructure.name}/data`;
    
    const method = selectedItem ? 'PUT' : 'POST';
    
    await apiCall(endpoint, {
      method,
      body: JSON.stringify(data)
    });
    
    await loadStructureData(selectedStructure.name);
  };

  const deleteData = async (itemId) => {
    await apiCall(`/structures/${selectedStructure.name}/data/${itemId}`, {
      method: 'DELETE'
    });
    
    await loadStructureData(selectedStructure.name);
  };

  const addItem = async (parentId = null) => {
    const newItem = {
      label: 'New Item',
      parent_id: parentId
    };
    
    await saveData(newItem);
  };

  const updateItem = async (itemId, data) => {
    setSelectedItem({ id: itemId, ...data });
    await saveData(data);
  };

  const deleteItem = async (itemId) => {
    if (confirm('Are you sure you want to delete this item?')) {
      await deleteData(itemId);
      setSelectedItem(null);
    }
  };

  useEffect(() => {
    loadStructures();
  }, []);

  useEffect(() => {
    if (selectedStructure) {
      loadStructureData(selectedStructure.name);
    }
  }, [selectedStructure]);

  const value = {
    structures,
    selectedStructure,
    setSelectedStructure,
    structureData,
    selectedItem,
    setSelectedItem,
    loading,
    error,
    saveData,
    deleteData,
    addItem,
    updateItem,
    deleteItem,
    loadStructures,
    loadStructureData,
    config
  };

  return (
    <EdixContext.Provider value={value}>
      {children}
    </EdixContext.Provider>
  );
};

// frontend_src/src/context/WebSocketContext.jsx
import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children, url }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const connect = () => {
      try {
        wsRef.current = new WebSocket(url);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
        };

        wsRef.current.onmessage = (event) => {
          const message = JSON.parse(event.data);
          setLastMessage(message);
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          
          // Reconnect after 3 seconds
          setTimeout(connect, 3000);
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
      }
    };

    connect();

    return () => {
      wsRef.current?.close();
    };
  }, [url]);

  const sendMessage = (message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  const value = {
    isConnected,
    lastMessage,
    sendMessage
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};