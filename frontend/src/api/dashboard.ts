import { getJson } from './client';
import { demoAttachments, demoContracts, demoEmails, demoFeatures, demoInsights, demoSummary } from '../utils/demoData';

export type MetricCard = { title: string; value: string | number; subtitle?: string };
export type ChartPoint = { label: string; value: number };
export type StageMetric = { stage: string; count: number; average_hours: number; breach_rate: number };
export type SummaryResponse = {
  metrics: MetricCard[];
  priority_distribution: ChartPoint[];
  category_distribution: ChartPoint[];
  lifecycle_pipeline: StageMetric[];
  email_volume: ChartPoint[];
  response_time_distribution: ChartPoint[];
  stakeholder_activity: ChartPoint[];
};

async function withFallback<T>(factory: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await factory();
  } catch {
    return fallback;
  }
}

export const dashboardApi = {
  summary: (token?: string) => withFallback(() => getJson<SummaryResponse>('/analytics/summary', token), demoSummary),
  insights: (token?: string) => withFallback(() => getJson<{ items: typeof demoInsights }>('/ai-insights/overview', token), { items: demoInsights }),
  emails: (token?: string) => withFallback(() => getJson<{ items: typeof demoEmails; pagination: { total: number; page: number; page_size: number } }>('/emails', token), { items: demoEmails, pagination: { total: demoEmails.length, page: 1, page_size: demoEmails.length } }),
  contracts: (token?: string) => withFallback(() => getJson<{ items: typeof demoContracts; pagination: { total: number; page: number; page_size: number } }>('/contracts', token), { items: demoContracts, pagination: { total: demoContracts.length, page: 1, page_size: demoContracts.length } }),
  attachments: (token?: string) => withFallback(() => getJson<{ items: typeof demoAttachments }>('/attachments', token), { items: demoAttachments }),
  features: async () => demoFeatures,
};
