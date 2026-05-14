import { Alert, Box, Stack, Typography } from '@mui/material';
import { DistributionCharts } from '../components/dashboard/DistributionCharts';
import { InsightCards } from '../components/dashboard/InsightCards';
import { PipelineChart } from '../components/dashboard/PipelineChart';
import { SummaryGrid } from '../components/dashboard/SummaryGrid';
import { SectionCard } from '../components/common/SectionCard';
import { useDashboardData } from '../hooks/useDashboardData';

export function DashboardPage() {
  const { summary, insights } = useDashboardData();
  const summaryData = summary.data;
  const insightData = insights.data?.items ?? [];

  if (!summaryData) {
    return <Alert severity="info">Loading dashboard...</Alert>;
  }

  return (
    <Stack spacing={3} id="overview">
      <div>
        <Typography variant="h4">Contract lifecycle command center</Typography>
        <Typography color="text.secondary" mt={1}>
          Stream Gmail Takeout data, classify contract interactions, monitor SLA breach risks, and surface AI-generated delay reasons.
        </Typography>
      </div>
      <SummaryGrid metrics={summaryData.metrics} />
      <Box sx={{ display: 'grid', gap: 2.5, gridTemplateColumns: { xs: '1fr', xl: '2fr 1fr' } }}>
        <Box id="lifecycle">
          <PipelineChart data={summaryData.lifecycle_pipeline} />
        </Box>
        <Box>
          <InsightCards items={insightData} />
        </Box>
      </Box>
      <DistributionCharts
        priorityData={summaryData.priority_distribution}
        categoryData={summaryData.category_distribution}
        emailVolume={summaryData.email_volume}
        stakeholderActivity={summaryData.stakeholder_activity}
      />
      <SectionCard title="Reference lifecycle outcomes">
        <Stack spacing={1.25}>
          <Typography>• 7-stage pipeline: Request → Legal Review → Finance Review → Procurement/Compliance → Redline Negotiation → Leadership Sign-off → Repository & Obligation Tracking.</Typography>
          <Typography>• Negotiation loop and procurement review are highlighted as the slowest stages for legal contract completion.</Typography>
          <Typography>• Attachments are included in AI indexing for clause extraction, risk flagging, and delay-reason detection.</Typography>
        </Stack>
      </SectionCard>
    </Stack>
  );
}
