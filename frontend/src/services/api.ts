import axios from 'axios';
import type {
  Trademark,
  IngestResponse,
  Job,
  CSVImportResponse,
  PaginatedResponse,
  SearchFilters,
  BulkDeleteResponse,
  HealthCheckResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    ...(API_TOKEN && { Authorization: `Bearer ${API_TOKEN}` }),
  },
});

export class APIClient {
  static async getAllTrademarks(): Promise<Trademark[]> {
    const response = await api.get<Trademark[]>('/retrieve/all');
    return response.data;
  }

  static async searchByApplicationNumber(applicationNumber: string): Promise<Trademark> {
    const response = await api.get<Trademark>(`/search/tm/${applicationNumber}`);
    return response.data;
  }

  static async searchByWordmarkAndClass(wordmark: string, className: string): Promise<Trademark> {
    const response = await api.get<Trademark>('/search/tm', {
      params: { wordmark, class_name: className },
    });
    return response.data;
  }

  static async ingestByApplicationNumber(applicationNumber: string): Promise<IngestResponse> {
    const response = await api.get<IngestResponse>(`/ingest/tm/${applicationNumber}`);
    return response.data;
  }

  static async ingestByWordmarkAndClass(wordmark: string, className: string): Promise<IngestResponse> {
    const response = await api.get<IngestResponse>('/ingest/tm', {
      params: { wordmark, class_name: className },
    });
    return response.data;
  }

  static async ingestAll(staleSinceDays: number = 15): Promise<IngestResponse> {
    const response = await api.get<IngestResponse>('/ingest/all', {
      params: { stale_since_days: staleSinceDays },
    });
    return response.data;
  }

  static async uploadCSV(file: File): Promise<CSVImportResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<CSVImportResponse>('/import/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        ...(API_TOKEN && { Authorization: `Bearer ${API_TOKEN}` }),
      },
    });
    return response.data;
  }

  // Job management endpoints
  static async getAllJobs(): Promise<Job[]> {
    const response = await api.get<Job[]>('/jobs');
    return response.data;
  }

  static async getJob(jobId: string): Promise<Job> {
    const response = await api.get<Job>(`/jobs/${jobId}`);
    return response.data;
  }

  static async getRunningJobs(): Promise<Job[]> {
    const response = await api.get<Job[]>('/jobs/status/running');
    return response.data;
  }

  // Delete trademark
  static async deleteByApplicationNumber(applicationNumber: string): Promise<Record<string, boolean>> {
    const response = await api.delete<Record<string, boolean>>(`/delete/tm/${applicationNumber}`);
    return response.data;
  }

  // Get trademark history
  static async getHistoryByApplicationNumber(applicationNumber: string): Promise<Trademark[]> {
    const response = await api.get<Trademark[]>(`/history/tm/${applicationNumber}`);
    return response.data;
  }

  // Pagination and filtering
  static async getPaginatedTrademarks(
    page: number = 1,
    pageSize: number = 50,
    filters?: SearchFilters
  ): Promise<PaginatedResponse> {
    const response = await api.get<PaginatedResponse>('/retrieve/paginated', {
      params: {
        page,
        page_size: pageSize,
        ...(filters?.wordmark && { wordmark: filters.wordmark }),
        ...(filters?.class_name && { class_name: filters.class_name }),
        ...(filters?.status && { status: filters.status }),
        ...(filters?.application_number && { application_number: filters.application_number }),
      },
    });
    return response.data;
  }

  // Bulk operations
  static async bulkDeleteTrademarks(applicationNumbers: string[]): Promise<BulkDeleteResponse> {
    const response = await api.post<BulkDeleteResponse>('/delete/bulk', {
      application_numbers: applicationNumbers,
    });
    return response.data;
  }

  // Export functionality
  static async exportToCSV(): Promise<Blob> {
    const response = await api.get('/export/csv', {
      responseType: 'blob',
    });
    return response.data;
  }

  static async exportToExcel(): Promise<Blob> {
    const response = await api.get('/export/excel', {
      responseType: 'blob',
    });
    return response.data;
  }

  // Job cancellation
  static async cancelJob(jobId: string): Promise<{ success: boolean; message: string }> {
    const response = await api.post<{ success: boolean; message: string }>(`/jobs/${jobId}/cancel`);
    return response.data;
  }

  // Health check
  static async healthCheck(): Promise<HealthCheckResponse> {
    const response = await api.get<HealthCheckResponse>('/health');
    return response.data;
  }
}
