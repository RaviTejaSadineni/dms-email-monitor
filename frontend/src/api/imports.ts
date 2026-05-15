import { getJson, postFormData, postJson } from './client';

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

export interface ImportJobLiveEvent {
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
}

export interface ImportJobLiveStats {
  job_id: number;
  status: ImportJob['status'];
  total_emails: number;
  processed_count: number;
  error_count: number;
  threads_created: number;
  contracts_found: number;
  attachments_extracted: number;
  spam_filtered: number;
  emails_per_second: number;
  estimated_remaining_seconds: number | null;
  current_batch_start: number;
  category_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
  recent_events: ImportJobLiveEvent[];
  current_email_subject: string | null;
}

export const importsApi = {
  createJob: (mboxPath: string, batchSize: number): Promise<ImportJob> =>
    postJson<ImportJob>('/import/jobs', { mbox_path: mboxPath, batch_size: batchSize }),

  createJobFromUpload: (
    file: File,
    batchSize: number,
    onUploadProgress?: (percent: number) => void,
  ): Promise<ImportJob> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('batch_size', String(batchSize));
    return postFormData<ImportJob>('/import/upload', formData, { onUploadProgress });
  },

  getJobProgress: (jobId: number): Promise<ImportJob> =>
    getJson<ImportJob>(`/import/jobs/${jobId}/progress`),

  getJobLiveStats: (jobId: number): Promise<ImportJobLiveStats> =>
    getJson<ImportJobLiveStats>(`/import/jobs/${jobId}/live-stats`),

  listJobs: (): Promise<ImportJob[]> =>
    getJson<ImportJob[]>('/import/jobs'),
};
