import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api/dashboard';
import { useAuth } from '../store/useAuth';

export const useDashboardData = () => {
  const { isAuthenticated } = useAuth();
  const summary = useQuery({ queryKey: ['summary'], queryFn: () => dashboardApi.summary(), enabled: isAuthenticated });
  const insights = useQuery({ queryKey: ['insights'], queryFn: () => dashboardApi.insights(), enabled: isAuthenticated });
  const emails = useQuery({ queryKey: ['emails'], queryFn: () => dashboardApi.emails(), enabled: isAuthenticated });
  const contracts = useQuery({ queryKey: ['contracts'], queryFn: () => dashboardApi.contracts(), enabled: isAuthenticated });
  const attachments = useQuery({ queryKey: ['attachments'], queryFn: () => dashboardApi.attachments(), enabled: isAuthenticated });
  const features = useQuery({ queryKey: ['features'], queryFn: () => dashboardApi.features(), enabled: isAuthenticated });

  return { summary, insights, emails, contracts, attachments, features };
};
