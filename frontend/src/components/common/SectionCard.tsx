import { Card, CardContent, Stack, Typography } from '@mui/material';
import type { PropsWithChildren, ReactNode } from 'react';

export function SectionCard({ title, action, children }: PropsWithChildren<{ title: string; action?: ReactNode }>) {
  return (
    <Card className="rounded-3xl">
      <CardContent>
        <Stack spacing={2.5}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{title}</Typography>
            {action}
          </Stack>
          {children}
        </Stack>
      </CardContent>
    </Card>
  );
}
