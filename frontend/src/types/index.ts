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

export interface CSVImportResponse extends IngestResponse {
  valid_count: number;
  error_count: number;
  errors: Array<{
    row: number;
    data: Record<string, any>;
    error: string;
  }>;
}

export interface CSVRow {
  id: string;
  application_number?: string;
  wordmark?: string;
  class_name?: string | number;
  isValid?: boolean;
  error?: string;
}

export interface Stats {
  total: number;
  registered: number;
  pending: number;
  other: number;
}
