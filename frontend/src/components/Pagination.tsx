import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import type { PaginationMeta } from '../types';

interface PaginationProps {
  pagination: PaginationMeta;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ pagination, onPageChange }) => {
  const { page, total_pages, has_prev, has_next, total } = pagination;

  const handleFirstPage = () => onPageChange(1);
  const handlePrevPage = () => onPageChange(page - 1);
  const handleNextPage = () => onPageChange(page + 1);
  const handleLastPage = () => onPageChange(total_pages);

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7;

    if (total_pages <= maxVisible) {
      // Show all pages
      for (let i = 1; i <= total_pages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);

      if (page <= 3) {
        // Near start
        for (let i = 2; i <= 4; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(total_pages);
      } else if (page >= total_pages - 2) {
        // Near end
        pages.push('...');
        for (let i = total_pages - 3; i <= total_pages; i++) {
          pages.push(i);
        }
      } else {
        // Middle
        pages.push('...');
        pages.push(page - 1);
        pages.push(page);
        pages.push(page + 1);
        pages.push('...');
        pages.push(total_pages);
      }
    }

    return pages;
  };

  return (
    <div className="flex items-center justify-between px-4 py-3 sm:px-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div className="flex-1 flex justify-between sm:hidden">
        <button
          onClick={handlePrevPage}
          disabled={!has_prev}
          className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={handleNextPage}
          disabled={!has_next}
          className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>

      <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-gray-700 dark:text-gray-300">
            Showing page <span className="font-medium">{page}</span> of{' '}
            <span className="font-medium">{total_pages}</span> ({total} total results)
          </p>
        </div>
        <div>
          <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            {/* First Page */}
            <button
              onClick={handleFirstPage}
              disabled={!has_prev}
              className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">First</span>
              <ChevronsLeft className="h-5 w-5" />
            </button>

            {/* Previous Page */}
            <button
              onClick={handlePrevPage}
              disabled={!has_prev}
              className="relative inline-flex items-center px-2 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">Previous</span>
              <ChevronLeft className="h-5 w-5" />
            </button>

            {/* Page Numbers */}
            {getPageNumbers().map((pageNum, idx) =>
              typeof pageNum === 'number' ? (
                <button
                  key={idx}
                  onClick={() => onPageChange(pageNum)}
                  className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                    page === pageNum
                      ? 'z-10 bg-blue-50 dark:bg-blue-900 border-blue-500 text-blue-600 dark:text-blue-200'
                      : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600'
                  }`}
                >
                  {pageNum}
                </button>
              ) : (
                <span
                  key={idx}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  {pageNum}
                </span>
              )
            )}

            {/* Next Page */}
            <button
              onClick={handleNextPage}
              disabled={!has_next}
              className="relative inline-flex items-center px-2 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">Next</span>
              <ChevronRight className="h-5 w-5" />
            </button>

            {/* Last Page */}
            <button
              onClick={handleLastPage}
              disabled={!has_next}
              className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">Last</span>
              <ChevronsRight className="h-5 w-5" />
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
};
