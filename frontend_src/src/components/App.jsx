/**
 * Edix Main Application Component
 */
import React, { useState, useEffect } from 'react';
import { useEdix } from '../contexts/EdixContext';
import StructureList from './StructureList';
import SchemaBuilder from './SchemaBuilder';
import DataTree from './DataTree';
import CodeEditor from './CodeEditor';

const App = () => {
  const { 
    structures, 
    currentStructure, 
    setCurrentStructure,
    schemas,
    currentSchema,
    setCurrentSchema
  } = useEdix();

  const [activeTab, setActiveTab] = useState('structures');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="edix-app">
      {/* Header */}
      <header className="edix-header">
        <div className="header-content">
          <h1 className="edix-logo">
            <span className="logo-icon">📊</span>
            Edix
          </h1>
          <nav className="nav-tabs">
            <button 
              className={`nav-tab ${activeTab === 'structures' ? 'active' : ''}`}
              onClick={() => setActiveTab('structures')}
            >
              Structures
            </button>
            <button 
              className={`nav-tab ${activeTab === 'schemas' ? 'active' : ''}`}
              onClick={() => setActiveTab('schemas')}
            >
              Schemas
            </button>
            <button 
              className={`nav-tab ${activeTab === 'editor' ? 'active' : ''}`}
              onClick={() => setActiveTab('editor')}
            >
              Editor
            </button>
          </nav>
          <div className="header-actions">
            <button 
              className="sidebar-toggle"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              ☰
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="edix-main">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="edix-sidebar">
            {activeTab === 'structures' && (
              <StructureList 
                structures={structures}
                currentStructure={currentStructure}
                onSelectStructure={setCurrentStructure}
              />
            )}
            {activeTab === 'schemas' && (
              <div className="schema-list">
                <h3>Available Schemas</h3>
                {schemas.map(schema => (
                  <div 
                    key={schema.id}
                    className={`schema-item ${currentSchema?.id === schema.id ? 'active' : ''}`}
                    onClick={() => setCurrentSchema(schema)}
                  >
                    <span className="schema-name">{schema.name}</span>
                    <span className="schema-type">{schema.type}</span>
                  </div>
                ))}
              </div>
            )}
          </aside>
        )}

        {/* Content Area */}
        <main className="edix-content">
          {activeTab === 'structures' && (
            <div className="structures-view">
              {currentStructure ? (
                <DataTree structure={currentStructure} />
              ) : (
                <div className="empty-state">
                  <h2>No Structure Selected</h2>
                  <p>Select a structure from the sidebar to view its data.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'schemas' && (
            <div className="schemas-view">
              {currentSchema ? (
                <SchemaBuilder schema={currentSchema} />
              ) : (
                <div className="empty-state">
                  <h2>No Schema Selected</h2>
                  <p>Select a schema from the sidebar to edit it.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'editor' && (
            <div className="editor-view">
              <CodeEditor />
            </div>
          )}
        </main>
      </div>

      {/* Status Bar */}
      <footer className="edix-status-bar">
        <div className="status-left">
          <span className="status-item">
            Ready | {structures.length} structures loaded
          </span>
        </div>
        <div className="status-right">
          <span className="status-item">Edix v1.0.0</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
