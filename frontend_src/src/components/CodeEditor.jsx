import React, { useRef, useEffect } from 'react';
import { Box, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import * as monaco from 'monaco-editor';
import { getLanguageForFormat } from '../utils/editor-utils';

const CodeEditor = ({
  content,
  onChange,
  format = 'json',
  onFormatChange,
  errors = [],
  height = '400px',
  readOnly = false,
}) => {
  const editorRef = useRef(null);
  const editorInstance = useRef(null);
  const monacoRef = useRef(null);
  const containerRef = useRef(null);

  // Initialize Monaco Editor
  useEffect(() => {
    if (containerRef.current && !editorInstance.current) {
      // Create editor instance
      editorInstance.current = monaco.editor.create(containerRef.current, {
        value: content || '',
        language: getLanguageForFormat(format),
        theme: 'vs-light',
        automaticLayout: true,
        minimap: {
          enabled: false,
        },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        roundedSelection: false,
        readOnly,
        lineDecorationsWidth: 10,
        lineNumbersMinChars: 3,
      });

      // Handle content changes
      editorInstance.current.onDidChangeModelContent(() => {
        const value = editorInstance.current.getValue();
        onChange?.(value);
      });

      // Store monaco instance
      monacoRef.current = monaco;
    }

    return () => {
      if (editorInstance.current) {
        editorInstance.current.dispose();
        editorInstance.current = null;
      }
    };
  }, []);

  // Update content when it changes
  useEffect(() => {
    if (editorInstance.current && content !== editorInstance.current.getValue()) {
      editorInstance.current.setValue(content || '');
    }
  }, [content]);

  // Update language when format changes
  useEffect(() => {
    if (editorInstance.current) {
      const model = editorInstance.current.getModel();
      monaco.editor.setModelLanguage(model, getLanguageForFormat(format));
    }
  }, [format]);

  // Set editor options based on format
  useEffect(() => {
    if (editorInstance.current) {
      const options = {
        tabSize: 2,
        insertSpaces: true,
        autoIndent: 'full',
      };

      if (format === 'json') {
        options.formatOnPaste = true;
        options.formatOnType = true;
      }

      editorInstance.current.updateOptions(options);
    }
  }, [format]);

  // Handle errors
  useEffect(() => {
    if (!editorInstance.current) return;

    const model = editorInstance.current.getModel();
    if (!model) return;

    const markers = errors.map(error => ({
      severity: monaco.MarkerSeverity.Error,
      message: error.message,
      startLineNumber: error.lineNumber || 1,
      startColumn: error.column || 1,
      endLineNumber: error.endLineNumber || 1,
      endColumn: error.endColumn || 100,
    }));

    monaco.editor.setModelMarkers(model, 'owner', markers);
  }, [errors]);

  const formatOptions = [
    { value: 'json', label: 'JSON' },
    { value: 'yaml', label: 'YAML' },
    { value: 'xml', label: 'XML' },
    { value: 'csv', label: 'CSV' },
  ];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'center' }}>
        <Typography variant="subtitle2" color="textSecondary">
          Editor
        </Typography>
        
        {onFormatChange && (
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Format</InputLabel>
            <Select
              value={format}
              label="Format"
              onChange={(e) => onFormatChange(e.target.value)}
              size="small"
              disabled={readOnly}
            >
              {formatOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      </Box>
      
      <Box
        ref={containerRef}
        sx={{
          flex: 1,
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          overflow: 'hidden',
          '& .monaco-editor': {
            '--vscode-editor-background': '#f8f9fa',
          },
          '& .monaco-editor .margin': {
            backgroundColor: '#f8f9fa',
          },
          '& .monaco-editor .monaco-editor-background': {
            backgroundColor: '#f8f9fa',
          },
        }}
        style={{ height }}
      />
      
      {errors.length > 0 && (
        <Box sx={{ mt: 1 }}>
          {errors.map((error, index) => (
            <Typography key={index} color="error" variant="caption" component="div">
              Line {error.lineNumber || 1}: {error.message}
            </Typography>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default CodeEditor;
