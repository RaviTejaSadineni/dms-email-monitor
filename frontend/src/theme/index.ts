import { createTheme } from '@mui/material/styles';

export const buildTheme = (mode: 'light' | 'dark') =>
  createTheme({
    palette: {
      mode,
      primary: { main: mode === 'light' ? '#4f46e5' : '#a5b4fc' },
      secondary: { main: '#06b6d4' },
      background: {
        default: mode === 'light' ? '#eef2ff' : '#0f172a',
        paper: mode === 'light' ? '#ffffff' : '#111827',
      },
    },
    shape: { borderRadius: 18 },
    typography: {
      fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      h4: { fontWeight: 700 },
      h5: { fontWeight: 700 },
      h6: { fontWeight: 700 },
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: '0 18px 45px rgba(15, 23, 42, 0.12)',
            backgroundImage: 'none',
          },
        },
      },
    },
  });
