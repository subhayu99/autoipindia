import React, { useState } from 'react';
import { Search, X } from 'lucide-react';
import type { SearchFilters as Filters } from '../types';

interface SearchFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  onSearch: () => void;
}

export const SearchFilters: React.FC<SearchFiltersProps> = ({ filters, onFiltersChange, onSearch }) => {
  const [localFilters, setLocalFilters] = useState<Filters>(filters);

  const handleInputChange = (field: keyof Filters, value: string) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value || undefined
    }));
  };

  const handleSearch = () => {
    onFiltersChange(localFilters);
    onSearch();
  };

  const handleClear = () => {
    const emptyFilters: Filters = {};
    setLocalFilters(emptyFilters);
    onFiltersChange(emptyFilters);
    onSearch();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const hasFilters = Object.values(localFilters).some(v => v);

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Wordmark Filter */}
        <div>
          <label htmlFor="wordmark" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Wordmark
          </label>
          <input
            type="text"
            id="wordmark"
            value={localFilters.wordmark || ''}
            onChange={(e) => handleInputChange('wordmark', e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search by wordmark..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>

        {/* Class Name Filter */}
        <div>
          <label htmlFor="class_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Class
          </label>
          <input
            type="text"
            id="class_name"
            value={localFilters.class_name || ''}
            onChange={(e) => handleInputChange('class_name', e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Filter by class..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>

        {/* Status Filter */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Status
          </label>
          <input
            type="text"
            id="status"
            value={localFilters.status || ''}
            onChange={(e) => handleInputChange('status', e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Filter by status..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>

        {/* Application Number Filter */}
        <div>
          <label htmlFor="application_number" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Application Number
          </label>
          <input
            type="text"
            id="application_number"
            value={localFilters.application_number || ''}
            onChange={(e) => handleInputChange('application_number', e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search by number..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 mt-4">
        <button
          onClick={handleSearch}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
        >
          <Search className="w-4 h-4" />
          Search
        </button>
        {hasFilters && (
          <button
            onClick={handleClear}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
          >
            <X className="w-4 h-4" />
            Clear
          </button>
        )}
      </div>
    </div>
  );
};
