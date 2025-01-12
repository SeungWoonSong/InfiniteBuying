import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Grid,
  Box,
  Chip,
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface TradingStatus {
  current_price: number;
  position_count: number;
  average_price: number;
  total_investment: number;
  unrealized_pnl: number;
  current_division: number;
  last_updated: string;
}

interface TradingStatusResponse {
  status: TradingStatus;
  recent_trades: any[];  // TODO: Add proper type
}

export const TradingStatus: React.FC = () => {
  const [status, setStatus] = useState<TradingStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const response = await axios.get<TradingStatusResponse>(`${API_BASE_URL}/trading/status`);
      if (response.data && response.data.status) {
        setStatus(response.data.status);
        setError(null);
      } else {
        setStatus(null);
        setError('Invalid response format');
      }
    } catch (error) {
      console.error('Failed to fetch trading status:', error);
      setStatus(null);
      setError(error instanceof Error ? error.message : 'Failed to fetch status');
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // 5초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography color="error">Error: {error}</Typography>
      </Paper>
    );
  }

  if (!status) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography>Loading trading status...</Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Trading Status
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={6} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Current Price
            </Typography>
            <Typography variant="h6">
              ${status.current_price.toFixed(2)}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Position Count
            </Typography>
            <Typography variant="h6">
              {status.position_count}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Average Price
            </Typography>
            <Typography variant="h6">
              ${status.average_price.toFixed(2)}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Total Investment
            </Typography>
            <Typography variant="h6">
              ${status.total_investment.toFixed(2)}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Unrealized P&L
            </Typography>
            <Typography
              variant="h6"
              color={status.unrealized_pnl >= 0 ? 'success.main' : 'error.main'}
            >
              ${status.unrealized_pnl.toFixed(2)}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Current Division
            </Typography>
            <Typography variant="h6">
              {status.current_division}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Last Updated
            </Typography>
            <Typography variant="h6">
              {status.last_updated}
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};
