import { Box, Card, Chip, Stack, Typography } from '@mui/material';
import { motion } from 'framer-motion';

import type { ImportJob, ImportJobLiveStats } from '../../api/imports';
import { CategoryLanes } from './CategoryLanes';
import { LiveLogFeed } from './LiveLogFeed';
import { ParticleStream } from './ParticleStream';

type Props = {
  job: ImportJob;
  stats: ImportJobLiveStats | null;
};

const FALLBACK_CATEGORY = {
  'Legal Review': 0,
  'Finance Review': 0,
  Negotiation: 0,
  General: 0,
  Spam: 0,
};

const FALLBACK_PRIORITY = {
  P1: 0,
  P2: 0,
  P3: 0,
  P4: 0,
};

function formatEta(seconds: number | null): string {
  if (seconds === null || seconds < 0) return '—';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <motion.div animate={{ scale: [1, 1.03, 1] }} transition={{ duration: 0.6 }}>
      <Card sx={{ p: 1.25, bgcolor: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
        <Typography variant="caption" color="grey.400">
          {label}
        </Typography>
        <Typography variant="h6" color="grey.100">
          {value}
        </Typography>
      </Card>
    </motion.div>
  );
}

export function ImportVisualizer({ job, stats }: Props) {
  const total = stats?.total_emails ?? job.total_emails;
  const processed = stats?.processed_count ?? job.processed_count;
  const progressPct = total > 0 ? Math.min(100, Math.round((processed / total) * 100)) : 0;
  const ringDegrees = (progressPct / 100) * 360;
  const categoryDistribution = stats?.category_distribution ?? FALLBACK_CATEGORY;
  const priorityDistribution = stats?.priority_distribution ?? FALLBACK_PRIORITY;

  return (
    <Stack spacing={2} sx={{ p: 2, borderRadius: 3, bgcolor: '#0f1726', border: '1px solid rgba(144,202,249,0.2)' }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="subtitle1" color="grey.100">
          3D Import Visualization
        </Typography>
        <Chip label={`${progressPct}%`} color="info" size="small" />
      </Stack>

      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', md: '5fr 7fr' } }}>
        <Box>
          <Stack spacing={2}>
            <Box
              sx={{
                height: 220,
                borderRadius: 2,
                position: 'relative',
                perspective: '1000px',
                transform: 'perspective(1000px) rotateY(5deg)',
                bgcolor: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', left: 24, right: 24, top: 18, bottom: 18, borderRadius: 1.5, bgcolor: 'rgba(103,58,183,0.2)' }} />
              <motion.div
                animate={{ top: `${progressPct}%` }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
                style={{
                  position: 'absolute',
                  left: 18,
                  right: 18,
                  height: 6,
                  borderRadius: 999,
                  background: 'linear-gradient(90deg, rgba(66,165,245,0), rgba(66,165,245,0.95), rgba(66,165,245,0))',
                  boxShadow: '0 0 24px rgba(66,165,245,0.85)',
                }}
              />
              {Array.from({ length: 7 }).map((_, idx) => (
                <motion.div
                  key={idx}
                  animate={{ x: [40, 240, 430], y: [40 + idx * 22, 20 + idx * 18, 55 + idx * 14], opacity: [0, 1, 0] }}
                  transition={{ duration: 2.2, repeat: Infinity, delay: idx * 0.22 }}
                  style={{ position: 'absolute', fontSize: 16 }}
                >
                  ✉️
                </motion.div>
              ))}
            </Box>

            <Box sx={{ position: 'relative', width: 180, height: 180, mx: 'auto' }}>
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  borderRadius: '50%',
                  background: `conic-gradient(#42a5f5 ${ringDegrees}deg, rgba(255,255,255,0.1) ${ringDegrees}deg)`,
                  filter: 'drop-shadow(0 0 18px rgba(66,165,245,0.6))',
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  inset: 16,
                  borderRadius: '50%',
                  bgcolor: '#0f1726',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center',
                  px: 1,
                }}
              >
                <Typography variant="h5" color="grey.100">
                  {progressPct}%
                </Typography>
                <Typography variant="caption" color="grey.400" noWrap>
                  {(stats?.current_email_subject || 'Scanning emails...').slice(0, 40)}
                </Typography>
              </Box>
            </Box>
          </Stack>
        </Box>

        <Box>
          <Stack spacing={2}>
            <Box sx={{ display: 'grid', gap: 1, gridTemplateColumns: { xs: 'repeat(2, minmax(0, 1fr))', md: 'repeat(3, minmax(0, 1fr))' } }}>
              <Box>
                <StatCard label="Emails scanned" value={processed.toLocaleString()} />
              </Box>
              <Box>
                <StatCard label="Threads" value={(stats?.threads_created ?? 0).toLocaleString()} />
              </Box>
              <Box>
                <StatCard label="Contracts" value={(stats?.contracts_found ?? 0).toLocaleString()} />
              </Box>
              <Box>
                <StatCard label="Attachments" value={(stats?.attachments_extracted ?? 0).toLocaleString()} />
              </Box>
              <Box>
                <StatCard label="Spam filtered" value={(stats?.spam_filtered ?? 0).toLocaleString()} />
              </Box>
              <Box>
                <StatCard label="Speed" value={`${(stats?.emails_per_second ?? 0).toFixed(1)} e/s`} />
              </Box>
            </Box>

            <Typography variant="caption" color="grey.400">
              ETA: {formatEta(stats?.estimated_remaining_seconds ?? null)}
            </Typography>

            <CategoryLanes distribution={categoryDistribution} />
            <ParticleStream priorityDistribution={priorityDistribution} speed={stats?.emails_per_second ?? 0} />
            <LiveLogFeed events={stats?.recent_events ?? []} />
          </Stack>
        </Box>
      </Box>
    </Stack>
  );
}
