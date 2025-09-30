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
  Paper,
  List,
  ListItem,
  ListItemText,
  Tabs,
  Tab,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm, Controller } from 'react-hook-form';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import DeleteIcon from '@mui/icons-material/Delete';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';
import SettingsIcon from '@mui/icons-material/Settings';
import { format } from 'date-fns';

import { agentAPI } from '../services/api';

const Agents = () => {
  const [open, setOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settingsAgent, setSettingsAgent] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const queryClient = useQueryClient();
  const { control, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery('agents', () => agentAPI.getAll(), {
    refetchOnWindowFocus: false,
    refetchOnMount: true,
    staleTime: 1 * 60 * 1000,
    cacheTime: 5 * 60 * 1000,
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

  const openChat = async (agent) => {
    setSelectedAgent(agent);
    try {
      const response = await agentAPI.getChatHistory(agent.agent_id || agent.id);
      const history = response.data.messages || [];
      
      if (history.length === 0) {
        setMessages([{
          id: 1,
          text: `Hello! I'm ${agent.name}. How can I help you today?`,
          sender: 'agent',
          timestamp: new Date()
        }]);
      } else {
        setMessages(history.map(msg => ({
          id: msg.id,
          text: msg.message,
          sender: msg.sender,
          timestamp: new Date(msg.timestamp)
        })));
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setMessages([{
        id: 1,
        text: `Hello! I'm ${agent.name}. How can I help you today?`,
        sender: 'agent',
        timestamp: new Date()
      }]);
    }
    setChatOpen(true);
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedAgent) return;
    
    const userMessage = {
      id: Date.now(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    const messageToSend = newMessage;
    setNewMessage('');
    
    try {
      const response = await agentAPI.chat(selectedAgent.agent_id || selectedAgent.id, messageToSend);
      const agentResponse = {
        id: response.data.response.id,
        text: response.data.response.message,
        sender: 'agent',
        timestamp: new Date(response.data.response.timestamp)
      };
      setMessages(prev => [...prev, agentResponse]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorResponse = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error processing your message. Please try again.',
        sender: 'agent',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorResponse]);
    }
  };

  const closeChat = () => {
    setChatOpen(false);
    setSelectedAgent(null);
    setMessages([]);
    setNewMessage('');
  };

  const [availableAgents, setAvailableAgents] = useState([]);
  const [selectedConnections, setSelectedConnections] = useState([]);

  const openSettings = async (agent) => {
    setSettingsAgent(agent);
    setSelectedConnections(agent.connected_agents || []);
    
    try {
      const response = await agentAPI.getAvailableForConnection(agent.agent_id || agent.id);
      setAvailableAgents(response.data.agents || []);
    } catch (error) {
      console.error('Failed to load available agents:', error);
      setAvailableAgents([]);
    }
    
    setSettingsOpen(true);
    setActiveTab(0);
  };

  const closeSettings = () => {
    setSettingsOpen(false);
    setSettingsAgent(null);
    setActiveTab(0);
  };

  const saveSettings = async () => {
    if (!settingsAgent) return;
    
    try {
      const updateData = {
        connected_agents: selectedConnections
      };
      
      await agentAPI.update(settingsAgent.agent_id || settingsAgent.id, updateData);
      queryClient.invalidateQueries('agents');
      closeSettings();
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  const handleConnectionToggle = (agentId) => {
    setSelectedConnections(prev => 
      prev.includes(agentId) 
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  const columns = [
    { field: 'name', headerName: 'Name', width: 200 },
    { 
      field: 'agent_type', 
      headerName: 'Type', 
      width: 150,
      renderCell: (params) => {
        const type = params.value || params.row.config?.agent_type || params.row.config?.model || 'GPT-4';
        return type;
      }
    },
    { 
      field: 'version', 
      headerName: 'Version', 
      width: 100,
      renderCell: (params) => {
        const version = params.value || params.row.config?.version || '1.0.0';
        return version;
      }
    },
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
      width: 240,
      sortable: false,
      align: 'center',
      headerAlign: 'center',
      renderCell: (params) => (
        <Box display="flex" justifyContent="center" alignItems="center" gap={0.5}>
          {params.row.status === 'idle' || params.row.status === 'paused' ? (
            <IconButton
              size="small"
              onClick={() => startMutation.mutate(params.row.agent_id || params.row.id)}
              color="success"
              title="Start Agent"
            >
              <PlayArrowIcon />
            </IconButton>
          ) : (
            <IconButton
              size="small"
              onClick={() => stopMutation.mutate(params.row.agent_id || params.row.id)}
              color="warning"
              title="Stop Agent"
            >
              <StopIcon />
            </IconButton>
          )}
          <IconButton
            size="small"
            onClick={() => openChat(params.row)}
            color="primary"
            title="Chat with Agent"
          >
            <ChatIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => openSettings(params.row)}
            color="info"
            title="Agent Settings"
          >
            <SettingsIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => deleteMutation.mutate(params.row.agent_id || params.row.id)}
            color="error"
            title="Delete Agent"
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  if (isLoading) return <LinearProgress />;

  const agents = data?.agents || data?.data?.agents || [];

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
          getRowId={(row) => row.agent_id || row.id}
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
                      <MenuItem value="conversational">Conversational</MenuItem>
                      <MenuItem value="analytical">Analytical</MenuItem>
                      <MenuItem value="creative">Creative</MenuItem>
                      <MenuItem value="custom">Custom</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />

              <Controller
                name="model"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Model</InputLabel>
                    <Select {...field} label="Model" defaultValue="openrouter/meta-llama/llama-3.2-3b-instruct:free">
                      <MenuItem value="openrouter/meta-llama/llama-3.2-3b-instruct:free">Llama 3.2 3B (Free)</MenuItem>
                      <MenuItem value="openrouter/meta-llama/llama-3.2-1b-instruct:free">Llama 3.2 1B (Free)</MenuItem>
                      <MenuItem value="openrouter/qwen/qwen-2-7b-instruct:free">Qwen 2 7B (Free)</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />

              <Controller
                name="instructions"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Instructions"
                    fullWidth
                    multiline
                    rows={2}
                    defaultValue="You are a helpful AI assistant."
                  />
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

      {/* Chat Window Dialog */}
      <Dialog 
        open={chatOpen} 
        onClose={closeChat} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { height: '600px', display: 'flex', flexDirection: 'column' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Chat with {selectedAgent?.name}
          </Typography>
          <IconButton onClick={closeChat} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
          <Paper 
            sx={{ 
              flex: 1, 
              m: 2, 
              p: 1, 
              overflow: 'auto',
              backgroundColor: '#f5f5f5'
            }}
          >
            <List sx={{ p: 0 }}>
              {messages.map((message) => (
                <ListItem 
                  key={message.id}
                  sx={{
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    mb: 1
                  }}
                >
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: message.sender === 'user' ? '#1976d2' : '#fff',
                      color: message.sender === 'user' ? '#fff' : '#000'
                    }}
                  >
                    <ListItemText 
                      primary={message.text}
                      secondary={format(message.timestamp, 'HH:mm')}
                      secondaryTypographyProps={{
                        sx: { color: message.sender === 'user' ? 'rgba(255,255,255,0.7)' : 'text.secondary' }
                      }}
                    />
                  </Paper>
                </ListItem>
              ))}
            </List>
          </Paper>
        </DialogContent>
        
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <TextField
            fullWidth
            placeholder="Type your message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            variant="outlined"
            size="small"
          />
          <Button
            variant="contained"
            onClick={sendMessage}
            disabled={!newMessage.trim()}
            startIcon={<SendIcon />}
          >
            Send
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Window Dialog */}
      <Dialog 
        open={settingsOpen} 
        onClose={closeSettings} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { height: '500px', display: 'flex', flexDirection: 'column' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pb: 0 }}>
          <Typography variant="h6">
            Settings - {settingsAgent?.name}
          </Typography>
          <IconButton onClick={closeSettings} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="General" />
            <Tab label="Properties" />
            <Tab label="Integration" />
            <Tab label="Connect with Other Agent" />
          </Tabs>
        </Box>
        
        <DialogContent sx={{ flex: 1, p: 3 }}>
          {/* General Tab */}
          {activeTab === 0 && (
            <Box>
              <TextField
                fullWidth
                label="Name"
                defaultValue={settingsAgent?.name}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Description"
                defaultValue={settingsAgent?.description}
                multiline
                rows={3}
                margin="normal"
              />
            </Box>
          )}
          
          {/* Properties Tab */}
          {activeTab === 1 && (
            <Box>
              <TextField
                fullWidth
                label="Behavior"
                margin="normal"
                placeholder="Define agent behavior..."
              />
              <TextField
                fullWidth
                label="Capabilities"
                margin="normal"
                placeholder="List agent capabilities..."
              />
              <TextField
                fullWidth
                label="Memory"
                margin="normal"
                placeholder="Memory settings..."
              />
              <TextField
                fullWidth
                label="Context Window"
                margin="normal"
                placeholder="Context window size..."
              />
            </Box>
          )}
          
          {/* Integration Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>Available Integrations</Typography>
              <FormControlLabel
                control={<Checkbox />}
                label="Google Sheet"
              />
              <br />
              <FormControlLabel
                control={<Checkbox />}
                label="Google Ad"
              />
              <br />
              <FormControlLabel
                control={<Checkbox />}
                label="Many Products"
              />
            </Box>
          )}
          
          {/* Connect with Other Agent Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>Connect with Other Agents</Typography>
              {availableAgents.length === 0 ? (
                <Typography color="text.secondary">No other agents available for connection.</Typography>
              ) : (
                availableAgents.map((agent) => (
                  <FormControlLabel
                    key={agent.id}
                    control={
                      <Checkbox 
                        checked={selectedConnections.includes(agent.id)}
                        onChange={() => handleConnectionToggle(agent.id)}
                      />
                    }
                    label={`${agent.name} - ${agent.description || 'No description'}`}
                  />
                ))
              )}
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            onClick={saveSettings}
            color="primary"
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Agents;