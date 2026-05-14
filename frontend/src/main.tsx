import { CssBaseline, ThemeProvider } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';
import { AppShell } from './components/layout/AppShell';
import { buildTheme } from './theme';

const queryClient = new QueryClient();

function Root() {
  const [mode, setMode] = useState<'light' | 'dark'>('light');
  const theme = useMemo(() => buildTheme(mode), [mode]);

  return (
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <AppShell mode={mode} onToggleMode={() => setMode((current) => (current === 'light' ? 'dark' : 'light'))}>
            <App />
          </AppShell>
        </ThemeProvider>
      </QueryClientProvider>
    </StrictMode>
  );
}

createRoot(document.getElementById('root')!).render(<Root />);
