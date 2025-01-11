import { ConfigForm } from './components/ConfigForm';
import { TradingStatus } from './components/TradingStatus';
import { TradeHistory } from './components/TradeHistory';
import { Container, CssBaseline, ThemeProvider, createTheme, Box } from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container>
        <Box sx={{ py: 4 }}>
          <TradingStatus />
          <ConfigForm />
          <Box sx={{ mt: 3 }}>
            <TradeHistory />
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
