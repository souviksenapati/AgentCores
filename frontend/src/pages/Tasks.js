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
  IconButton,
  LinearProgress,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm, Controller } from 'react-hook-form';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { format } from 'date-fns';

import { taskAPI, agentAPI } from '../services/api';

const Tasks = () => {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const { control, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery('tasks', () => taskAPI.getAll());
  const { data: agentsData } = useQuery('agents', () => agentAPI.getAll());

  const createMutation = useMutation(taskAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('tasks');
      setOpen(false);
      reset();
    },
  });

  const executeMutation = useMutation(taskAPI.execute, {
    onSuccess: () => queryClient.invalidateQueries('tasks'),
  });

  const onSubmit = (data) => {
    const inputData = {};
    try {
      if (data.input_data) {
        Object.assign(inputData, JSON.parse(data.input_data));
      }
    } catch (e) {
      // If JSON parsing fails, treat as simple text input
      inputData.text = data.input_data;
    }

    createMutation.mutate({
      ...data,
      input_data: inputData,
    });
  };

  const columns = [
    { field: 'name', headerName: 'Name', width: 200 },
    { field: 'task_type', headerName: 'Type', width: 150 },
    { field: 'priority', headerName: 'Priority', width: 100 },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 150,
      renderCell: (params) => format(new Date(params.value), 'MMM dd, yyyy'),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <IconButton
          size="small"
          onClick={() => executeMutation.mutate(params.row.id)}
          color="primary"
        >
          <PlayArrowIcon />
        </IconButton>
      ),
    },
  ];

  if (isLoading) return <LinearProgress />;

  const tasks = data?.data?.tasks || [];
  const agents = agentsData?.data?.agents || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Tasks</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Create Task
        </Button>
      </Box>

      <Box style={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={tasks}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10]}
          disableSelectionOnClick
        />
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Create New Task</DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column" gap={2} mt={1}>
              <Controller
                name="name"
                control={control}
                rules={{ required: 'Name is required' }}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    label="Task Name"
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
                    rows={2}
                  />
                )}
              />

              <Controller
                name="agent_id"
                control={control}
                rules={{ required: 'Agent is required' }}
                render={({ field, fieldState }) => (
                  <FormControl fullWidth error={!!fieldState.error}>
                    <InputLabel>Agent</InputLabel>
                    <Select {...field} label="Agent">
                      {agents.map((agent) => (
                        <MenuItem key={agent.id} value={agent.id}>
                          {agent.name} ({agent.agent_type})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />

              <Controller
                name="task_type"
                control={control}
                rules={{ required: 'Task type is required' }}
                render={({ field, fieldState }) => (
                  <FormControl fullWidth error={!!fieldState.error}>
                    <InputLabel>Task Type</InputLabel>
                    <Select {...field} label="Task Type">
                      <MenuItem value="text_processing">Text Processing</MenuItem>
                      <MenuItem value="api_call">API Call</MenuItem>
                      <MenuItem value="workflow">Workflow</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />

              <Controller
                name="input_data"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Input Data (JSON or text)"
                    fullWidth
                    multiline
                    rows={4}
                    placeholder='{"text": "Hello world", "operation": "uppercase"}'
                  />
                )}
              />

              <Controller
                name="priority"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Priority</InputLabel>
                    <Select {...field} label="Priority" defaultValue={1}>
                      <MenuItem value={1}>Low</MenuItem>
                      <MenuItem value={2}>Medium</MenuItem>
                      <MenuItem value={3}>High</MenuItem>
                      <MenuItem value={4}>Urgent</MenuItem>
                      <MenuItem value={5}>Critical</MenuItem>
                    </Select>
                  </FormControl>
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

export default Tasks;