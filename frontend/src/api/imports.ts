import { getJson, postJson } from './client';

export interface ImportJobError {
  batch_start: number;
  error: string;
}

export interface ImportJob {
  id: number;
  filename: string;
  file_size_bytes: number;
  status: 'queued' | 'running' | 'completed' | 'completed_with_errors' | 'failed';
  total_emails: number;
  processed_count: number;
  error_count: number;
  errors: ImportJobError[];
  started_at: string | null;
  completed_at: string | null;
}

export const importsApi = {
  createJob: (mboxPath: string, batchSize: number): Promise<ImportJob> =>
    postJson<ImportJob>('/import/jobs', { mbox_path: mboxPath, batch_size: batchSize }),

  getJobProgress: (jobId: number): Promise<ImportJob> =>
    getJson<ImportJob>(`/import/jobs/${jobId}/progress`),

  listJobs: (): Promise<ImportJob[]> =>
    getJson<ImportJob[]>('/import/jobs'),
};
