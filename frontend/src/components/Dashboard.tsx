import React, { useEffect, useState } from 'react';
import { RefreshCw, AlertCircle, Activity } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { StatsCards } from './StatsCards';
import { AddTrademarkForm } from './AddTrademarkForm';
import { TrademarkTable } from './TrademarkTable';
import { JobsPanel } from './JobsPanel';
import { APIClient } from '../services/api';
import type { Job } from '../types';

export const Dashboard: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeJobs, setActiveJobs] = useState<string[]>([]);

  // Fetch trademarks
  const { data: trademarks, isLoading: loadingTrademarks, error: trademarksError, refetch: refetchTrademarks } = useQuery({
    queryKey: ['trademarks'],
    queryFn: APIClient.getAllTrademarks,
    staleTime: 10000,
  });

  // Fetch all jobs
  const { data: jobs, refetch: refetchJobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: APIClient.getAllJobs,
    staleTime: 5000,
  });

  // Poll for running jobs
  useEffect(() => {
    const interval = setInterval(() => {
      if (jobs?.some(j => j.status === 'running')) {
        refetchJobs();
        // Also refetch trademarks if there are running jobs
        refetchTrademarks();
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [jobs, refetchJobs, refetchTrademarks]);

  // Mutation for starting ingestion
  const ingestMutation = useMutation({
    mutationFn: async (params: { applicationNumber?: string; wordmark?: string; className?: string }) => {
      if (params.applicationNumber) {
        return APIClient.ingestByApplicationNumber(params.applicationNumber);
      } else if (params.wordmark && params.className) {
        return APIClient.ingestByWordmarkAndClass(params.wordmark, params.className);
      }
      throw new Error('Invalid parameters');
    },
    onSuccess: (data) => {
      setActiveJobs(prev => [...prev, data.job_id]);
      refetchJobs();
      // Start polling for this specific job
      setTimeout(() => refetchTrademarks(), 5000);
    },
  });

  const handleAddTrademark = (params: { applicationNumber?: string; wordmark?: string; className?: string }) => {
    ingestMutation.mutate(params);
  };

  const handleRefresh = (applicationNumber: string) => {
    ingestMutation.mutate({ applicationNumber });
  };

  const handleRefreshAll = async () => {
    try {
      const response = await APIClient.ingestAll();
      setActiveJobs(prev => [...prev, response.job_id]);
      refetchJobs();
      setTimeout(() => refetchTrademarks(), 5000);
    } catch (error) {
      console.error('Failed to start refresh all:', error);
    }
  };

  const runningJobsCount = jobs?.filter(j => j.status === 'running').length || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                AutoIPIndia Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Indian Trademark Status Management
              </p>
            </div>
            <div className="flex items-center space-x-3">
              {runningJobsCount > 0 && (
                <div className="flex items-center px-3 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium">
                  <Activity className="w-4 h-4 mr-2 animate-pulse" />
                  {runningJobsCount} job{runningJobsCount > 1 ? 's' : ''} running
                </div>
              )}
              <button
                onClick={handleRefreshAll}
                disabled={loadingTrademarks || runningJobsCount >= 5}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed shadow-sm transition-all duration-200"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loadingTrademarks ? 'animate-spin' : ''}`} />
                Refresh All
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success Message */}
        {ingestMutation.isSuccess && ingestMutation.data && (
          <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-400 rounded-r-lg shadow-sm">
            <p className="text-sm font-medium text-green-800">
              ✓ {ingestMutation.data.message}
            </p>
          </div>
        )}

        {/* Error Message */}
        {(trademarksError || ingestMutation.error) && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg flex items-start shadow-sm">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">Error occurred</p>
              <p className="text-sm text-red-600 mt-1">
                {trademarksError instanceof Error ? trademarksError.message :
                 ingestMutation.error instanceof Error ? ingestMutation.error.message :
                 'Unknown error'}
              </p>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        {trademarks && <StatsCards trademarks={trademarks} />}

        {/* Jobs Panel */}
        {jobs && jobs.length > 0 && <JobsPanel jobs={jobs} />}

        {/* Add Trademark Form */}
        <AddTrademarkForm onSubmit={handleAddTrademark} isLoading={ingestMutation.isPending} />

        {/* Loading State */}
        {loadingTrademarks && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
              <span className="mt-3 text-gray-600 block">Loading trademarks...</span>
            </div>
          </div>
        )}

        {/* Table */}
        {trademarks && trademarks.length > 0 && (
          <TrademarkTable
            data={trademarks}
            onRefresh={handleRefresh}
            isRefreshing={ingestMutation.isPending}
          />
        )}

        {/* Empty State */}
        {trademarks && trademarks.length === 0 && !loadingTrademarks && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="max-w-sm mx-auto">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No trademarks yet</h3>
              <p className="text-gray-600">Add your first trademark using the form above to get started!</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
