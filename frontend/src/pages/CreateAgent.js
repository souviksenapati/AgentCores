import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Container,
  Grid,
  Alert,
  Chip,
  Stepper,
  Step,
  StepLabel,
  FormControlLabel,
  Switch,
  Slider,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from 'react-query';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import SmartToyIcon from '@mui/icons-material/SmartToy';

import { agentAPI } from '../services/api';

const steps = ['Basic Information', 'Configuration', 'Capabilities', 'Review'];

const CreateAgent = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // Use simple state instead of React Hook Form to avoid conflicts
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    agent_type: '',
    version: '',
    capabilities: [],
    temperature: 0.7,
    max_tokens: '',
    timeout: '',
    auto_start: false,
    priority: 'normal',
    memory_limit: '',
    concurrent_tasks: '',
  });

  const createMutation = useMutation(agentAPI.create, {
    onSuccess: (data) => {
      console.log('✅ Agent created successfully:', data);
      queryClient.invalidateQueries('agents');
      navigate('/agents');
    },
    onError: (error) => {
      console.error('❌ Agent creation failed:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to create agent');
    },
  });

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const updateField = (fieldName, value) => {
    console.log(`Updating ${fieldName}:`, value);
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const onSubmit = () => {
    console.log('🚀 Form submitted with data:', formData);
    
    const agentData = {
      name: formData.name || 'Unnamed Agent',
      description: formData.description || 'No description provided',
      agent_type: formData.agent_type || 'gpt-4',
      version: formData.version || '1.0.0',
      capabilities: formData.capabilities || [],
      configuration: {
        temperature: formData.temperature || 0.7,
        max_tokens: parseInt(formData.max_tokens) || 2048,
        timeout: parseInt(formData.timeout) || 30,
        auto_start: formData.auto_start || false,
        priority: formData.priority || 'normal',
      },
      resources: {
        memory_limit: parseInt(formData.memory_limit) || 512,
        concurrent_tasks: parseInt(formData.concurrent_tasks) || 1,
      },
    };
    
    console.log('📤 Sending agent data to API:', agentData);
    setError('');
    createMutation.mutate(agentData);
  };

  const availableCapabilities = [
    'text_processing',
    'api_calls',
    'data_analysis',
    'image_processing',
    'web_scraping',
    'email_handling',
    'file_management',
    'database_operations',
    'natural_language',
    'code_generation',
    'translation',
    'summarization',
  ];

  const agentTypes = [
    { value: 'gpt-4', label: 'GPT-4 (OpenAI)', description: 'Advanced reasoning and complex tasks' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo (OpenAI)', description: 'Fast and efficient for most tasks' },
    { value: 'claude-3', label: 'Claude 3 (Anthropic)', description: 'Strong analytical and writing capabilities' },
    { value: 'gemini-pro', label: 'Gemini Pro (Google)', description: 'Multimodal AI with broad knowledge' },
    { value: 'custom', label: 'Custom Agent', description: 'Custom implementation or API' },
  ];

  const toggleCapability = (capability) => {
    const current = formData.capabilities || [];
    const newCapabilities = current.includes(capability)
      ? current.filter(c => c !== capability)
      : [...current, capability];
    updateField('capabilities', newCapabilities);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                value={formData.name}
                onChange={(e) => updateField('name', e.target.value)}
                label="Agent Name"
                fullWidth
                placeholder="e.g., Content Writer Agent"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                value={formData.description}
                onChange={(e) => updateField('description', e.target.value)}
                label="Description"
                fullWidth
                multiline
                rows={4}
                placeholder="Describe what this agent does and its primary use cases..."
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Agent Type</InputLabel>
                <Select 
                  value={formData.agent_type} 
                  onChange={(e) => updateField('agent_type', e.target.value)} 
                  label="Agent Type"
                >
                  {agentTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Box>
                        <Typography>{type.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {type.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                value={formData.version}
                onChange={(e) => updateField('version', e.target.value)}
                label="Version"
                fullWidth
                placeholder="1.0.0"
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Temperature: {formData.temperature}</Typography>
              <Slider
                value={formData.temperature}
                onChange={(e, value) => updateField('temperature', value)}
                min={0}
                max={2}
                step={0.1}
                marks
                valueLabelDisplay="auto"
              />
              <Typography variant="caption" color="text.secondary">
                Controls randomness: 0 = focused, 2 = creative
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                value={formData.max_tokens}
                onChange={(e) => updateField('max_tokens', e.target.value)}
                label="Max Tokens"
                type="number"
                fullWidth
                helperText="Maximum response length"
                placeholder="2048"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                value={formData.timeout}
                onChange={(e) => updateField('timeout', e.target.value)}
                label="Timeout (seconds)"
                type="number"
                fullWidth
                helperText="Task execution timeout"
                placeholder="30"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select 
                  value={formData.priority} 
                  onChange={(e) => updateField('priority', e.target.value)} 
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={formData.auto_start} 
                    onChange={(e) => updateField('auto_start', e.target.checked)} 
                  />
                }
                label="Auto-start agent after creation"
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Select Agent Capabilities
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Choose the capabilities your agent will have. You can add more later.
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {availableCapabilities.map((capability) => (
                  <Chip
                    key={capability}
                    label={capability.replace('_', ' ')}
                    onClick={() => toggleCapability(capability)}
                    color={formData.capabilities?.includes(capability) ? 'primary' : 'default'}
                    variant={formData.capabilities?.includes(capability) ? 'filled' : 'outlined'}
                    clickable
                  />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                value={formData.memory_limit}
                onChange={(e) => updateField('memory_limit', e.target.value)}
                label="Memory Limit (MB)"
                type="number"
                fullWidth
                helperText="Maximum memory usage"
                placeholder="512"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                value={formData.concurrent_tasks}
                onChange={(e) => updateField('concurrent_tasks', e.target.value)}
                label="Concurrent Tasks"
                type="number"
                fullWidth
                helperText="Number of simultaneous tasks"
                placeholder="1"
              />
            </Grid>
          </Grid>
        );

      case 3:
        console.log('🔍 Review step - formData:', formData);
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Review Agent Configuration
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Basic Information</Typography>
                <Typography><strong>Name:</strong> {formData.name || 'Not set'}</Typography>
                <Typography><strong>Type:</strong> {formData.agent_type || 'Not set'}</Typography>
                <Typography><strong>Version:</strong> {formData.version || 'Not set'}</Typography>
                <Typography><strong>Description:</strong> {formData.description || 'Not set'}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Configuration</Typography>
                <Typography><strong>Temperature:</strong> {formData.temperature}</Typography>
                <Typography><strong>Max Tokens:</strong> {formData.max_tokens || 'Not set'}</Typography>
                <Typography><strong>Timeout:</strong> {formData.timeout ? `${formData.timeout}s` : 'Not set'}</Typography>
                <Typography><strong>Priority:</strong> {formData.priority}</Typography>
                <Typography><strong>Auto-start:</strong> {formData.auto_start ? 'Yes' : 'No'}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Capabilities</Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {(formData.capabilities || []).map((capability) => (
                    <Chip key={capability} label={capability.replace('_', ' ')} size="small" />
                  ))}
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Resources</Typography>
                <Typography><strong>Memory Limit:</strong> {formData.memory_limit ? `${formData.memory_limit} MB` : 'Not set'}</Typography>
                <Typography><strong>Concurrent Tasks:</strong> {formData.concurrent_tasks || 'Not set'}</Typography>
              </Paper>
            </Grid>
          </Grid>
        );

      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/agents')}
          sx={{ mb: 2 }}
        >
          Back to Agents
        </Button>
        <Typography variant="h4" gutterBottom>
          <SmartToyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Create New Agent
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            onClick={handleBack}
            disabled={activeStep === 0}
          >
            Back
          </Button>
          <Box>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                disabled={createMutation.isLoading}
                onClick={onSubmit}
              >
                {createMutation.isLoading ? 'Creating...' : 'Create Agent'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default CreateAgent;