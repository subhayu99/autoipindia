export interface Trademark {
  application_number: string;
  wordmark: string;
  class_name: string | number;
  status: string;
  timestamp: string;
}

export interface Job {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: {
    success: number;
    failed: number;
  };
  error?: string;
  params?: Record<string, any>;
}

export interface IngestResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface Stats {
  total: number;
  registered: number;
  pending: number;
  other: number;
}
