import { Box, Stack, Typography } from '@mui/material';
import { motion } from 'framer-motion';

const CATEGORY_COLORS: Record<string, string> = {
  'Legal Review': '#42a5f5',
  'Finance Review': '#66bb6a',
  Negotiation: '#ffa726',
  Spam: '#ef5350',
  General: '#9e9e9e',
};

type Props = {
  distribution: Record<string, number>;
};

export function CategoryLanes({ distribution }: Props) {
  const entries = Object.entries(distribution);
  const total = Math.max(entries.reduce((sum, [, count]) => sum + count, 0), 1);

  return (
    <Stack spacing={1.25}>
      {entries.map(([category, count]) => {
        const width = `${Math.max((count / total) * 100, count > 0 ? 8 : 2)}%`;
        const color = CATEGORY_COLORS[category] ?? '#90a4ae';
        return (
          <Box key={category}>
            <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
              <Typography variant="caption" color="grey.300">
                {category}
              </Typography>
              <Typography variant="caption" color="grey.400">
                {count.toLocaleString()}
              </Typography>
            </Stack>
            <Box sx={{ height: 12, borderRadius: 999, bgcolor: 'rgba(255,255,255,0.08)', overflow: 'hidden', position: 'relative' }}>
              <motion.div
                animate={{ width }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                style={{ height: '100%', borderRadius: 999, background: color, boxShadow: `0 0 12px ${color}` }}
              />
            </Box>
          </Box>
        );
      })}
    </Stack>
  );
}
