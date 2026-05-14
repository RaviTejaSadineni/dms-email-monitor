import { Divider, Stack } from '@mui/material';
import { ContractsPage } from './pages/ContractsPage';
import { DashboardPage } from './pages/DashboardPage';
import { EmailsPage } from './pages/EmailsPage';
import { FeatureCatalogPage } from './pages/FeatureCatalogPage';
import { ImportsPage } from './pages/ImportsPage';
import { InsightsPage } from './pages/InsightsPage';

function App() {
  return (
    <Stack spacing={3}>
      <DashboardPage />
      <Divider flexItem />
      <EmailsPage />
      <Divider flexItem />
      <ContractsPage />
      <Divider flexItem />
      <ImportsPage />
      <Divider flexItem />
      <InsightsPage />
      <Divider flexItem />
      <FeatureCatalogPage />
    </Stack>
  );
}

export default App;
