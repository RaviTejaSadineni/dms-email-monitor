import { Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useMemo, useState } from 'react';
import { SectionCard } from '../components/common/SectionCard';
import { useDashboardData } from '../hooks/useDashboardData';

export function EmailsPage() {
  const { emails } = useDashboardData();
  const [query, setQuery] = useState('');
  const rows = emails.data?.items ?? [];
  const filtered = useMemo(
    () => rows.filter((item) => `${item.subject} ${item.sender} ${item.category}`.toLowerCase().includes(query.toLowerCase())),
    [rows, query],
  );

  return (
    <SectionCard
      title="Email intelligence"
      action={<TextField size="small" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by sender, subject, or category" />}
    >
      <Typography color="text.secondary">
        Search, filter, and review high-priority contract emails with AI classification, sentiment, and attachment context.
      </Typography>
      <Table size="small" id="emails">
        <TableHead>
          <TableRow>
            <TableCell>Subject</TableCell>
            <TableCell>Sender</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Priority</TableCell>
            <TableCell>Sentiment</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filtered.map((row) => (
            <TableRow key={row.id} hover>
              <TableCell>
                <Stack spacing={0.5}>
                  <Typography variant="subtitle2">{row.subject}</Typography>
                  <Typography color="text.secondary" variant="body2">{row.ai_summary}</Typography>
                </Stack>
              </TableCell>
              <TableCell>{row.sender}</TableCell>
              <TableCell>{row.category}</TableCell>
              <TableCell><Chip size="small" label={row.priority} color={row.priority === 'P1' ? 'error' : 'primary'} /></TableCell>
              <TableCell>{row.sentiment}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </SectionCard>
  );
}
