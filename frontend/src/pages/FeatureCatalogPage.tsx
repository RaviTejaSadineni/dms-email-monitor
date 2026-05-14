import { Accordion, AccordionDetails, AccordionSummary, Chip, Stack, Typography } from '@mui/material';
import { SectionCard } from '../components/common/SectionCard';
import { useDashboardData } from '../hooks/useDashboardData';

export function FeatureCatalogPage() {
  const { features } = useDashboardData();
  const groups = features.data ?? [];
  const total = groups.reduce((accumulator, group) => accumulator + group.items.length, 0);

  return (
    <SectionCard title="130+ mandatory features catalog" action={<Chip color="primary" label={`${total} features`} />}>
      <Stack spacing={1.5}>
        {groups.map((group) => (
          <Accordion key={group.area} disableGutters>
            <AccordionSummary>
              <Typography variant="subtitle1">{group.area}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
                {group.items.map((item) => (
                  <Chip key={item} label={item} variant="outlined" className="justify-start" />
                ))}
              </div>
            </AccordionDetails>
          </Accordion>
        ))}
      </Stack>
    </SectionCard>
  );
}
