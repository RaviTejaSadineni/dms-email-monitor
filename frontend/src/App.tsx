import { CircularProgress, Stack } from '@mui/material';
import type { ReactNode } from 'react';
import { Navigate, Outlet, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { ContractsPage } from './pages/ContractsPage';
import { DashboardPage } from './pages/DashboardPage';
import { EmailsPage } from './pages/EmailsPage';
import { FeatureCatalogPage } from './pages/FeatureCatalogPage';
import { ImportsPage } from './pages/ImportsPage';
import { InsightsPage } from './pages/InsightsPage';
import { LoginPage, RegisterPage } from './pages/LoginPage';
import { useAuth } from './store/useAuth';

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isInitializing } = useAuth();
  const location = useLocation();

  if (isInitializing) {
    return (
      <Stack alignItems="center" justifyContent="center" sx={{ minHeight: '100vh' }}>
        <CircularProgress />
      </Stack>
    );
  }

  if (!isAuthenticated) {
    const redirect = `${location.pathname}${location.search}`;
    return <Navigate replace to={`/login?redirect=${encodeURIComponent(redirect)}`} />;
  }

  return <>{children}</>;
}

function ProtectedLayout({ mode, onToggleMode }: { mode: 'light' | 'dark'; onToggleMode: () => void }) {
  const { logout, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <AppShell
      currentPath={location.pathname}
      mode={mode}
      onLogout={() => {
        logout();
        navigate('/login', { replace: true });
      }}
      onNavigate={(path) => navigate(path)}
      onToggleMode={onToggleMode}
      userEmail={user?.email}
      userName={user?.full_name}
    >
      <Outlet />
    </AppShell>
  );
}

function App({ mode, onToggleMode }: { mode: 'light' | 'dark'; onToggleMode: () => void }) {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        element={(
          <ProtectedRoute>
            <ProtectedLayout mode={mode} onToggleMode={onToggleMode} />
          </ProtectedRoute>
        )}
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/emails" element={<EmailsPage />} />
        <Route path="/contracts" element={<ContractsPage />} />
        <Route path="/imports" element={<ImportsPage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="/features" element={<FeatureCatalogPage />} />
      </Route>
      <Route path="*" element={<Navigate replace to="/" />} />
    </Routes>
  );
}

export default App;
