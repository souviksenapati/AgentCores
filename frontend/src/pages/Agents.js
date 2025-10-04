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

// OpenRouter free models - verified working models only (Updated 2025-01-03)
const OPENROUTER_FREE_MODELS = [
  // Top Performers - Large Models
  { value: 'openrouter/meta-llama/llama-3.3-70b-instruct:free', label: 'Llama 3.3 70B - 65K Context (Free)' },
  { value: 'openrouter/meta-llama/llama-4-maverick:free', label: 'Llama 4 Maverick - 128K Context (Free)' },
  { value: 'openrouter/qwen/qwen-2.5-72b-instruct:free', label: 'Qwen2.5 72B - 32K Context (Free)' },
  { value: 'openrouter/mistralai/mistral-small-3.2-24b-instruct:free', label: 'Mistral Small 3.2 - 131K Context (Free)' },
  
  // Balanced Performance
  { value: 'openrouter/google/gemma-3-27b-it:free', label: 'Gemma 3 27B - 96K Context (Free)' },
  { value: 'openrouter/google/gemma-3-12b-it:free', label: 'Gemma 3 12B - 32K Context (Free)' },
  { value: 'openrouter/nvidia/nemotron-nano-9b-v2:free', label: 'NVIDIA Nemotron 9B - 128K Context (Free)' },
  
  // Reliable & Fast
  { value: 'openrouter/deepseek/deepseek-chat-v3.1:free', label: 'DeepSeek Chat v3.1 - 164K Context (Free)' },
  { value: 'openrouter/meta-llama/llama-3.3-8b-instruct:free', label: 'Llama 3.3 8B - 128K Context (Free)' },
  { value: 'openrouter/mistralai/mistral-nemo:free', label: 'Mistral Nemo - 131K Context (Free)' }
];

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
    
    // Initialize form data with current agent values
    const currentConfig = agent.config ? 
      (typeof agent.config === 'string' ? JSON.parse(agent.config) : agent.config) : {};
    
    // Normalize agent_type from config
    let agentType = currentConfig.agent_type || 'conversational';
    // Map old values to new expected values
    if (agentType === 'claude-3') agentType = 'conversational';
    
    setSettingsFormData({
      name: agent.name || '',
      description: agent.description || '',
      agent_type: agentType,
      model: currentConfig.model || 'openrouter/deepseek/deepseek-chat-v3.1:free',
      instructions: currentConfig.instructions || 'You are a helpful AI assistant.',
      temperature: currentConfig.temperature || 0.7,
      max_tokens: currentConfig.max_tokens || 1000,
      top_p: currentConfig.top_p || 1.0,
      frequency_penalty: currentConfig.frequency_penalty || 0.0,
      presence_penalty: currentConfig.presence_penalty || 0.0,
      memory_enabled: currentConfig.memory_enabled !== false,
      content_filter: currentConfig.content_filter !== false,
      context_window: currentConfig.context_window || 4000,
      max_memory_messages: currentConfig.max_memory_messages || 50,
      response_style: currentConfig.response_style || 'balanced',
      personality: currentConfig.personality || 'professional',
      safety_level: currentConfig.safety_level || 'standard',
      response_timeout: currentConfig.response_timeout || 30,
      rate_limit: currentConfig.rate_limit || 60
    });
    
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



  const [settingsFormData, setSettingsFormData] = useState({});

  const handleSettingsChange = (field, value) => {
    setSettingsFormData(prev => ({ ...prev, [field]: value }));
  };

  const saveSettings = async () => {
    if (!settingsAgent) {
      console.error('No agent selected for settings update');
      return;
    }
    
    try {
      const agentId = settingsAgent.agent_id || settingsAgent.id;
      if (!agentId) {
        throw new Error('Agent ID is missing');
      }

      const currentConfig = settingsAgent.config ? 
        (typeof settingsAgent.config === 'string' ? JSON.parse(settingsAgent.config) : settingsAgent.config) : {};
      
      // Only send fields that have actually changed or are required
      const updateData = {};
      
      // Basic fields
      if (settingsFormData.name && settingsFormData.name !== settingsAgent.name) {
        updateData.name = settingsFormData.name;
      }
      if (settingsFormData.description !== undefined && settingsFormData.description !== settingsAgent.description) {
        updateData.description = settingsFormData.description;
      }
      if (settingsFormData.agent_type && settingsFormData.agent_type !== currentConfig.agent_type) {
        updateData.agent_type = settingsFormData.agent_type;
      }
      
      // Model and AI settings
      if (settingsFormData.model && settingsFormData.model !== currentConfig.model) {
        updateData.model = settingsFormData.model;
      }
      if (settingsFormData.instructions !== undefined && settingsFormData.instructions !== currentConfig.instructions) {
        updateData.instructions = settingsFormData.instructions;
      }
      
      // Numeric parameters with proper validation
      if (settingsFormData.temperature !== undefined) {
        const temp = parseFloat(settingsFormData.temperature);
        if (!isNaN(temp) && temp >= 0 && temp <= 2) {
          updateData.temperature = temp;
        }
      }
      if (settingsFormData.max_tokens !== undefined) {
        const tokens = parseInt(settingsFormData.max_tokens);
        if (!isNaN(tokens) && tokens > 0 && tokens <= 8000) {
          updateData.max_tokens = tokens;
        }
      }
      if (settingsFormData.top_p !== undefined) {
        const topP = parseFloat(settingsFormData.top_p);
        if (!isNaN(topP) && topP >= 0 && topP <= 1) {
          updateData.top_p = topP;
        }
      }
      if (settingsFormData.frequency_penalty !== undefined) {
        const freq = parseFloat(settingsFormData.frequency_penalty);
        if (!isNaN(freq) && freq >= -2 && freq <= 2) {
          updateData.frequency_penalty = freq;
        }
      }
      if (settingsFormData.presence_penalty !== undefined) {
        const pres = parseFloat(settingsFormData.presence_penalty);
        if (!isNaN(pres) && pres >= -2 && pres <= 2) {
          updateData.presence_penalty = pres;
        }
      }
      
      // Boolean settings
      if (settingsFormData.memory_enabled !== undefined) {
        updateData.memory_enabled = Boolean(settingsFormData.memory_enabled);
      }
      if (settingsFormData.content_filter !== undefined) {
        updateData.content_filter = Boolean(settingsFormData.content_filter);
      }
      
      // Memory and context settings
      if (settingsFormData.context_window !== undefined) {
        const context = parseInt(settingsFormData.context_window);
        if (!isNaN(context) && context > 0) {
          updateData.context_window = context;
        }
      }
      if (settingsFormData.max_memory_messages !== undefined) {
        const memMsg = parseInt(settingsFormData.max_memory_messages);
        if (!isNaN(memMsg) && memMsg > 0) {
          updateData.max_memory_messages = memMsg;
        }
      }
      
      // Style and personality settings
      if (settingsFormData.response_style && settingsFormData.response_style !== currentConfig.response_style) {
        updateData.response_style = settingsFormData.response_style;
      }
      if (settingsFormData.personality && settingsFormData.personality !== currentConfig.personality) {
        updateData.personality = settingsFormData.personality;
      }
      if (settingsFormData.safety_level && settingsFormData.safety_level !== currentConfig.safety_level) {
        updateData.safety_level = settingsFormData.safety_level;
      }
      
      // Performance settings
      if (settingsFormData.response_timeout !== undefined) {
        const timeout = parseInt(settingsFormData.response_timeout);
        if (!isNaN(timeout) && timeout > 0) {
          updateData.response_timeout = timeout;
        }
      }
      if (settingsFormData.rate_limit !== undefined) {
        const rateLimit = parseInt(settingsFormData.rate_limit);
        if (!isNaN(rateLimit) && rateLimit > 0) {
          updateData.rate_limit = rateLimit;
        }
      }
      
      // Connected agents
      if (selectedConnections && Array.isArray(selectedConnections)) {
        updateData.connected_agents = selectedConnections;
      }
      
      // Only make API call if there are changes to save
      if (Object.keys(updateData).length === 0) {
        closeSettings();
        return;
      }
      
      await agentAPI.update(agentId, updateData);
      
      // Refresh the agents list to show updated data
      await queryClient.invalidateQueries('agents');
      
      // Clear form data and close dialog
      setSettingsFormData({});
      closeSettings();
      
    } catch (error) {
      console.error('❌ FAILED to save settings:', error);
      console.error('❌ Error Details:', {
        message: error.message,
        response: error.response,
        request: error.request,
        config: error.config
      });
      
      let errorMessage = 'Failed to save settings. Please try again.';
      
      if (error.response) {
        // Server responded with error
        if (error.response.status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
        } else if (error.response.status === 404) {
          errorMessage = 'Agent not found. Please refresh and try again.';
        } else if (error.response.status === 400) {
          errorMessage = 'Invalid data provided. Please check your inputs.';
        } else if (error.response.data && error.response.data.detail) {
          errorMessage = `Error: ${error.response.data.detail}`;
        }
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error. Check if backend container is running on port 8000.';
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }
      alert(errorMessage);
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
                    <Select {...field} label="Model" defaultValue="openrouter/deepseek/deepseek-chat-v3.1:free">
                      {/* Verified Working Free Models */}
                      
                      {OPENROUTER_FREE_MODELS.map((model) => (
                        <MenuItem key={model.value} value={model.value}>
                          {model.label}
                        </MenuItem>
                      ))}
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
          sx: { height: '600px', display: 'flex', flexDirection: 'column' }
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
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} variant="scrollable">
            <Tab label="General" />
            <Tab label="Behavior" />
            <Tab label="Parameters" />
            <Tab label="Memory" />
            <Tab label="MCP Servers" />
            <Tab label="Connections" />
            <Tab label="Advanced" />
          </Tabs>
        </Box>
        
        <DialogContent sx={{ flex: 1, p: 3 }}>
          {/* General Tab */}
          {activeTab === 0 && (
            <Box>
              <TextField
                fullWidth
                label="Name"
                value={settingsFormData.name || settingsAgent?.name || ''}
                onChange={(e) => handleSettingsChange('name', e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Description"
                value={settingsFormData.description || settingsAgent?.description || ''}
                onChange={(e) => handleSettingsChange('description', e.target.value)}
                multiline
                rows={3}
                margin="normal"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Agent Type</InputLabel>
                <Select 
                  value={settingsFormData.agent_type || 'conversational'}
                  onChange={(e) => handleSettingsChange('agent_type', e.target.value)}
                >
                  <MenuItem value="conversational">Conversational</MenuItem>
                  <MenuItem value="analytical">Analytical</MenuItem>
                  <MenuItem value="creative">Creative</MenuItem>
                  <MenuItem value="technical">Technical</MenuItem>
                  <MenuItem value="customer_service">Customer Service</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth margin="normal">
                <InputLabel>Model</InputLabel>
                <Select 
                  value={settingsFormData.model || 'openrouter/deepseek/deepseek-chat-v3.1:free'}
                  onChange={(e) => handleSettingsChange('model', e.target.value)}
                >
                  {OPENROUTER_FREE_MODELS.map((model) => (
                    <MenuItem key={model.value} value={model.value}>
                      {model.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          )}
          
          {/* Behavior Tab */}
          {activeTab === 1 && (
            <Box>
              <TextField
                fullWidth
                label="System Instructions"
                defaultValue={
                  settingsAgent?.config?.instructions || 
                  (typeof settingsAgent?.config === 'string' ? JSON.parse(settingsAgent.config)?.instructions : null) ||
                  'You are a helpful AI assistant.'
                }
                onChange={(e) => handleSettingsChange('instructions', e.target.value)}
                multiline
                rows={4}
                margin="normal"
                helperText="Define how the agent should behave and respond"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Personality</InputLabel>
                <Select 
                  defaultValue="professional"
                  onChange={(e) => handleSettingsChange('personality', e.target.value)}
                >
                  <MenuItem value="friendly">Friendly</MenuItem>
                  <MenuItem value="professional">Professional</MenuItem>
                  <MenuItem value="casual">Casual</MenuItem>
                  <MenuItem value="formal">Formal</MenuItem>
                  <MenuItem value="creative">Creative</MenuItem>
                  <MenuItem value="analytical">Analytical</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth margin="normal">
                <InputLabel>Response Style</InputLabel>
                <Select 
                  defaultValue="balanced"
                  onChange={(e) => handleSettingsChange('response_style', e.target.value)}
                >
                  <MenuItem value="concise">Concise</MenuItem>
                  <MenuItem value="balanced">Balanced</MenuItem>
                  <MenuItem value="detailed">Detailed</MenuItem>
                  <MenuItem value="step_by_step">Step-by-step</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth margin="normal">
                <InputLabel>Safety Level</InputLabel>
                <Select 
                  defaultValue="standard"
                  onChange={(e) => handleSettingsChange('safety_level', e.target.value)}
                >
                  <MenuItem value="permissive">Permissive</MenuItem>
                  <MenuItem value="standard">Standard</MenuItem>
                  <MenuItem value="strict">Strict</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={
                  <Checkbox 
                    defaultChecked 
                    onChange={(e) => handleSettingsChange('content_filter', e.target.checked)}
                  />
                }
                label="Enable Content Filter"
              />
              <TextField
                fullWidth
                label="Blocked Topics"
                placeholder="politics, violence, illegal activities"
                onChange={(e) => handleSettingsChange('blocked_topics', e.target.value)}
                margin="normal"
                helperText="Comma-separated list of topics to avoid"
              />
            </Box>
          )}
          
          {/* Parameters Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>AI Model Parameters</Typography>
              <Box display="flex" gap={2}>
                <TextField
                  label="Temperature"
                  type="number"
                  defaultValue={
                    settingsAgent?.config?.temperature || 
                    (typeof settingsAgent?.config === 'string' ? JSON.parse(settingsAgent.config)?.temperature : null) ||
                    0.7
                  }
                  onChange={(e) => handleSettingsChange('temperature', e.target.value)}
                  inputProps={{ min: 0, max: 2, step: 0.1 }}
                  margin="normal"
                  helperText="Creativity (0-2)"
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Max Tokens"
                  type="number"
                  defaultValue={
                    settingsAgent?.config?.max_tokens || 
                    (typeof settingsAgent?.config === 'string' ? JSON.parse(settingsAgent.config)?.max_tokens : null) ||
                    1000
                  }
                  onChange={(e) => handleSettingsChange('max_tokens', e.target.value)}
                  inputProps={{ min: 100, max: 8000 }}
                  margin="normal"
                  helperText="Response length"
                  sx={{ flex: 1 }}
                />
              </Box>
              <Box display="flex" gap={2}>
                <TextField
                  label="Top P"
                  type="number"
                  defaultValue={1.0}
                  onChange={(e) => handleSettingsChange('top_p', e.target.value)}
                  inputProps={{ min: 0, max: 1, step: 0.1 }}
                  margin="normal"
                  helperText="Nucleus sampling"
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Frequency Penalty"
                  type="number"
                  defaultValue={0.0}
                  onChange={(e) => handleSettingsChange('frequency_penalty', e.target.value)}
                  inputProps={{ min: -2, max: 2, step: 0.1 }}
                  margin="normal"
                  helperText="Reduce repetition"
                  sx={{ flex: 1 }}
                />
              </Box>
              <TextField
                label="Presence Penalty"
                type="number"
                defaultValue={0.0}
                onChange={(e) => handleSettingsChange('presence_penalty', e.target.value)}
                inputProps={{ min: -2, max: 2, step: 0.1 }}
                margin="normal"
                helperText="Encourage new topics"
                fullWidth
              />
            </Box>
          )}
          
          {/* Memory Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>Memory Configuration</Typography>
              <FormControlLabel
                control={
                  <Checkbox 
                    defaultChecked 
                    onChange={(e) => handleSettingsChange('memory_enabled', e.target.checked)}
                  />
                }
                label="Enable Conversation Memory"
              />
              <FormControlLabel
                control={<Checkbox name="long_term_memory" />}
                label="Enable Long-term Memory"
              />
              <TextField
                fullWidth
                label="Context Window"
                type="number"
                defaultValue={4000}
                onChange={(e) => handleSettingsChange('context_window', e.target.value)}
                inputProps={{ min: 1000, max: 32000 }}
                margin="normal"
                helperText="Maximum context size for conversations"
              />
              <TextField
                fullWidth
                label="Max Memory Messages"
                type="number"
                defaultValue={50}
                onChange={(e) => handleSettingsChange('max_memory_messages', e.target.value)}
                inputProps={{ min: 10, max: 1000 }}
                margin="normal"
                helperText="Number of previous messages to remember"
              />
              <TextField
                fullWidth
                name="memory_retention"
                label="Memory Retention (days)"
                type="number"
                defaultValue={30}
                inputProps={{ min: 1, max: 365 }}
                margin="normal"
                helperText="How long to keep conversation history"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Memory Priority</InputLabel>
                <Select name="memory_priority" defaultValue="balanced">
                  <MenuItem value="recent">Recent Messages</MenuItem>
                  <MenuItem value="important">Important Context</MenuItem>
                  <MenuItem value="balanced">Balanced</MenuItem>
                  <MenuItem value="semantic">Semantic Similarity</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
          
          {/* MCP Servers Tab */}
          {activeTab === 4 && (
            <Box>
              <Typography variant="h6" gutterBottom>MCP (Model Context Protocol) Servers</Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Connect your agent to external tools and services through standardized MCP servers.
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom>Productivity Tools</Typography>
              <Box display="flex" flexDirection="column" gap={1} mb={3}>
                <FormControlLabel control={<Checkbox name="mcp_google_sheets" />} label="Google Sheets - Read/write spreadsheets" />
                <FormControlLabel control={<Checkbox name="mcp_google_drive" />} label="Google Drive - File management" />
                <FormControlLabel control={<Checkbox name="mcp_google_calendar" />} label="Google Calendar - Schedule management" />
                <FormControlLabel control={<Checkbox name="mcp_notion" />} label="Notion - Database operations" />
                <FormControlLabel control={<Checkbox name="mcp_airtable" />} label="Airtable - Database management" />
              </Box>
              
              <Typography variant="subtitle1" gutterBottom>Communication</Typography>
              <Box display="flex" flexDirection="column" gap={1} mb={3}>
                <FormControlLabel control={<Checkbox name="mcp_slack" />} label="Slack - Team communication" />
                <FormControlLabel control={<Checkbox name="mcp_discord" />} label="Discord - Community management" />
                <FormControlLabel control={<Checkbox name="mcp_teams" />} label="Microsoft Teams - Enterprise chat" />
                <FormControlLabel control={<Checkbox name="mcp_email" />} label="Email - Send/receive emails" />
              </Box>
              
              <Typography variant="subtitle1" gutterBottom>Development Tools</Typography>
              <Box display="flex" flexDirection="column" gap={1} mb={3}>
                <FormControlLabel control={<Checkbox name="mcp_github" />} label="GitHub - Repository management" />
                <FormControlLabel control={<Checkbox name="mcp_gitlab" />} label="GitLab - Code collaboration" />
                <FormControlLabel control={<Checkbox name="mcp_jira" />} label="Jira - Issue tracking" />
                <FormControlLabel control={<Checkbox name="mcp_linear" />} label="Linear - Project management" />
              </Box>
              
              <Typography variant="subtitle1" gutterBottom>Data & Analytics</Typography>
              <Box display="flex" flexDirection="column" gap={1} mb={3}>
                <FormControlLabel control={<Checkbox name="mcp_postgresql" />} label="PostgreSQL - Database queries" />
                <FormControlLabel control={<Checkbox name="mcp_mysql" />} label="MySQL - Database operations" />
                <FormControlLabel control={<Checkbox name="mcp_mongodb" />} label="MongoDB - Document database" />
                <FormControlLabel control={<Checkbox name="mcp_redis" />} label="Redis - Cache operations" />
              </Box>
              
              <Typography variant="subtitle1" gutterBottom>Utilities</Typography>
              <Box display="flex" flexDirection="column" gap={1} mb={3}>
                <FormControlLabel control={<Checkbox name="mcp_web_search" />} label="Web Search - Internet search" />
                <FormControlLabel control={<Checkbox name="mcp_calculator" />} label="Calculator - Mathematical operations" />
                <FormControlLabel control={<Checkbox name="mcp_weather" />} label="Weather - Weather information" />
                <FormControlLabel control={<Checkbox name="mcp_translator" />} label="Translator - Language translation" />
              </Box>
              
              <TextField
                fullWidth
                name="custom_mcp_servers"
                label="Custom MCP Server URLs"
                placeholder="https://mcp.example.com/server1, https://mcp.example.com/server2"
                margin="normal"
                helperText="Comma-separated list of custom MCP server endpoints"
              />
            </Box>
          )}
          

          
          {/* Connections Tab */}
          {activeTab === 5 && (
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
          
          {/* Advanced Tab */}
          {activeTab === 6 && (
            <Box>
              <Typography variant="h6" gutterBottom>Advanced Settings</Typography>
              <TextField
                fullWidth
                name="custom_prompt"
                label="Custom System Prompt"
                multiline
                rows={4}
                margin="normal"
                placeholder="Additional system instructions..."
                helperText="Advanced prompt engineering (overrides default instructions)"
              />
              <TextField
                fullWidth
                label="Rate Limit (requests/minute)"
                type="number"
                defaultValue={60}
                onChange={(e) => handleSettingsChange('rate_limit', e.target.value)}
                inputProps={{ min: 1, max: 1000 }}
                margin="normal"
                helperText="Maximum requests per minute for this agent"
              />
              <TextField
                fullWidth
                label="Response Timeout (seconds)"
                type="number"
                defaultValue={30}
                onChange={(e) => handleSettingsChange('response_timeout', e.target.value)}
                inputProps={{ min: 5, max: 300 }}
                margin="normal"
                helperText="Maximum time to wait for agent response"
              />
              <TextField
                fullWidth
                name="tags"
                label="Tags"
                placeholder="customer-service, technical, beta"
                margin="normal"
                helperText="Comma-separated tags for organization"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Collaboration Mode</InputLabel>
                <Select name="collaboration_mode" defaultValue="independent">
                  <MenuItem value="independent">Independent</MenuItem>
                  <MenuItem value="collaborative">Collaborative</MenuItem>
                  <MenuItem value="hierarchical">Hierarchical</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={<Checkbox name="auto_pause" />}
                label="Auto-pause when inactive"
              />
              <FormControlLabel
                control={<Checkbox name="debug_logging" />}
                label="Enable debug logging"
              />
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 2, justifyContent: 'flex-end' }}>
          <Button onClick={closeSettings} sx={{ mr: 1 }}>Cancel</Button>
          <Button
            variant="contained"
            onClick={saveSettings}
            color="primary"
          >
            Save Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Agents;