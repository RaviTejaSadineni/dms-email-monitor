import { Box, Button, Paper, Stack, Typography } from '@mui/material';
import type { PropsWithChildren } from 'react';

const items = [
  { label: 'Overview', href: '#overview' },
  { label: 'Lifecycle', href: '#lifecycle' },
  { label: 'Emails', href: '#emails' },
  { label: 'Contracts', href: '#contracts' },
  { label: 'Imports', href: '#imports' },
  { label: 'Insights', href: '#insights' },
  { label: 'Theme', href: '#overview' },
];

export function AppShell({ children, mode, onToggleMode }: PropsWithChildren<{ mode: 'light' | 'dark'; onToggleMode: () => void }>) {
  return (
    <Box sx={{ minHeight: '100vh', background: (theme) => theme.palette.background.default }}>
      <Box sx={{ px: { xs: 2, md: 4 }, py: 3 }}>
        <Paper sx={{ p: 3, borderRadius: 5 }}>
          <Stack spacing={2.5}>
            <Stack direction={{ xs: 'column', lg: 'row' }} justifyContent="space-between" spacing={2}>
              <div>
                <Typography variant="h4">Legal Contract Intelligence Platform</Typography>
                <Typography color="text.secondary" mt={1}>
                  End-to-end contract lifecycle analytics for Gmail Takeout emails and attachments.
                </Typography>
              </div>
              <Button color="primary" variant="contained" onClick={onToggleMode} sx={{ alignSelf: { xs: 'flex-start', lg: 'center' } }}>
                Switch to {mode === 'light' ? 'dark' : 'light'} mode
              </Button>
            </Stack>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.25} flexWrap="wrap">
              {items.map((item) => (
                <Button key={item.label} component="a" href={item.href} variant="outlined" sx={{ borderRadius: 999 }}>
                  {item.label}
                </Button>
              ))}
            </Stack>
          </Stack>
        </Paper>
      </Box>
      <Box component="main" sx={{ px: { xs: 2, md: 4 }, pb: 4 }}>
        {children}
      </Box>
    </Box>
  );
}
