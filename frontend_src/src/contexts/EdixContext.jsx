/**
 * Edix Context - Global State Management
 */
import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Initial state
const initialState = {
  structures: [],
  currentStructure: null,
  schemas: [],
  currentSchema: null,
  loading: false,
  error: null,
  connected: false,
  websocket: null
};

// Action types
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_STRUCTURES: 'SET_STRUCTURES',
  SET_CURRENT_STRUCTURE: 'SET_CURRENT_STRUCTURE',
  SET_SCHEMAS: 'SET_SCHEMAS',
  SET_CURRENT_SCHEMA: 'SET_CURRENT_SCHEMA',
  SET_CONNECTED: 'SET_CONNECTED',
  SET_WEBSOCKET: 'SET_WEBSOCKET',
  ADD_STRUCTURE: 'ADD_STRUCTURE',
  UPDATE_STRUCTURE: 'UPDATE_STRUCTURE',
  DELETE_STRUCTURE: 'DELETE_STRUCTURE'
};

// Reducer
const edixReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, loading: action.payload };
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    case ActionTypes.SET_STRUCTURES:
      return { ...state, structures: action.payload, loading: false };
    case ActionTypes.SET_CURRENT_STRUCTURE:
      return { ...state, currentStructure: action.payload };
    case ActionTypes.SET_SCHEMAS:
      return { ...state, schemas: action.payload };
    case ActionTypes.SET_CURRENT_SCHEMA:
      return { ...state, currentSchema: action.payload };
    case ActionTypes.SET_CONNECTED:
      return { ...state, connected: action.payload };
    case ActionTypes.SET_WEBSOCKET:
      return { ...state, websocket: action.payload };
    case ActionTypes.ADD_STRUCTURE:
      return { 
        ...state, 
        structures: [...state.structures, action.payload] 
      };
    case ActionTypes.UPDATE_STRUCTURE:
      return {
        ...state,
        structures: state.structures.map(s => 
          s.id === action.payload.id ? action.payload : s
        ),
        currentStructure: state.currentStructure?.id === action.payload.id 
          ? action.payload 
          : state.currentStructure
      };
    case ActionTypes.DELETE_STRUCTURE:
      return {
        ...state,
        structures: state.structures.filter(s => s.id !== action.payload),
        currentStructure: state.currentStructure?.id === action.payload 
          ? null 
          : state.currentStructure
      };
    default:
      return state;
  }
};

// Context
const EdixContext = createContext();

// Provider component
export const EdixProvider = ({ children }) => {
  const [state, dispatch] = useReducer(edixReducer, initialState);

  // API base URL
  const API_BASE = '/api';

  // API functions
  const api = {
    async fetchStructures() {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      try {
        const response = await fetch(`${API_BASE}/tables`);
        if (!response.ok) throw new Error('Failed to fetch structures');
        const data = await response.json();
        dispatch({ type: ActionTypes.SET_STRUCTURES, payload: data });
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
      }
    },

    async fetchSchemas() {
      try {
        const response = await fetch(`${API_BASE}/schemas`);
        if (!response.ok) throw new Error('Failed to fetch schemas');
        const data = await response.json();
        dispatch({ type: ActionTypes.SET_SCHEMAS, payload: data });
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
      }
    },

    async createStructure(name, schema) {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      try {
        const response = await fetch(`${API_BASE}/tables`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, schema })
        });
        if (!response.ok) throw new Error('Failed to create structure');
        const data = await response.json();
        dispatch({ type: ActionTypes.ADD_STRUCTURE, payload: data });
        return data;
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
        throw error;
      }
    },

    async deleteStructure(id) {
      try {
        const response = await fetch(`${API_BASE}/tables/${id}`, {
          method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete structure');
        dispatch({ type: ActionTypes.DELETE_STRUCTURE, payload: id });
      } catch (error) {
        dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
        throw error;
      }
    }
  };

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://${window.location.host}/ws`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        dispatch({ type: ActionTypes.SET_CONNECTED, payload: true });
        dispatch({ type: ActionTypes.SET_WEBSOCKET, payload: ws });
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        dispatch({ type: ActionTypes.SET_CONNECTED, payload: false });
        dispatch({ type: ActionTypes.SET_WEBSOCKET, payload: null });
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        dispatch({ type: ActionTypes.SET_ERROR, payload: 'WebSocket connection failed' });
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          // Handle real-time updates
          if (message.type === 'structure_updated') {
            dispatch({ type: ActionTypes.UPDATE_STRUCTURE, payload: message.data });
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (state.websocket) {
        state.websocket.close();
      }
    };
  }, []);

  // Load initial data
  useEffect(() => {
    api.fetchStructures();
    api.fetchSchemas();
  }, []);

  // Context value
  const contextValue = {
    ...state,
    setCurrentStructure: (structure) => 
      dispatch({ type: ActionTypes.SET_CURRENT_STRUCTURE, payload: structure }),
    setCurrentSchema: (schema) => 
      dispatch({ type: ActionTypes.SET_CURRENT_SCHEMA, payload: schema }),
    setError: (error) => 
      dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    clearError: () => 
      dispatch({ type: ActionTypes.SET_ERROR, payload: null }),
    api
  };

  return (
    <EdixContext.Provider value={contextValue}>
      {children}
    </EdixContext.Provider>
  );
};

// Hook to use context
export const useEdix = () => {
  const context = useContext(EdixContext);
  if (!context) {
    throw new Error('useEdix must be used within an EdixProvider');
  }
  return context;
};

export default EdixContext;
