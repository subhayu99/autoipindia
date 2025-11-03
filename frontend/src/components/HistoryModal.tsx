import React, { useEffect, useState } from 'react';
import { X, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { APIClient } from '../services/api';
import type { Trademark } from '../types';
import { formatRelativeTime } from '../utils/time';

interface HistoryModalProps {
  applicationNumber: string;
  isOpen: boolean;
  onClose: () => void;
}

export const HistoryModal: React.FC<HistoryModalProps> = ({ applicationNumber, isOpen, onClose }) => {
  const [history, setHistory] = useState<Trademark[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && applicationNumber) {
      loadHistory();
    }
  }, [isOpen, applicationNumber]);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await APIClient.getHistoryByApplicationNumber(applicationNumber);
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const isFailed = (status: string) => status.includes('!FAILED');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Status History</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Application Number: <span className="font-semibold">{applicationNumber}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600 dark:text-gray-400">Loading history...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800 dark:text-red-300">Error loading history</p>
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && history.length === 0 && (
            <div className="text-center py-12">
              <Clock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 dark:text-gray-400">No history available for this trademark</p>
            </div>
          )}

          {!loading && !error && history.length > 0 && (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

              {/* Timeline items */}
              <div className="space-y-6">
                {history.map((item, index) => {
                  const failed = isFailed(item.status);
                  return (
                    <div key={`${item.timestamp}-${index}`} className="relative pl-12">
                      {/* Timeline dot */}
                      <div className={`absolute left-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        failed
                          ? 'bg-red-600 dark:bg-red-700'
                          : 'bg-green-500 dark:bg-green-600'
                      } shadow-lg`}>
                        {failed ? (
                          <AlertCircle className="w-5 h-5 text-white" />
                        ) : (
                          <CheckCircle className="w-5 h-5 text-white" />
                        )}
                      </div>

                      {/* Content card */}
                      <div className={`rounded-lg p-4 shadow-sm border-2 ${
                        failed
                          ? 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-800'
                          : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600'
                      }`}>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                                failed
                                  ? 'bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300'
                                  : 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300'
                              }`}>
                                {failed ? 'System Failure' : item.status}
                              </span>
                              {index === 0 && (
                                <span className="text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 px-2 py-1 rounded-full font-medium">
                                  Latest
                                </span>
                              )}
                            </div>

                            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                              <div className="flex items-center">
                                <span className="font-medium w-24">Wordmark:</span>
                                <span>{item.wordmark}</span>
                              </div>
                              <div className="flex items-center">
                                <span className="font-medium w-24">Class:</span>
                                <span>{item.class_name}</span>
                              </div>
                            </div>
                          </div>

                          <div className="text-right ml-4">
                            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                              <Clock className="w-4 h-4 mr-1" />
                              <span title={new Date(item.timestamp).toLocaleString()}>
                                {formatRelativeTime(item.timestamp)}
                              </span>
                            </div>
                            <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                              {new Date(item.timestamp).toLocaleString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
