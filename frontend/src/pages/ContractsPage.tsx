import { Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { SectionCard } from '../components/common/SectionCard';
import { useDashboardData } from '../hooks/useDashboardData';

export function ContractsPage() {
  const { contracts, attachments } = useDashboardData();
  const contractRows = contracts.data?.items ?? [];
  const attachmentRows = attachments.data?.items ?? [];

  return (
    <Stack spacing={2.5} id="contracts">
      <SectionCard title="Contract portfolio">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Contract</TableCell>
              <TableCell>Stage</TableCell>
              <TableCell>Value</TableCell>
              <TableCell>Risk</TableCell>
              <TableCell>SLA</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {contractRows.map((row) => (
              <TableRow key={row.id} hover>
                <TableCell>
                  <Typography variant="subtitle2">{row.contract_number}</Typography>
                  <Typography color="text.secondary" variant="body2">{row.ai_summary}</Typography>
                </TableCell>
                <TableCell>{row.current_stage}</TableCell>
                <TableCell>{row.value_currency} {row.value_amount?.toLocaleString?.() ?? row.value_amount}</TableCell>
                <TableCell>{row.risk_score}</TableCell>
                <TableCell>
                  <Chip label={row.sla_breached ? 'Breached' : 'On track'} color={row.sla_breached ? 'warning' : 'success'} size="small" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </SectionCard>
      <SectionCard title="Attachment intelligence">
        <Stack spacing={2}>
          {attachmentRows.map((attachment) => (
            <div key={attachment.id} className="rounded-3xl border border-slate-200/70 p-4 dark:border-slate-700">
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
                <div>
                  <Typography variant="subtitle1">{attachment.filename}</Typography>
                  <Typography color="text.secondary" variant="body2">{attachment.ai_extracted_text}</Typography>
                </div>
                <Chip label={attachment.content_type ?? 'Unknown'} size="small" />
              </Stack>
              <Typography mt={2}>{attachment.ai_analysis}</Typography>
            </div>
          ))}
        </Stack>
      </SectionCard>
    </Stack>
  );
}
