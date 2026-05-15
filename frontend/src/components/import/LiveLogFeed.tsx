import { Box, Stack, Typography } from '@mui/material';
import { useEffect, useRef } from 'react';

import type { ImportJobLiveEvent } from '../../api/imports';

const EVENT_COLORS: Record<string, string> = {
  info: '#64b5f6',
  success: '#81c784',
  warning: '#ffb74d',
  error: '#e57373',
};

type Props = {
  events: ImportJobLiveEvent[];
};

export function LiveLogFeed({ events }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.scrollTop = containerRef.current.scrollHeight;
  }, [events]);

  return (
    <Box
      ref={containerRef}
      sx={{
        maxHeight: 170,
        overflowY: 'auto',
        borderRadius: 2,
        p: 1.25,
        bgcolor: 'rgba(0,0,0,0.35)',
        border: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <Stack spacing={0.8}>
        {events.length === 0 && (
          <Typography variant="caption" color="grey.500">
            Waiting for live import events…
          </Typography>
        )}
        {events.map((event, index) => (
          <Typography key={`${event.timestamp}-${index}`} variant="caption" sx={{ color: EVENT_COLORS[event.type] ?? 'grey.300' }}>
            [{new Date(event.timestamp).toLocaleTimeString()}] {event.message}
          </Typography>
        ))}
      </Stack>
    </Box>
  );
}
