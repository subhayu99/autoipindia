import axios from 'axios';
import type { Trademark, IngestResponse, Job } from '../types';

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
}
