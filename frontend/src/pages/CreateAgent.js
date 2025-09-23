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
import { useForm, Controller } from 'react-hook-form';
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
  const { control, handleSubmit, watch, setValue, getValues, formState: { errors } } = useForm({
    defaultValues: {
      name: '',
      description: '',
      agent_type: 'gpt-4',
      version: '1.0.0',
      capabilities: [],
      temperature: 0.7,
      max_tokens: 2048,
      timeout: 30,
      auto_start: false,
      priority: 'normal',
      memory_limit: 512,
      concurrent_tasks: 1,
    }
  });

  const createMutation = useMutation(agentAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('agents');
      navigate('/agents');
    },
    onError: (error) => {
      setError(error.response?.data?.detail || 'Failed to create agent');
    },
  });

  const watchedValues = watch();

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const onSubmit = (data) => {
    const agentData = {
      ...data,
      configuration: {
        temperature: data.temperature,
        max_tokens: data.max_tokens,
        timeout: data.timeout,
        auto_start: data.auto_start,
        priority: data.priority,
      },
      resources: {
        memory_limit: data.memory_limit,
        concurrent_tasks: data.concurrent_tasks,
      },
    };
    
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
    const current = watchedValues.capabilities || [];
    const newCapabilities = current.includes(capability)
      ? current.filter(c => c !== capability)
      : [...current, capability];
    setValue('capabilities', newCapabilities);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Controller
                name="name"
                control={control}
                rules={{ required: 'Agent name is required' }}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    label="Agent Name"
                    fullWidth
                    error={!!fieldState.error}
                    helperText={fieldState.error?.message}
                    placeholder="e.g., Content Writer Agent"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="description"
                control={control}
                rules={{ required: 'Description is required' }}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    label="Description"
                    fullWidth
                    multiline
                    rows={4}
                    error={!!fieldState.error}
                    helperText={fieldState.error?.message}
                    placeholder="Describe what this agent does and its primary use cases..."
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="agent_type"
                control={control}
                rules={{ required: 'Agent type is required' }}
                render={({ field, fieldState }) => (
                  <FormControl fullWidth error={!!fieldState.error}>
                    <InputLabel>Agent Type</InputLabel>
                    <Select {...field} label="Agent Type">
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
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="version"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Version"
                    fullWidth
                    placeholder="1.0.0"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Temperature: {watchedValues.temperature}</Typography>
              <Controller
                name="temperature"
                control={control}
                render={({ field }) => (
                  <Slider
                    {...field}
                    min={0}
                    max={2}
                    step={0.1}
                    marks
                    valueLabelDisplay="auto"
                  />
                )}
              />
              <Typography variant="caption" color="text.secondary">
                Controls randomness: 0 = focused, 2 = creative
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="max_tokens"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Max Tokens"
                    type="number"
                    fullWidth
                    helperText="Maximum response length"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="timeout"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Timeout (seconds)"
                    type="number"
                    fullWidth
                    helperText="Task execution timeout"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="priority"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Priority</InputLabel>
                    <Select {...field} label="Priority">
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="normal">Normal</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="urgent">Urgent</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="auto_start"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={<Switch {...field} checked={field.value} />}
                    label="Auto-start agent after creation"
                  />
                )}
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
                    color={watchedValues.capabilities?.includes(capability) ? 'primary' : 'default'}
                    variant={watchedValues.capabilities?.includes(capability) ? 'filled' : 'outlined'}
                    clickable
                  />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="memory_limit"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Memory Limit (MB)"
                    type="number"
                    fullWidth
                    helperText="Maximum memory usage"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="concurrent_tasks"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Concurrent Tasks"
                    type="number"
                    fullWidth
                    helperText="Number of simultaneous tasks"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      case 3:
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
                <Typography><strong>Name:</strong> {watchedValues.name}</Typography>
                <Typography><strong>Type:</strong> {watchedValues.agent_type}</Typography>
                <Typography><strong>Version:</strong> {watchedValues.version}</Typography>
                <Typography><strong>Description:</strong> {watchedValues.description}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Configuration</Typography>
                <Typography><strong>Temperature:</strong> {watchedValues.temperature}</Typography>
                <Typography><strong>Max Tokens:</strong> {watchedValues.max_tokens}</Typography>
                <Typography><strong>Timeout:</strong> {watchedValues.timeout}s</Typography>
                <Typography><strong>Priority:</strong> {watchedValues.priority}</Typography>
                <Typography><strong>Auto-start:</strong> {watchedValues.auto_start ? 'Yes' : 'No'}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Capabilities</Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {(watchedValues.capabilities || []).map((capability) => (
                    <Chip key={capability} label={capability.replace('_', ' ')} size="small" />
                  ))}
                </Box>
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

        <form onSubmit={handleSubmit(onSubmit)}>
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
                  type="submit"
                  variant="contained"
                  startIcon={<SaveIcon />}
                  disabled={createMutation.isLoading}
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
        </form>
      </Paper>
    </Container>
  );
};

export default CreateAgent;