/**
 * Gets the Monaco editor language ID for a given format
 * @param {string} format - The format name (e.g., 'json', 'yaml')
 * @returns {string} The Monaco editor language ID
 */
export const getLanguageForFormat = (format) => {
  const formatMap = {
    json: 'json',
    yaml: 'yaml',
    yml: 'yaml',
    xml: 'xml',
    html: 'html',
    csv: 'csv',
    javascript: 'javascript',
    js: 'javascript',
    typescript: 'typescript',
    ts: 'typescript',
    python: 'python',
    py: 'python',
    sql: 'sql',
    markdown: 'markdown',
    md: 'markdown',
  };

  return formatMap[format.toLowerCase()] || 'plaintext';
};

/**
 * Formats the content based on the specified format
 * @param {string} content - The content to format
 * @param {string} format - The target format (e.g., 'json', 'yaml')
 * @returns {Promise<string>} The formatted content
 */
export const formatContent = async (content, format) => {
  if (!content) return '';
  
  try {
    switch (format.toLowerCase()) {
      case 'json':
        return JSON.stringify(JSON.parse(content), null, 2);
      // Add more formatters as needed
      default:
        return content;
    }
  } catch (error) {
    console.error(`Error formatting content as ${format}:`, error);
    return content;
  }
};

/**
 * Validates content against a specific format
 * @param {string} content - The content to validate
 * @param {string} format - The format to validate against
 * @returns {{valid: boolean, errors: Array<{message: string, lineNumber?: number}>}}
 */
export const validateContent = (content, format) => {
  if (!content) return { valid: true, errors: [] };
  
  const errors = [];
  
  try {
    switch (format.toLowerCase()) {
      case 'json':
        JSON.parse(content);
        break;
      // Add more validators as needed
    }
    return { valid: true, errors };
  } catch (error) {
    // Parse error message to get line number if available
    const lineMatch = error.message.match(/at position (\d+)/);
    const position = lineMatch ? parseInt(lineMatch[1], 10) : 0;
    
    // Estimate line number based on position (very rough estimate)
    const lineNumber = position > 0 
      ? content.substring(0, position).split('\n').length
      : 1;
    
    errors.push({
      message: error.message,
      lineNumber,
      position,
    });
    
    return { valid: false, errors };
  }
};

/**
 * Converts content from one format to another
 * @param {string} content - The content to convert
 * @param {string} fromFormat - The source format
 * @param {string} toFormat - The target format
 * @returns {Promise<string>} The converted content
 */
export const convertContent = async (content, fromFormat, toFormat) => {
  if (fromFormat === toFormat) return content;
  
  try {
    // Convert to intermediate JSON if needed
    let jsonObj;
    switch (fromFormat.toLowerCase()) {
      case 'json':
        jsonObj = JSON.parse(content);
        break;
      // Add more parsers as needed
      default:
        return content; // No conversion available
    }
    
    // Convert from JSON to target format
    switch (toFormat.toLowerCase()) {
      case 'json':
        return JSON.stringify(jsonObj, null, 2);
      // Add more serializers as needed
      default:
        return content; // No conversion available
    }
  } catch (error) {
    console.error(`Error converting from ${fromFormat} to ${toFormat}:`, error);
    throw error;
  }
};
