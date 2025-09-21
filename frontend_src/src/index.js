/**
 * Edix Frontend - Main Entry Point
 * Universal Data Structure Editor
 */
import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles/main.css';

// Import main components
import App from './components/App';
import { EdixProvider } from './contexts/EdixContext';

// Initialize the application
const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <EdixProvider>
      <App />
    </EdixProvider>
  </React.StrictMode>
);

// Hot Module Replacement
if (module.hot) {
  module.hot.accept('./components/App', () => {
    const NextApp = require('./components/App').default;
    root.render(
      <React.StrictMode>
        <EdixProvider>
          <NextApp />
        </EdixProvider>
      </React.StrictMode>
    );
  });
}
