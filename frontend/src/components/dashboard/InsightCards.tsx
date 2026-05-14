import { Chip, Stack, Typography } from '@mui/material';
import { SectionCard } from '../common/SectionCard';

export function InsightCards({ items }: { items: Array<{ title: string; content: string; confidence: number }> }) {
  return (
    <SectionCard title="AI insights & recommendations">
      <Stack spacing={2}>
        {items.map((item) => (
          <div key={item.title} className="rounded-3xl border border-slate-200/70 p-4 dark:border-slate-700">
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1.5}>
              <Typography variant="subtitle1">{item.title}</Typography>
              <Chip size="small" label={`${Math.round(item.confidence * 100)}% confidence`} color="secondary" />
            </Stack>
            <Typography color="text.secondary">{item.content}</Typography>
          </div>
        ))}
      </Stack>
    </SectionCard>
  );
}
