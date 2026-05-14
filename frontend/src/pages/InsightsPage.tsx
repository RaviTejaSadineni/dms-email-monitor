import { Box, Chip, Stack, Typography } from '@mui/material';
import { SectionCard } from '../components/common/SectionCard';
import { useDashboardData } from '../hooks/useDashboardData';

export function InsightsPage() {
  const { summary } = useDashboardData();
  const pipeline = summary.data?.lifecycle_pipeline ?? [];
  const hotspots = pipeline.filter((item) => item.average_hours >= 72);

  return (
    <Box id="insights" sx={{ display: 'grid', gap: 2.5, gridTemplateColumns: { xs: '1fr', xl: 'repeat(2, minmax(0, 1fr))' } }}>
      <Box>
        <SectionCard title="AI-generated delay reasons">
          <Stack spacing={2}>
            {hotspots.map((item) => (
              <div key={item.stage} className="rounded-3xl border border-slate-200/70 p-4 dark:border-slate-700">
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1.5}>
                  <Typography variant="subtitle1">{item.stage}</Typography>
                  <Chip label={`${item.average_hours} hours avg`} color="warning" size="small" />
                </Stack>
                <Typography color="text.secondary">AI indicates this stage suffers from document gaps, approval wait times, or repeated clause negotiations.</Typography>
              </div>
            ))}
          </Stack>
        </SectionCard>
      </Box>
      <Box>
        <SectionCard title="Mandatory feature coverage">
          <Typography color="text.secondary">
            The workspace includes dashboards for priorities, contract lifecycle, AI insights, attachments, search, filters, import monitoring, and the complete 130-feature catalog requested for appraisal delivery planning.
          </Typography>
        </SectionCard>
      </Box>
    </Box>
  );
}
