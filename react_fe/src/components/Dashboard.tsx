import React from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';
import { StatsCards } from './StatsCards';
import { AddTrademarkForm } from './AddTrademarkForm';
import { TrademarkTable } from './TrademarkTable';
import { useTrademarks } from '../hooks/useTrademarks';

export const Dashboard: React.FC = () => {
  const { trademarks, isLoading, error, refetch, ingest, isIngesting, ingestError, ingestResult } = useTrademarks();

  const handleAddTrademark = (params: { applicationNumber?: string; wordmark?: string; className?: string }) => {
    ingest(params);
  };

  const handleRefresh = (applicationNumber: string) => {
    ingest({ applicationNumber });
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AutoIPIndia Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Indian Trademark Status Management
              </p>
            </div>
            <button
              onClick={() => refetch()}
              disabled={isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh All
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success Message */}
        {ingestResult && !ingestError && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-800">
              Successfully ingested: {ingestResult.success}, Failed: {ingestResult.failed}
            </p>
          </div>
        )}

        {/* Error Message */}
        {(error || ingestError) && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">Error occurred</p>
              <p className="text-sm text-red-600 mt-1">
                {error instanceof Error ? error.message : ingestError instanceof Error ? ingestError.message : 'Unknown error'}
              </p>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        {trademarks && <StatsCards trademarks={trademarks} />}

        {/* Add Trademark Form */}
        <AddTrademarkForm onSubmit={handleAddTrademark} isLoading={isIngesting} />

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            <span className="ml-3 text-gray-600">Loading trademarks...</span>
          </div>
        )}

        {/* Table */}
        {trademarks && trademarks.length > 0 && (
          <TrademarkTable
            data={trademarks}
            onRefresh={handleRefresh}
            isRefreshing={isIngesting}
          />
        )}

        {/* Empty State */}
        {trademarks && trademarks.length === 0 && !isLoading && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <p className="text-gray-600">No trademarks found. Add one above to get started!</p>
          </div>
        )}
      </main>
    </div>
  );
};
