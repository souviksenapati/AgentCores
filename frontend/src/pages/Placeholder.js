import React from 'react';
import { Box, Typography } from '@mui/material';

export default function Placeholder({ title = 'Coming Soon', description = 'This page is under construction.' }) {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>{title}</Typography>
      <Typography color="text.secondary">{description}</Typography>
    </Box>
  );
}
