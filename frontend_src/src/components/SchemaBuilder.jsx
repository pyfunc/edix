import React, { useState, useCallback } from 'react';
import { useEdix } from '../contexts/EdixContext';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Grid,
  IconButton,
  Divider,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  FormHelperText,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
} from '@mui/icons-material';

const fieldTypes = [
  { value: 'string', label: 'Text' },
  { value: 'number', label: 'Number' },
  { value: 'boolean', label: 'Boolean' },
  { value: 'date', label: 'Date' },
  { value: 'datetime', label: 'Date & Time' },
  { value: 'object', label: 'Object' },
  { value: 'array', label: 'Array' },
];

const SchemaBuilder = () => {
  const { createSchema } = useEdix();
  const [schema, setSchema] = useState({
    name: '',
    description: '',
    fields: [
      {
        name: '',
        type: 'string',
        required: true,
      },
    ],
  });
  const [errors, setErrors] = useState({});

  const validate = useCallback(() => {
    const newErrors = {};
    
    if (!schema.name.trim()) {
      newErrors.name = 'Schema name is required';
    }
    
    schema.fields.forEach((field, index) => {
      if (!field.name.trim()) {
        newErrors[`field-${index}-name`] = 'Field name is required';
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [schema]);

  const handleAddField = () => {
    setSchema(prev => ({
      ...prev,
      fields: [
        ...prev.fields,
        {
          name: '',
          type: 'string',
          required: true,
        },
      ],
    }));
  };

  const handleRemoveField = (index) => {
    setSchema(prev => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index),
    }));
  };

  const handleFieldChange = (index, field) => {
    const newFields = [...schema.fields];
    newFields[index] = { ...newFields[index], ...field };
    setSchema(prev => ({
      ...prev,
      fields: newFields,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await createSchema(schema);
      // Reset form on success
      setSchema({
        name: '',
        description: '',
        fields: [
          {
            name: '',
            type: 'string',
            required: true,
          },
        ],
      });
    } catch (error) {
      console.error('Failed to create schema:', error);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Create New Schema
      </Typography>
      
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Schema Name"
              value={schema.name}
              onChange={(e) => setSchema({ ...schema, name: e.target.value })}
              error={!!errors.name}
              helperText={errors.name}
              margin="normal"
              required
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={schema.description}
              onChange={(e) => setSchema({ ...schema, description: e.target.value })}
              margin="normal"
              multiline
              rows={2}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Fields
              </Typography>
            </Divider>
            
            {schema.fields.map((field, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #eee', borderRadius: 1 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={5}>
                    <TextField
                      fullWidth
                      label="Field Name"
                      value={field.name}
                      onChange={(e) => handleFieldChange(index, { name: e.target.value })}
                      error={!!errors[`field-${index}-name`]}
                      helperText={errors[`field-${index}-name`]}
                      size="small"
                      required
                    />
                  </Grid>
                  
                  <Grid item xs={4}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Type</InputLabel>
                      <Select
                        value={field.type}
                        label="Type"
                        onChange={(e) => handleFieldChange(index, { type: e.target.value })}
                      >
                        {fieldTypes.map((type) => (
                          <MenuItem key={type.value} value={type.value}>
                            {type.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={2}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={field.required}
                          onChange={(e) => handleFieldChange(index, { required: e.target.checked })}
                        />
                      }
                      label="Required"
                      componentsProps={{
                        typography: { variant: 'body2' },
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={1} sx={{ textAlign: 'right' }}>
                    <IconButton
                      size="small"
                      onClick={() => handleRemoveField(index)}
                      color="error"
                      disabled={schema.fields.length === 1}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Grid>
                </Grid>
              </Box>
            ))}
            
            <Button
              startIcon={<AddIcon />}
              onClick={handleAddField}
              size="small"
              sx={{ mt: 1 }}
            >
              Add Field
            </Button>
          </Grid>
          
          <Grid item xs={12} sx={{ mt: 2, textAlign: 'right' }}>
            <Button
              type="submit"
              variant="contained"
              startIcon={<SaveIcon />}
              disabled={schema.fields.some(f => !f.name.trim())}
            >
              Save Schema
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default SchemaBuilder;
