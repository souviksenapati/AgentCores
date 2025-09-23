import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  LinearProgress,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm, Controller } from 'react-hook-form';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import DeleteIcon from '@mui/icons-material/Delete';
import { format } from 'date-fns';

import { agentAPI } from '../services/api';

const Agents = () => {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const { control, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery('agents', () => agentAPI.getAll(), {
    refetchOnWindowFocus: false, // Prevents reload on minimize/maximize
    refetchOnMount: true,        // Fresh data when navigating back
    staleTime: 1 * 60 * 1000,   // 1 minute - more frequent for management page
    cacheTime: 5 * 60 * 1000,   // 5 minutes in memory
  });

  const createMutation = useMutation(agentAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('agents');
      setOpen(false);
      reset();
    },
  });

  const startMutation = useMutation(agentAPI.start, {
    onSuccess: () => queryClient.invalidateQueries('agents'),
  });

  const stopMutation = useMutation(agentAPI.stop, {
    onSuccess: () => queryClient.invalidateQueries('agents'),
  });

  const deleteMutation = useMutation(agentAPI.delete, {
    onSuccess: () => queryClient.invalidateQueries('agents'),
  });

  const onSubmit = (data) => {
    createMutation.mutate({
      ...data,
      capabilities: data.capabilities ? data.capabilities.split(',').map(s => s.trim()) : [],
      configuration: {},
      resources: {},
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'success';
      case 'idle': return 'default';
      case 'error': return 'error';
      case 'paused': return 'warning';
      default: return 'default';
    }
  };

  const columns = [
    { field: 'name', headerName: 'Name', width: 200 },
    { field: 'agent_type', headerName: 'Type', width: 150 },
    { field: 'version', headerName: 'Version', width: 100 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={getStatusColor(params.value)}
          size="small"
        />
      ),
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 150,
      renderCell: (params) => format(new Date(params.value), 'MMM dd, yyyy'),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 200,
      sortable: false,
      renderCell: (params) => (
        <Box>
          {params.row.status === 'idle' || params.row.status === 'paused' ? (
            <IconButton
              size="small"
              onClick={() => startMutation.mutate(params.row.id)}
              color="success"
            >
              <PlayArrowIcon />
            </IconButton>
          ) : (
            <IconButton
              size="small"
              onClick={() => stopMutation.mutate(params.row.id)}
              color="warning"
            >
              <StopIcon />
            </IconButton>
          )}
          <IconButton
            size="small"
            onClick={() => deleteMutation.mutate(params.row.id)}
            color="error"
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  if (isLoading) return <LinearProgress />;

  const agents = data?.data?.agents || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Agents</Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
          >
            Quick Create
          </Button>
          <Button
            variant="contained"
            startIcon={<EditIcon />}
            href="/agents/create"
          >
            Advanced Create
          </Button>
        </Box>
      </Box>

      <Box style={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={agents}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10]}
          disableSelectionOnClick
        />
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Create New Agent</DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column" gap={2} mt={1}>
              <Controller
                name="name"
                control={control}
                rules={{ required: 'Name is required' }}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    label="Agent Name"
                    fullWidth
                    error={!!fieldState.error}
                    helperText={fieldState.error?.message}
                  />
                )}
              />

              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Description"
                    fullWidth
                    multiline
                    rows={3}
                  />
                )}
              />

              <Controller
                name="agent_type"
                control={control}
                rules={{ required: 'Agent type is required' }}
                render={({ field, fieldState }) => (
                  <FormControl fullWidth error={!!fieldState.error}>
                    <InputLabel>Agent Type</InputLabel>
                    <Select {...field} label="Agent Type">
                      <MenuItem value="gpt-4">GPT-4</MenuItem>
                      <MenuItem value="claude">Claude</MenuItem>
                      <MenuItem value="custom">Custom</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />

              <Controller
                name="capabilities"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Capabilities (comma-separated)"
                    fullWidth
                    placeholder="text_processing, api_calls, data_analysis"
                  />
                )}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isLoading}
            >
              Create
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Agents;