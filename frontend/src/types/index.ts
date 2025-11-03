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
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: {
    success: number;
    failed: number;
    skipped?: number;
  };
  error?: string;
  params?: Record<string, any>;
  progress?: {
    current: number;
    total: number;
    percentage: number;
    message: string;
  };
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

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse {
  data: Trademark[];
  pagination: PaginationMeta;
}

export interface SearchFilters {
  wordmark?: string;
  class_name?: string;
  status?: string;
  application_number?: string;
}

export interface BulkDeleteResponse {
  deleted: number;
  failed: number;
  errors: string[];
}

export interface HealthCheckResponse {
  status: string;
  version: string;
  database: string;
  service: string;
}
