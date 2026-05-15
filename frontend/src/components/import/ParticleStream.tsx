import { Box } from '@mui/material';
import { motion } from 'framer-motion';

const PRIORITY_COLORS: Record<string, string> = {
  P1: '#ef5350',
  P2: '#ff9800',
  P3: '#fdd835',
  P4: '#66bb6a',
};

type Props = {
  priorityDistribution: Record<string, number>;
  speed: number;
};

export function ParticleStream({ priorityDistribution, speed }: Props) {
  const particles = Object.entries(priorityDistribution)
    .flatMap(([priority, count]) =>
      Array.from({ length: Math.min(Math.max(Math.round(count / 20), count > 0 ? 1 : 0), 8) }).map((_, index) => ({
        id: `${priority}-${index}`,
        priority,
      })),
    )
    .slice(0, 24);

  const duration = Math.max(0.8, 4 - Math.min(speed, 20) * 0.12);

  return (
    <Box
      sx={{
        position: 'relative',
        height: 100,
        borderRadius: 2,
        bgcolor: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.08)',
        overflow: 'hidden',
      }}
    >
      <Box sx={{ position: 'absolute', left: 8, top: '50%', transform: 'translateY(-50%)', color: 'grey.400', fontSize: 12 }}>MBOX</Box>
      <Box sx={{ position: 'absolute', left: '46%', top: '50%', transform: 'translateY(-50%)', color: 'grey.400', fontSize: 18 }}>⚙</Box>
      <Box sx={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', color: 'grey.400', fontSize: 12 }}>DB</Box>
      {particles.map((particle, index) => {
        const top = 18 + (index % 7) * 10;
        const color = PRIORITY_COLORS[particle.priority] ?? '#90a4ae';
        return (
          <motion.div
            key={particle.id}
            initial={{ x: -24, opacity: 0.2 }}
            animate={{ x: 560, opacity: [0.2, 1, 0.2] }}
            transition={{ duration, ease: 'linear', repeat: Infinity, delay: index * 0.1 }}
            style={{
              position: 'absolute',
              left: 24,
              top,
              width: 6,
              height: 6,
              borderRadius: '999px',
              background: color,
              boxShadow: `0 0 10px ${color}`,
            }}
          />
        );
      })}
    </Box>
  );
}
