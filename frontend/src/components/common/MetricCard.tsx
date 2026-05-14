import { Card, CardContent, Stack, Typography } from '@mui/material';

export type MetricCardProps = {
  title: string;
  value: string | number;
  subtitle?: string;
};

export function MetricCard({ title, value, subtitle }: MetricCardProps) {
  return (
    <Card className="h-full rounded-3xl">
      <CardContent>
        <Stack spacing={1.5}>
          <Typography color="text.secondary" variant="body2">{title}</Typography>
          <Typography variant="h4">{value}</Typography>
          {subtitle ? (
            <Typography color="text.secondary" variant="body2">{subtitle}</Typography>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
