import React from 'react';
import { Activity, CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react';
import type { Job } from '../types';
import { formatRelativeTime, formatDuration } from '../utils/time';

interface JobsPanelProps {
  jobs: Job[];
}

export const JobsPanel: React.FC<JobsPanelProps> = ({ jobs }) => {
  if (jobs.length === 0) {
    return null;
  }

  const getStatusIcon = (status: Job['status']) => {
    switch (status) {
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: Job['status']) => {
    switch (status) {
      case 'running':
        return 'bg-blue-50 border-blue-200';
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center mb-4">
        <Activity className="w-5 h-5 mr-2 text-gray-700" />
        <h2 className="text-lg font-semibold text-gray-800">Background Jobs</h2>
        <span className="ml-auto text-sm text-gray-500">
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
                    <span className="font-medium text-gray-900 capitalize">
                      {job.type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatRelativeTime(job.created_at)}
                    </span>
                  </div>

                  {job.params && (
                    <div className="text-sm text-gray-600 mt-1">
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
                    <div className="text-xs text-blue-600 mt-1">
                      Running for {formatDuration(job.started_at)}
                    </div>
                  )}

                  {job.status === 'completed' && job.result && (
                    <div className="text-xs text-green-600 mt-1">
                      ✓ Success: {job.result.success} | Failed: {job.result.failed}
                      {job.started_at && job.completed_at && (
                        <span className="ml-2">
                          (took {formatDuration(job.started_at, job.completed_at)})
                        </span>
                      )}
                    </div>
                  )}

                  {job.status === 'failed' && job.error && (
                    <div className="text-xs text-red-600 mt-1">
                      ✗ Error: {job.error}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {jobs.length > 10 && (
        <div className="mt-3 text-center text-sm text-gray-500">
          Showing 10 of {jobs.length} jobs
        </div>
      )}
    </div>
  );
};
