import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  LinearProgress,
  Snackbar,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useRef, useState } from 'react';
import { importsApi, type ImportJob } from '../api/imports';
import { SectionCard } from '../components/common/SectionCard';

const POLL_INTERVAL_MS = 2000;

const STATUS_COLORS: Record<ImportJob['status'], 'default' | 'info' | 'warning' | 'success' | 'error'> = {
  queued: 'info',
  running: 'warning',
  completed: 'success',
  completed_with_errors: 'error',
  failed: 'error',
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

function formatDateTime(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString();
}

export function ImportsPage() {
  const [path, setPath] = useState('/data/takeout/legal-advisor.mbox');
  const [batchSize, setBatchSize] = useState(500);

  const [activeJob, setActiveJob] = useState<ImportJob | null>(null);
  const [jobHistory, setJobHistory] = useState<ImportJob[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current !== null) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const refreshHistory = useCallback(async () => {
    try {
      const jobs = await importsApi.listJobs();
      setJobHistory(jobs);
    } catch (err) {
      console.error('Failed to fetch job history:', err);
    }
  }, []);

  const startPolling = useCallback(
    (jobId: number) => {
      stopPolling();
      pollRef.current = setInterval(async () => {
        try {
          const job = await importsApi.getJobProgress(jobId);
          setActiveJob(job);
          if (job.status === 'completed' || job.status === 'completed_with_errors' || job.status === 'failed') {
            stopPolling();
            setSnackbar({
              open: true,
              message:
                job.status === 'completed'
                  ? `Import completed: ${job.processed_count.toLocaleString()} emails processed.`
                  : `Import finished with ${job.error_count} error(s).`,
              severity: job.status === 'completed' ? 'success' : 'error',
            });
            void refreshHistory();
          }
        } catch (err) {
          console.error('Failed to fetch job progress:', err);
          stopPolling();
        }
      }, POLL_INTERVAL_MS);
    },
    [stopPolling, refreshHistory],
  );

  useEffect(() => {
    void refreshHistory().finally(() => setHistoryLoading(false));
    return () => stopPolling();
  }, [refreshHistory, stopPolling]);

  const isRunning = activeJob !== null && (activeJob.status === 'queued' || activeJob.status === 'running');

  const handleQueueImport = async () => {
    setSubmitting(true);
    try {
      const job = await importsApi.createJob(path, batchSize);
      setActiveJob(job);
      startPolling(job.id);
    } catch (err) {
      setSnackbar({ open: true, message: err instanceof Error ? err.message : 'Failed to create import job', severity: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  const progress =
    activeJob && activeJob.total_emails > 0
      ? Math.min(100, Math.round((activeJob.processed_count / activeJob.total_emails) * 100))
      : 0;

  return (
    <Stack spacing={3} id="imports">
      <SectionCard
        title="High-volume Gmail Takeout import"
        action={
          <Button variant="contained" onClick={() => void handleQueueImport()} disabled={submitting || isRunning} startIcon={submitting ? <CircularProgress size={16} color="inherit" /> : undefined}>
            {submitting ? 'Queuing…' : isRunning ? 'Running…' : 'Queue import'}
          </Button>
        }
      >
        <Typography color="text.secondary">
          Streaming mbox parser, deduplication by message-id, attachment extraction, and AI-ready batch processing tuned for large 23GB imports.
        </Typography>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <TextField
            fullWidth
            label="mbox path"
            value={path}
            onChange={(event) => setPath(event.target.value)}
            disabled={isRunning}
          />
          <TextField
            type="number"
            label="Batch size"
            value={batchSize}
            onChange={(event) => setBatchSize(Number(event.target.value))}
            disabled={isRunning}
          />
        </Stack>

        {activeJob && (
          <Stack spacing={1.5}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="subtitle2">Import progress</Typography>
                <Chip label={activeJob.status.replace('_', ' ')} color={STATUS_COLORS[activeJob.status]} size="small" />
              </Stack>
              <Typography color="text.secondary" variant="body2">
                {activeJob.processed_count.toLocaleString()} / {activeJob.total_emails.toLocaleString()} emails
                {activeJob.file_size_bytes > 0 && ` · ${formatBytes(activeJob.file_size_bytes)}`}
              </Typography>
            </Stack>
            <LinearProgress
              variant={activeJob.status === 'queued' ? 'indeterminate' : 'determinate'}
              value={progress}
              sx={{ height: 10, borderRadius: 999 }}
            />
            {activeJob.error_count > 0 && (
              <Alert severity="warning">
                {activeJob.error_count} error(s) encountered.
                {activeJob.errors.length > 0 && (
                  <Box component="ul" sx={{ m: 0, pl: 2 }}>
                    {activeJob.errors.slice(0, 5).map((e, i) => (
                      <li key={`${e.batch_start}-${i}`}>Batch {e.batch_start}: {e.error}</li>
                    ))}
                  </Box>
                )}
              </Alert>
            )}
            <Typography color="text.secondary" variant="body2">
              Default batch size 500-1000, async processing with Redis-backed progress caching.
            </Typography>
          </Stack>
        )}
      </SectionCard>

      <SectionCard title="Import history">
        {historyLoading ? (
          <CircularProgress size={24} />
        ) : jobHistory.length === 0 ? (
          <Typography color="text.secondary">No import jobs yet.</Typography>
        ) : (
          <Box sx={{ overflowX: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Filename</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Processed</TableCell>
                  <TableCell align="right">Errors</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell>Completed</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {jobHistory.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell>{job.filename}</TableCell>
                    <TableCell>
                      <Chip label={job.status.replace('_', ' ')} color={STATUS_COLORS[job.status]} size="small" />
                    </TableCell>
                    <TableCell align="right">
                      {job.processed_count.toLocaleString()} / {job.total_emails.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">{job.error_count}</TableCell>
                    <TableCell>{formatDateTime(job.started_at)}</TableCell>
                    <TableCell>{formatDateTime(job.completed_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        )}
      </SectionCard>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar((s) => ({ ...s, open: false }))}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Stack>
  );
}
