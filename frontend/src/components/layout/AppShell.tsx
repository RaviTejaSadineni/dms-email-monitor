import { AppBar, Box, Button, Divider, Drawer, List, ListItemButton, ListItemText, Stack, Toolbar, Typography } from '@mui/material';
import type { PropsWithChildren } from 'react';

const drawerWidth = 260;

const items = [
  { label: 'Dashboard', path: '/' },
  { label: 'Emails', path: '/emails' },
  { label: 'Contracts', path: '/contracts' },
  { label: 'Import', path: '/imports' },
  { label: 'AI Insights', path: '/insights' },
  { label: 'Features', path: '/features' },
];

type AppShellProps = PropsWithChildren<{
  currentPath: string;
  mode: 'light' | 'dark';
  onLogout: () => void;
  onNavigate: (path: string) => void;
  onToggleMode: () => void;
  userEmail?: string;
  userName?: string;
}>;

export function AppShell({ children, currentPath, mode, onLogout, onNavigate, onToggleMode, userEmail, userName }: AppShellProps) {
  return (
    <Box sx={{ minHeight: '100vh', background: (theme) => theme.palette.background.default, display: 'flex' }}>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            borderRight: '1px solid',
            borderColor: 'divider',
          },
        }}
      >
        <Toolbar>
          <Stack spacing={0.5}>
            <Typography variant="h6">Legal Contract Intelligence Platform</Typography>
            <Typography variant="body2" color="text.secondary">
              Contract lifecycle analytics
            </Typography>
          </Stack>
        </Toolbar>
        <Divider />
        <List sx={{ px: 1.5, py: 2 }}>
          {items.map((item) => (
            <ListItemButton
              key={item.path}
              selected={currentPath === item.path}
              onClick={() => onNavigate(item.path)}
              sx={{ borderRadius: 3, mb: 0.5 }}
            >
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="sticky" color="inherit" elevation={0} sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          <Toolbar sx={{ justifyContent: 'space-between', gap: 2 }}>
            <div>
              <Typography variant="h6">End-to-end contract monitoring</Typography>
              <Typography color="text.secondary" variant="body2">
                Signed in as {userName || 'User'}{userEmail ? ` • ${userEmail}` : ''}
              </Typography>
            </div>
            <Stack direction="row" spacing={1.5}>
              <Button color="primary" variant="outlined" onClick={onToggleMode}>
                {mode === 'light' ? 'Dark mode' : 'Light mode'}
              </Button>
              <Button color="primary" variant="contained" onClick={onLogout}>
                Logout
              </Button>
            </Stack>
          </Toolbar>
        </AppBar>
        <Box component="main" sx={{ p: { xs: 2, md: 4 } }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
