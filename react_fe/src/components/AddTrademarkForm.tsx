import React, { useState } from 'react';
import { Plus, Loader2 } from 'lucide-react';

interface AddTrademarkFormProps {
  onSubmit: (params: { applicationNumber?: string; wordmark?: string; className?: string }) => void;
  isLoading: boolean;
}

export const AddTrademarkForm: React.FC<AddTrademarkFormProps> = ({ onSubmit, isLoading }) => {
  const [applicationNumber, setApplicationNumber] = useState('');
  const [wordmark, setWordmark] = useState('');
  const [className, setClassName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (applicationNumber) {
      onSubmit({ applicationNumber });
      setApplicationNumber('');
    } else if (wordmark && className) {
      onSubmit({ wordmark, className });
      setWordmark('');
      setClassName('');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center mb-4">
        <Plus className="w-5 h-5 mr-2 text-gray-700" />
        <h2 className="text-lg font-semibold text-gray-800">Add New Trademark</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-7 gap-4 items-end">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Application Number
            </label>
            <input
              type="text"
              value={applicationNumber}
              onChange={(e) => setApplicationNumber(e.target.value)}
              placeholder="e.g., 1234567"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center justify-center">
            <span className="text-gray-500 font-medium">OR</span>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Wordmark
            </label>
            <input
              type="text"
              value={wordmark}
              onChange={(e) => setWordmark(e.target.value)}
              placeholder="e.g., NIKE"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Class
            </label>
            <input
              type="number"
              value={className}
              onChange={(e) => setClassName(e.target.value)}
              placeholder="e.g., 25"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || (!applicationNumber && (!wordmark || !className))}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Ingesting...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-2" />
                Ingest
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
