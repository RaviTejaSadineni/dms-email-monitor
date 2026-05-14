import { Box, Chip, LinearProgress, Stack, Typography } from '@mui/material';
import type { StageMetric } from '../../api/dashboard';
import { SectionCard } from '../common/SectionCard';

export function PipelineChart({ data }: { data: StageMetric[] }) {
  const maxHours = Math.max(...data.map((stage) => stage.average_hours), 1);

  return (
    <SectionCard title="Contract review lifecycle">
      <Stack spacing={2}>
        {data.map((stage) => (
          <Box key={stage.stage} className="rounded-3xl border border-slate-200/70 p-4 dark:border-slate-700">
            <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2} mb={1.5}>
              <div>
                <Typography variant="subtitle1">{stage.stage}</Typography>
                <Typography color="text.secondary" variant="body2">
                  {stage.count} contracts • Avg duration {stage.average_hours} hours
                </Typography>
              </div>
              <Chip
                size="small"
                label={`${stage.breach_rate}% breach risk`}
                color={stage.average_hours > 72 ? 'warning' : 'primary'}
              />
            </Stack>
            <LinearProgress
              variant="determinate"
              value={Math.min(100, (stage.average_hours / maxHours) * 100)}
              sx={{ height: 10, borderRadius: 999 }}
            />
          </Box>
        ))}
      </Stack>
    </SectionCard>
  );
}
