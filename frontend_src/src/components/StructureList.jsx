import React from 'react';
import { List, ListItem, ListItemText, ListItemIcon, Typography, Paper } from '@mui/material';
import { Folder as FolderIcon, InsertDriveFile as FileIcon } from '@mui/icons-material';

const StructureList = ({ structures, activeStructure, onSelectStructure }) => {
  return (
    <Paper sx={{ height: '100%', overflow: 'auto' }}>
      <List dense>
        <Typography variant="subtitle2" sx={{ p: 1, fontWeight: 'bold', bgcolor: '#f5f5f5' }}>
          Data Structures
        </Typography>
        
        {structures.length === 0 ? (
          <Typography variant="body2" sx={{ p: 2, color: 'text.secondary' }}>
            No structures found
          </Typography>
        ) : (
          structures.map((structure) => (
            <ListItem
              button
              key={structure.name}
              selected={activeStructure === structure.name}
              onClick={() => onSelectStructure(structure.name)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                {structure.schema_name ? <FileIcon /> : <FolderIcon />}
              </ListItemIcon>
              <ListItemText
                primary={structure.name}
                secondary={structure.description || 'No description'}
                primaryTypographyProps={{
                  variant: 'body2',
                  noWrap: true,
                }}
                secondaryTypographyProps={{
                  variant: 'caption',
                  noWrap: true,
                }}
              />
            </ListItem>
          ))
        )}
      </List>
    </Paper>
  );
};

export default StructureList;
