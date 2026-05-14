import { Button, LinearProgress, Stack, TextField, Typography } from '@mui/material';
import { useMemo, useState } from 'react';
import { SectionCard } from '../components/common/SectionCard';

export function ImportsPage() {
  const [path, setPath] = useState('/data/takeout/legal-advisor.mbox');
  const [batchSize, setBatchSize] = useState(500);
  const progress = useMemo(() => Math.min(100, Math.round((20868 / 20868) * 100)), []);

  return (
    <SectionCard title="High-volume Gmail Takeout import" action={<Button variant="contained">Queue import</Button>}>
      <Typography color="text.secondary" id="imports">
        Streaming mbox parser, deduplication by message-id, attachment extraction, and AI-ready batch processing tuned for large 23GB imports.
      </Typography>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        <TextField fullWidth label="mbox path" value={path} onChange={(event) => setPath(event.target.value)} />
        <TextField type="number" label="Batch size" value={batchSize} onChange={(event) => setBatchSize(Number(event.target.value))} />
      </Stack>
      <Stack spacing={1.5}>
        <Stack direction="row" justifyContent="space-between">
          <Typography variant="subtitle2">Import progress</Typography>
          <Typography color="text.secondary" variant="body2">20,868 / 20,868 emails</Typography>
        </Stack>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 10, borderRadius: 999 }} />
        <Typography color="text.secondary" variant="body2">Default batch size 500-1000, async processing with Redis-backed progress caching.</Typography>
      </Stack>
    </SectionCard>
  );
}
