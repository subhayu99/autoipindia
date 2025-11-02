import axios from 'axios';
import type { Trademark, IngestResult } from '../types';

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

  static async ingestByApplicationNumber(applicationNumber: string): Promise<IngestResult> {
    const response = await api.get<IngestResult>(`/ingest/tm/${applicationNumber}`);
    return response.data;
  }

  static async ingestByWordmarkAndClass(wordmark: string, className: string): Promise<IngestResult> {
    const response = await api.get<IngestResult>('/ingest/tm', {
      params: { wordmark, class_name: className },
    });
    return response.data;
  }

  static async ingestAll(staleSinceDays: number = 15): Promise<IngestResult> {
    const response = await api.get<IngestResult>('/ingest/all', {
      params: { stale_since_days: staleSinceDays },
    });
    return response.data;
  }
}
