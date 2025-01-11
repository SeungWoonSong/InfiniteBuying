import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Grid,
  Box,
  Chip,
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

interface TradingStatus {
  current_price: number;
  position_count: number;
  average_price: number;
  total_investment: number;
  unrealized_pnl: number;
  current_division: number;
  last_updated: string;
}

export const TradingStatus: React.FC = () => {
  const [status, setStatus] = useState<TradingStatus | null>(null);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/trading/status`);
      setStatus(response.data.status);
    } catch (error) {
      console.error('Failed to fetch trading status:', error);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // 5초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  if (!status) return null;

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
            <Chip
              label={`${status.current_division}회차`}
              color="primary"
              size="small"
            />
          </Box>
        </Grid>
      </Grid>
      <Typography variant="caption" display="block" sx={{ mt: 2, textAlign: 'right' }}>
        Last updated: {new Date(status.last_updated).toLocaleString()}
      </Typography>
    </Paper>
  );
};
