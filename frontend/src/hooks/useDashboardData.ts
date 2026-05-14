import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api/dashboard';

export const useDashboardData = () => {
  const token = undefined;
  const summary = useQuery({ queryKey: ['summary'], queryFn: () => dashboardApi.summary(token) });
  const insights = useQuery({ queryKey: ['insights'], queryFn: () => dashboardApi.insights(token) });
  const emails = useQuery({ queryKey: ['emails'], queryFn: () => dashboardApi.emails(token) });
  const contracts = useQuery({ queryKey: ['contracts'], queryFn: () => dashboardApi.contracts(token) });
  const attachments = useQuery({ queryKey: ['attachments'], queryFn: () => dashboardApi.attachments(token) });
  const features = useQuery({ queryKey: ['features'], queryFn: () => dashboardApi.features() });

  return { summary, insights, emails, contracts, attachments, features };
};
