import { Box, Chip, Stack, Typography } from '@mui/material';
import type { ChartPoint } from '../../api/dashboard';
import { SectionCard } from '../common/SectionCard';

function MetricList({ title, items }: { title: string; items: ChartPoint[] }) {
  return (
    <SectionCard title={title}>
      <Stack spacing={1.5}>
        {items.map((item) => (
          <Stack key={item.label} direction="row" justifyContent="space-between" alignItems="center">
            <Typography>{item.label}</Typography>
            <Chip size="small" color="primary" label={item.value} />
          </Stack>
        ))}
      </Stack>
    </SectionCard>
  );
}

export function DistributionCharts({
  priorityData,
  categoryData,
  emailVolume,
  stakeholderActivity,
}: {
  priorityData: ChartPoint[];
  categoryData: ChartPoint[];
  emailVolume: ChartPoint[];
  stakeholderActivity: ChartPoint[];
}) {
  return (
    <Box sx={{ display: 'grid', gap: 2.5, gridTemplateColumns: { xs: '1fr', xl: 'repeat(3, minmax(0, 1fr))' } }}>
      <MetricList title="Priority distribution" items={priorityData} />
      <MetricList title="Category distribution" items={categoryData} />
      <MetricList title="Stakeholder intensity" items={stakeholderActivity} />
      <Box sx={{ gridColumn: { xl: '1 / -1' } }}>
        <MetricList title="Email volume timeline" items={emailVolume} />
      </Box>
    </Box>
  );
}
