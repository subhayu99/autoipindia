import React, { useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
  type ColumnFiltersState,
} from '@tanstack/react-table';
import { RefreshCw, ChevronLeft, ChevronRight, ArrowUpDown, Clock, Trash2 } from 'lucide-react';
import type { Trademark } from '../types';
import { formatRelativeTime } from '../utils/time';
import { HistoryModal } from './HistoryModal';

interface TrademarkTableProps {
  data: Trademark[];
  onRefresh: (applicationNumber: string) => void;
  onDelete: (applicationNumber: string) => void;
  isRefreshing: boolean;
  isDark?: boolean;
}

const columnHelper = createColumnHelper<Trademark>();

export const TrademarkTable: React.FC<TrademarkTableProps> = ({ data, onRefresh, onDelete, isRefreshing }) => {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [historyApplicationNumber, setHistoryApplicationNumber] = useState('');

  const handleRowClick = (trademark: Trademark) => {
    setHistoryApplicationNumber(trademark.application_number);
    setHistoryModalOpen(true);
  };

  const columns = useMemo(
    () => [
      columnHelper.accessor('application_number', {
        header: 'Application Number',
        cell: (info) => (
          <span className="font-medium text-blue-600 dark:text-blue-400">{info.getValue()}</span>
        ),
      }),
      columnHelper.accessor('wordmark', {
        header: 'Wordmark',
        cell: (info) => (
          <span className="font-semibold dark:text-gray-200">{info.getValue()}</span>
        ),
      }),
      columnHelper.accessor('class_name', {
        header: 'Class',
        cell: (info) => (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
            {info.getValue()}
          </span>
        ),
      }),
      columnHelper.accessor('status', {
        header: 'Status',
        cell: (info) => {
          const status = info.getValue();
          const isRegistered = status.toLowerCase().includes('registered');
          const isPending = status.toLowerCase().includes('pending') || status.toLowerCase().includes('examination');

          return (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              isRegistered ? 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300' :
              isPending ? 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300' :
              'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
            }`}>
              {status}
            </span>
          );
        },
      }),
      columnHelper.accessor('timestamp', {
        header: 'Last Updated',
        cell: (info) => (
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <Clock className="w-3.5 h-3.5 mr-1.5 text-gray-400 dark:text-gray-500" />
            <span title={new Date(info.getValue()).toLocaleString()}>
              {formatRelativeTime(info.getValue())}
            </span>
          </div>
        ),
      }),
      columnHelper.display({
        id: 'actions',
        header: 'Actions',
        cell: (info) => (
          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRefresh(info.row.original.application_number);
              }}
              disabled={isRefreshing}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-lg text-white bg-orange-600 hover:bg-orange-700 dark:bg-orange-500 dark:hover:bg-orange-600 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
              title="Re-ingest trademark"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (confirm(`Delete trademark ${info.row.original.application_number}?`)) {
                  onDelete(info.row.original.application_number);
                }
              }}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 transition-colors"
              title="Delete trademark"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ),
      }),
    ],
    [onRefresh, onDelete, isRefreshing]
  );

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  });

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Trademarks Database</h2>
            <span className="ml-3 text-sm text-gray-500 dark:text-gray-400">
              Click any row to view history
            </span>
          </div>
          <div className="flex-1 max-w-md ml-4">
            <input
              type="text"
              value={globalFilter ?? ''}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder="Search all fields..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800"
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <div className="flex items-center">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() && (
                          <ArrowUpDown className="ml-2 w-4 h-4" />
                        )}
                      </div>
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {table.getRowModel().rows.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => handleRowClick(row.original)}
                  className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
            {Math.min(
              (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
              table.getFilteredRowModel().rows.length
            )}{' '}
            of {table.getFilteredRowModel().rows.length} results
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
            </span>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <HistoryModal
        applicationNumber={historyApplicationNumber}
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
      />
    </>
  );
};
