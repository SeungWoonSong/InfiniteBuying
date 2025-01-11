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

const API_BASE_URL = 'http://localhost:8000/api';

interface TradingConfig {
  symbol: string;
  total_divisions: number;
  first_buy_amount: number;
  pre_turn_threshold: number;
  quarter_loss_start: number;
  is_running: boolean;
}

export const ConfigForm: React.FC = () => {
  const [config, setConfig] = useState<TradingConfig>({
    symbol: '',
    total_divisions: 40,
    first_buy_amount: 1,
    pre_turn_threshold: 20,
    quarter_loss_start: 39,
    is_running: false,
  });

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/config`);
      setConfig(response.data);
    } catch (error) {
      console.error('Failed to fetch config:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { is_running, ...configUpdate } = config;
      await axios.post(`${API_BASE_URL}/config`, configUpdate);
      alert('Configuration updated successfully!');
    } catch (error) {
      console.error('Failed to update config:', error);
      alert('Failed to update configuration');
    }
  };

  const handleStartBot = async () => {
    try {
      await axios.post(`${API_BASE_URL}/config/start`);
      await fetchConfig();
    } catch (error) {
      console.error('Failed to start bot:', error);
    }
  };

  const handleStopBot = async () => {
    try {
      await axios.post(`${API_BASE_URL}/config/stop`);
      await fetchConfig();
    } catch (error) {
      console.error('Failed to stop bot:', error);
    }
  };

  const handleResetBot = async () => {
    try {
      await axios.post(`${API_BASE_URL}/config/reset`);
      await fetchConfig();
    } catch (error) {
      console.error('Failed to reset bot:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfig({ ...config, [e.target.name]: e.target.type === 'number' ? Number(e.target.value) : e.target.value });
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Trading Bot Configuration
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Symbol"
              name="symbol"
              value={config.symbol}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Total Divisions"
              name="total_divisions"
              value={config.total_divisions}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="First Buy Amount"
              name="first_buy_amount"
              value={config.first_buy_amount}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Pre-turn Threshold"
              name="pre_turn_threshold"
              value={config.pre_turn_threshold}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Quarter Loss Start"
              name="quarter_loss_start"
              value={config.quarter_loss_start}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="contained"
                color="primary"
                type="submit"
                disabled={config.is_running}
              >
                Save Configuration
              </Button>
              {config.is_running ? (
                <Button
                  variant="contained"
                  color="error"
                  onClick={handleStopBot}
                >
                  Stop Bot
                </Button>
              ) : (
                <>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handleStartBot}
                  >
                    Start Bot
                  </Button>
                  <Button
                    variant="outlined"
                    color="warning"
                    onClick={handleResetBot}
                  >
                    Reset Bot
                  </Button>
                </>
              )}
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};
