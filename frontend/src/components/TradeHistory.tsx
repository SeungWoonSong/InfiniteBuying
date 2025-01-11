import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

interface Trade {
  timestamp: string;
  symbol: string;
  action: string;
  price: number;
  quantity: number;
  division: number;
  total_amount: number;
}

export const TradeHistory: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/trading/history`, {
        params: {
          limit: rowsPerPage,
          offset: page * rowsPerPage,
        },
      });
      setTrades(response.data);
    } catch (error) {
      console.error('Failed to fetch trade history:', error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, rowsPerPage]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Trade History
      </Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Action</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell align="center">Division</TableCell>
              <TableCell align="right">Total</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade, index) => (
              <TableRow key={index}>
                <TableCell>
                  {new Date(trade.timestamp).toLocaleString()}
                </TableCell>
                <TableCell>{trade.symbol}</TableCell>
                <TableCell>
                  <Chip
                    label={trade.action}
                    color={trade.action === 'BUY' ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  ${trade.price.toFixed(2)}
                </TableCell>
                <TableCell align="right">
                  {trade.quantity}
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={`${trade.division}회차`}
                    color="primary"
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  ${trade.total_amount.toFixed(2)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        component="div"
        count={-1}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[5, 10, 25, 50]}
      />
    </Paper>
  );
};
