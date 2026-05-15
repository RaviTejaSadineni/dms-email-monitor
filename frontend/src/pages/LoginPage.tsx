import { Alert, Box, Button, Card, CardContent, Stack, Tab, Tabs, TextField, Typography } from '@mui/material';
import { useMemo, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../store/useAuth';

type AuthMode = 'login' | 'register';

function AuthPage({ mode }: { mode: AuthMode }) {
  const { isAuthenticated, login, register } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const redirectPath = searchParams.get('redirect') || '/';

  if (isAuthenticated) {
    return <Navigate replace to={redirectPath} />;
  }

  const handleSubmit = async () => {
    setError(null);
    setIsSubmitting(true);
    try {
      if (mode === 'login') {
        await login({ email, password });
      } else {
        await register({ email, password, full_name: fullName });
      }
      navigate(redirectPath, { replace: true });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Authentication failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', px: 2, py: 4 }}>
      <Card sx={{ width: '100%', maxWidth: 480, borderRadius: 5 }}>
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={3}>
            <div>
              <Typography variant="h4">Legal Contract Intelligence Platform</Typography>
              <Typography color="text.secondary" mt={1}>
                Sign in to access dashboards, imports, insights, and contract analytics.
              </Typography>
            </div>
            <Tabs value={mode} onChange={(_, value: AuthMode) => navigate(`${value === 'login' ? '/login' : '/register'}${location.search}`)}>
              <Tab label="Login" value="login" />
              <Tab label="Register" value="register" />
            </Tabs>
            {error ? <Alert severity="error">{error}</Alert> : null}
            <Stack
              component="form"
              spacing={2.5}
              onSubmit={(event) => {
                event.preventDefault();
                void handleSubmit();
              }}
            >
              {mode === 'register' ? (
                <TextField
                  label="Full name"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  autoComplete="name"
                  required
                />
              ) : null}
              <TextField
                label="Email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                required
              />
              <Button type="submit" variant="contained" size="large" disabled={isSubmitting}>
                {isSubmitting ? 'Please wait…' : mode === 'login' ? 'Login' : 'Create account'}
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}

export function LoginPage() {
  return <AuthPage mode="login" />;
}

export function RegisterPage() {
  return <AuthPage mode="register" />;
}
