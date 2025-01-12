import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Grid,
  Switch,
  FormControlLabel,
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface BotConfig {
  is_running: boolean;
  log_dir?: string;
  app_key?: string;
  app_secret?: string;
  account_number?: string;
  account_code?: string;
}

interface TradingConfig {
  symbol: string;
  total_divisions: number;
  first_buy_amount: number;
  pre_turn_threshold: number;
  quarter_loss_start: number;
}

interface Config {
  bot_config: BotConfig;
  trading_config: TradingConfig;
}

export const ConfigForm: React.FC = () => {
  const [config, setConfig] = useState<Config | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/config`);
      if (response.data) {
        setConfig(response.data);
        setError(null);
      } else {
        setConfig(null);
        setError('Invalid response format');
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
      setConfig(null);
      setError(error instanceof Error ? error.message : 'Failed to fetch config');
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!config) return;

    try {
      await axios.post(`${API_BASE_URL}/config`, config);
      alert('Configuration updated successfully!');
    } catch (error) {
      console.error('Failed to update config:', error);
      alert('Failed to update configuration. Please try again.');
    }
  };

  const handleStartBot = async () => {
    try {
      await axios.post(`${API_BASE_URL}/config/start`);
      await fetchConfig();
      alert('Bot started successfully!');
    } catch (error) {
      console.error('Failed to start bot:', error);
      alert('Failed to start bot. Please try again.');
    }
  };

  const handleStopBot = async () => {
    try {
      await axios.post(`${API_BASE_URL}/config/stop`);
      await fetchConfig();
      alert('Bot stopped successfully!');
    } catch (error) {
      console.error('Failed to stop bot:', error);
      alert('Failed to stop bot. Please try again.');
    }
  };

  const handleResetBot = async () => {
    if (window.confirm('Are you sure you want to reset the bot? This will clear all trading history.')) {
      try {
        await axios.post(`${API_BASE_URL}/config/reset`);
        await fetchConfig();
        alert('Bot reset successfully!');
      } catch (error) {
        console.error('Failed to reset bot:', error);
        alert('Failed to reset bot. Please try again.');
      }
    }
  };

  if (error) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography color="error">Error: {error}</Typography>
      </Paper>
    );
  }

  if (!config) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography>Loading configuration...</Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Bot Configuration
      </Typography>
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.bot_config.is_running}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      bot_config: {
                        ...config.bot_config,
                        is_running: e.target.checked,
                      },
                    })
                  }
                />
              }
              label="Bot Running"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Symbol"
              value={config.trading_config.symbol}
              onChange={(e) =>
                setConfig({
                  ...config,
                  trading_config: {
                    ...config.trading_config,
                    symbol: e.target.value,
                  },
                })
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Total Divisions"
              value={config.trading_config.total_divisions}
              onChange={(e) =>
                setConfig({
                  ...config,
                  trading_config: {
                    ...config.trading_config,
                    total_divisions: Number(e.target.value),
                  },
                })
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="First Buy Amount"
              value={config.trading_config.first_buy_amount}
              onChange={(e) =>
                setConfig({
                  ...config,
                  trading_config: {
                    ...config.trading_config,
                    first_buy_amount: Number(e.target.value),
                  },
                })
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Pre-turn Threshold"
              value={config.trading_config.pre_turn_threshold}
              onChange={(e) =>
                setConfig({
                  ...config,
                  trading_config: {
                    ...config.trading_config,
                    pre_turn_threshold: Number(e.target.value),
                  },
                })
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Quarter Loss Start"
              value={config.trading_config.quarter_loss_start}
              onChange={(e) =>
                setConfig({
                  ...config,
                  trading_config: {
                    ...config.trading_config,
                    quarter_loss_start: Number(e.target.value),
                  },
                })
              }
            />
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="error"
                onClick={handleResetBot}
              >
                Reset Bot
              </Button>
              <Button
                variant="contained"
                color={config.bot_config.is_running ? "error" : "success"}
                onClick={config.bot_config.is_running ? handleStopBot : handleStartBot}
              >
                {config.bot_config.is_running ? "Stop Bot" : "Start Bot"}
              </Button>
              <Button
                type="submit"
                variant="contained"
                color="primary"
              >
                Save Configuration
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};
