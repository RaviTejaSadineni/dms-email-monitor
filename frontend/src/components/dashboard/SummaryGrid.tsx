import { Box } from '@mui/material';
import type { MetricCard as MetricCardType } from '../../api/dashboard';
import { MetricCard } from '../common/MetricCard';

export function SummaryGrid({ metrics }: { metrics: MetricCardType[] }) {
  return (
    <Box
      sx={{
        display: 'grid',
        gap: 2.5,
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, minmax(0, 1fr))',
          xl: 'repeat(3, minmax(0, 1fr))',
        },
      }}
    >
      {metrics.map((metric) => (
        <Box key={metric.title}>
          <MetricCard title={metric.title} value={metric.value} subtitle={metric.subtitle} />
        </Box>
      ))}
    </Box>
  );
}
