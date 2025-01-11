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

  const handleBotControl = async () => {
    try {
      await axios.post(`${API_BASE_URL}/${config.is_running ? 'stop' : 'start'}`);
      setConfig(prev => ({ ...prev, is_running: !prev.is_running }));
    } catch (error) {
      console.error('Failed to control bot:', error);
      alert('Failed to control bot');
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Trading Bot Configuration
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Symbol"
              value={config.symbol}
              onChange={(e) => setConfig({ ...config, symbol: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              type="number"
              label="Total Divisions"
              value={config.total_divisions}
              onChange={(e) => setConfig({ ...config, total_divisions: Number(e.target.value) })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              type="number"
              label="First Buy Amount"
              value={config.first_buy_amount}
              onChange={(e) => setConfig({ ...config, first_buy_amount: Number(e.target.value) })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              type="number"
              label="Pre Turn Threshold"
              value={config.pre_turn_threshold}
              onChange={(e) => setConfig({ ...config, pre_turn_threshold: Number(e.target.value) })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              type="number"
              label="Quarter Loss Start"
              value={config.quarter_loss_start}
              onChange={(e) => setConfig({ ...config, quarter_loss_start: Number(e.target.value) })}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.is_running}
                  onChange={handleBotControl}
                  color="primary"
                />
              }
              label={config.is_running ? "Bot Running" : "Bot Stopped"}
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
            >
              Save Configuration
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};
