import React, { useState } from 'react';
import { Activity, CheckCircle, XCircle, Clock, Loader2, Ban, StopCircle } from 'lucide-react';
import type { Job } from '../types';
import { formatRelativeTime, formatDuration } from '../utils/time';
import { APIClient } from '../services/api';

interface JobsPanelProps {
  jobs: Job[];
  onJobUpdate?: () => void;
}

export const JobsPanel: React.FC<JobsPanelProps> = ({ jobs, onJobUpdate }) => {
  const [cancellingJobs, setCancellingJobs] = useState<Set<string>>(new Set());

  if (jobs.length === 0) {
    return null;
  }

  const handleCancelJob = async (jobId: string) => {
    if (window.confirm('Are you sure you want to cancel this job?')) {
      try {
        setCancellingJobs(prev => new Set(prev).add(jobId));
        await APIClient.cancelJob(jobId);
        if (onJobUpdate) {
          onJobUpdate();
        }
      } catch (error) {
        console.error('Error cancelling job:', error);
        alert('Failed to cancel job. Please try again.');
      } finally {
        setCancellingJobs(prev => {
          const newSet = new Set(prev);
          newSet.delete(jobId);
          return newSet;
        });
      }
    }
  };

  const getStatusIcon = (status: Job['status']) => {
    switch (status) {
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500 dark:text-blue-400" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500 dark:text-green-400" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500 dark:text-red-400" />;
      case 'cancelled':
        return <Ban className="w-4 h-4 text-orange-500 dark:text-orange-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400 dark:text-gray-500" />;
    }
  };

  const getStatusColor = (status: Job['status']) => {
    switch (status) {
      case 'running':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700';
      case 'completed':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700';
      case 'failed':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700';
      case 'cancelled':
        return 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-700';
      default:
        return 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors">
      <div className="flex items-center mb-4">
        <Activity className="w-5 h-5 mr-2 text-gray-700 dark:text-gray-300" />
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Background Jobs</h2>
        <span className="ml-auto text-sm text-gray-500 dark:text-gray-400">
          {jobs.filter(j => j.status === 'running').length} running
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {jobs.slice(0, 10).map((job) => (
          <div
            key={job.id}
            className={`p-4 rounded-md border-2 ${getStatusColor(job.status)} transition-all duration-200`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                {getStatusIcon(job.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900 dark:text-white capitalize">
                      {job.type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {formatRelativeTime(job.created_at)}
                    </span>
                  </div>

                  {job.params && (
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {job.params.application_number && (
                        <span>App #: {job.params.application_number}</span>
                      )}
                      {job.params.wordmark && (
                        <span>{job.params.wordmark} (Class {job.params.class_name})</span>
                      )}
                      {job.params.count && (
                        <span>{job.params.count} trademarks</span>
                      )}
                    </div>
                  )}

                  {job.status === 'running' && job.started_at && (
                    <div className="mt-2 space-y-1">
                      <div className="text-xs text-blue-600 dark:text-blue-400">
                        Running for {formatDuration(job.started_at)}
                      </div>
                      {job.progress && (
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                            <span>{job.progress.message || 'Processing...'}</span>
                            <span>{job.progress.current}/{job.progress.total} ({job.progress.percentage.toFixed(1)}%)</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${job.progress.percentage}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {job.status === 'completed' && job.result && (
                    <div className="text-xs text-green-600 dark:text-green-400 mt-1">
                      ✓ Success: {job.result.success} | Failed: {job.result.failed}
                      {job.result.skipped && job.result.skipped > 0 && (
                        <span> | Skipped: {job.result.skipped}</span>
                      )}
                      {job.started_at && job.completed_at && (
                        <span className="ml-2">
                          (took {formatDuration(job.started_at, job.completed_at)})
                        </span>
                      )}
                    </div>
                  )}

                  {job.status === 'failed' && job.error && (
                    <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                      ✗ Error: {job.error}
                    </div>
                  )}

                  {job.status === 'cancelled' && (
                    <div className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                      ⊗ Job was cancelled
                    </div>
                  )}
                </div>
              </div>

              {/* Cancel button for running/pending jobs */}
              {(job.status === 'running' || job.status === 'pending') && (
                <div className="ml-2">
                  <button
                    onClick={() => handleCancelJob(job.id)}
                    disabled={cancellingJobs.has(job.id)}
                    className="px-3 py-1 text-xs bg-red-100 hover:bg-red-200 dark:bg-red-900/30 dark:hover:bg-red-900/50 text-red-700 dark:text-red-400 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                    title="Cancel job"
                  >
                    {cancellingJobs.has(job.id) ? (
                      <>
                        <div className="animate-spin rounded-full h-3 w-3 border-2 border-red-700 dark:border-red-400 border-t-transparent" />
                        Cancelling...
                      </>
                    ) : (
                      <>
                        <StopCircle className="w-3 h-3" />
                        Cancel
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {jobs.length > 10 && (
        <div className="mt-3 text-center text-sm text-gray-500 dark:text-gray-400">
          Showing 10 of {jobs.length} jobs
        </div>
      )}
    </div>
  );
};
