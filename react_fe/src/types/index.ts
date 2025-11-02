export interface Trademark {
  application_number: string;
  wordmark: string;
  class_name: string | number;
  status: string;
  timestamp: string;
}

export interface IngestResult {
  success: number;
  failed: number;
  error?: string;
}

export interface Stats {
  total: number;
  registered: number;
  pending: number;
  other: number;
}
