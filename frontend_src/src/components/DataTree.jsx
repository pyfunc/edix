import React, { useState } from 'react';
import { TreeView, TreeItem } from '@mui/lab';
import { Box, Typography, Paper } from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';

const DataTree = ({ data, activeItem, onSelectItem }) => {
  const [expanded, setExpanded] = useState(['root']);

  const handleToggle = (event, nodeIds) => {
    setExpanded(nodeIds);
  };

  const handleSelect = (event, nodeId) => {
    if (nodeId !== 'root') {
      onSelectItem(nodeId);
    }
  };

  // Group items by their first level key for better organization
  const groupedData = data.reduce((acc, item) => {
    const type = item.type || 'Other';
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(item);
    return acc;
  }, {});

  return (
    <Paper sx={{ height: '100%', overflow: 'auto' }}>
      <Box sx={{ p: 1, borderBottom: '1px solid #eee' }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
          Items
        </Typography>
      </Box>
      
      <TreeView
        defaultCollapseIcon={<ExpandMoreIcon />}
        defaultExpandIcon={<ChevronRightIcon />}
        expanded={expanded}
        onNodeToggle={handleToggle}
        onNodeSelect={handleSelect}
        selected={activeItem || ''}
        sx={{ flexGrow: 1, overflowY: 'auto', p: 1 }}
      >
        <TreeItem nodeId="root" label="Data Items" sx={{ '& > .MuiTreeItem-content': { p: 0.5 } }}>
          {Object.entries(groupedData).map(([type, items]) => (
            <TreeItem
              key={type}
              nodeId={`group-${type}`}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FolderIcon sx={{ fontSize: 16, mr: 0.5 }} />
                  <Typography variant="body2">
                    {type} ({items.length})
                  </Typography>
                </Box>
              }
              sx={{ '& > .MuiTreeItem-content': { p: 0 } }}
            >
              {items.map((item) => (
                <TreeItem
                  key={item.id}
                  nodeId={String(item.id)}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <FileIcon sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
                      <Typography variant="body2" noWrap>
                        {item.name || `Item ${item.id}`}
                      </Typography>
                    </Box>
                  }
                  sx={{
                    '& .MuiTreeItem-content': {
                      p: 0,
                      pl: 2,
                      '&.Mui-selected, &.Mui-selected.Mui-focused': {
                        backgroundColor: 'primary.light',
                      },
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    },
                  }}
                />
              ))}
            </TreeItem>
          ))}
        </TreeItem>
      </TreeView>
    </Paper>
  );
};

export default DataTree;
