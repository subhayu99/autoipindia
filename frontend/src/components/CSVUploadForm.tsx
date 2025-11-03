import React, { useState, useCallback, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  ColumnDef,
} from '@tanstack/react-table';
import { Upload, FileUp, AlertCircle, CheckCircle, X, Trash2 } from 'lucide-react';
import { CSVRow } from '../types';
import { APIClient } from '../services/api';

const CSVUploadForm: React.FC = () => {
  const [csvData, setCsvData] = useState<CSVRow[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{
    success: boolean;
    message: string;
    jobId?: string;
  } | null>(null);

  // Parse CSV file
  const parseCSV = useCallback((text: string): CSVRow[] => {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length === 0) return [];

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const rows: CSVRow[] = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const row: CSVRow = {
        id: `row-${i}`,
      };

      headers.forEach((header, index) => {
        const value = values[index]?.trim();
        if (value) {
          if (header === 'application_number') {
            row.application_number = value;
          } else if (header === 'wordmark') {
            row.wordmark = value;
          } else if (header === 'class_name' || header === 'class') {
            row.class_name = value;
          }
        }
      });

      // Validate row
      const hasAppNumber = !!row.application_number;
      const hasWordmarkAndClass = !!row.wordmark && !!row.class_name;

      row.isValid = hasAppNumber || hasWordmarkAndClass;
      if (!row.isValid) {
        row.error = 'Either application_number OR (wordmark + class_name) required';
      }

      rows.push(row);
    }

    return rows;
  }, []);

  // Handle file upload
  const handleFileUpload = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const parsedData = parseCSV(text);
      setCsvData(parsedData);
      setUploadResult(null);
    };
    reader.readAsText(file);
  }, [parseCSV]);

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
      handleFileUpload(file);
    }
  }, [handleFileUpload]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  }, [handleFileUpload]);

  // Update cell value
  const updateCell = useCallback((rowId: string, columnId: string, value: string) => {
    setCsvData(prev => prev.map(row => {
      if (row.id === rowId) {
        const updated = { ...row, [columnId]: value };

        // Re-validate
        const hasAppNumber = !!updated.application_number;
        const hasWordmarkAndClass = !!updated.wordmark && !!updated.class_name;
        updated.isValid = hasAppNumber || hasWordmarkAndClass;
        updated.error = updated.isValid ? undefined : 'Either application_number OR (wordmark + class_name) required';

        return updated;
      }
      return row;
    }));
  }, []);

  // Delete row
  const deleteRow = useCallback((rowId: string) => {
    setCsvData(prev => prev.filter(row => row.id !== rowId));
  }, []);

  // Add new row
  const addRow = useCallback(() => {
    const newRow: CSVRow = {
      id: `row-${Date.now()}`,
      isValid: false,
      error: 'Either application_number OR (wordmark + class_name) required',
    };
    setCsvData(prev => [...prev, newRow]);
  }, []);

  // Submit to API
  const handleSubmit = useCallback(async () => {
    const validRows = csvData.filter(row => row.isValid);

    if (validRows.length === 0) {
      setUploadResult({
        success: false,
        message: 'No valid rows to submit',
      });
      return;
    }

    // Convert to CSV format
    const headers = ['application_number', 'wordmark', 'class_name'];
    const csvContent = [
      headers.join(','),
      ...validRows.map(row =>
        headers.map(h => row[h as keyof CSVRow] || '').join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const file = new File([blob], 'trademarks.csv', { type: 'text/csv' });

    try {
      setIsUploading(true);
      const response = await APIClient.uploadCSV(file);
      setUploadResult({
        success: true,
        message: response.message,
        jobId: response.job_id,
      });
      // Clear data after successful upload
      setTimeout(() => {
        setCsvData([]);
      }, 2000);
    } catch (error: any) {
      setUploadResult({
        success: false,
        message: error.response?.data?.detail || 'Failed to upload CSV',
      });
    } finally {
      setIsUploading(false);
    }
  }, [csvData]);

  // Define columns with editable cells
  const columns = useMemo<ColumnDef<CSVRow, any>[]>(
    () => [
      {
        id: 'status',
        header: 'Status',
        cell: ({ row }) => (
          <div className="flex items-center justify-center">
            {row.original.isValid ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500" />
            )}
          </div>
        ),
        size: 60,
      },
      {
        accessorKey: 'application_number',
        header: 'Application Number',
        cell: ({ row, getValue }) => (
          <input
            type="text"
            value={(getValue() as string) || ''}
            onChange={(e) => updateCell(row.original.id, 'application_number', e.target.value)}
            className="w-full px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="e.g., 1234567"
          />
        ),
      },
      {
        accessorKey: 'wordmark',
        header: 'Wordmark',
        cell: ({ row, getValue }) => (
          <input
            type="text"
            value={(getValue() as string) || ''}
            onChange={(e) => updateCell(row.original.id, 'wordmark', e.target.value)}
            className="w-full px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="e.g., NIKE"
          />
        ),
      },
      {
        accessorKey: 'class_name',
        header: 'Class',
        cell: ({ row, getValue }) => (
          <input
            type="text"
            value={(getValue() as string | number) || ''}
            onChange={(e) => updateCell(row.original.id, 'class_name', e.target.value)}
            className="w-full px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="e.g., 25"
          />
        ),
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => (
          <button
            onClick={() => deleteRow(row.original.id)}
            className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            title="Delete row"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        ),
        size: 80,
      },
    ],
    [updateCell, deleteRow]
  );

  const table = useReactTable({
    data: csvData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const validCount = csvData.filter(row => row.isValid).length;
  const invalidCount = csvData.filter(row => !row.isValid).length;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold dark:text-white">Bulk CSV Upload</h2>

      {/* Upload Area */}
      {csvData.length === 0 && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center transition-colors
            ${isDragging
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-300 dark:border-gray-600'
            }
          `}
        >
          <div className="flex flex-col items-center gap-4">
            <FileUp className="h-12 w-12 text-gray-400 dark:text-gray-500" />
            <div>
              <p className="text-lg font-medium dark:text-white">
                Drop CSV file here or click to upload
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Expected format: application_number OR (wordmark, class_name)
              </p>
            </div>
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileInput}
                className="hidden"
              />
              <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                <Upload className="h-4 w-4" />
                Select CSV File
              </span>
            </label>
          </div>
        </div>
      )}

      {/* Data Table */}
      {csvData.length > 0 && (
        <>
          <div className="flex items-center justify-between">
            <div className="flex gap-4 text-sm">
              <span className="text-green-600 dark:text-green-400">
                ✓ Valid: {validCount}
              </span>
              {invalidCount > 0 && (
                <span className="text-red-600 dark:text-red-400">
                  ✗ Invalid: {invalidCount}
                </span>
              )}
            </div>
            <button
              onClick={addRow}
              className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 dark:text-white"
            >
              + Add Row
            </button>
          </div>

          <div className="border dark:border-gray-700 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  {table.getHeaderGroups().map(headerGroup => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map(header => (
                        <th
                          key={header.id}
                          className="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300"
                        >
                          {flexRender(header.column.columnDef.header, header.getContext())}
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y dark:divide-gray-700">
                  {table.getRowModel().rows.map(row => (
                    <tr
                      key={row.id}
                      className={
                        row.original.isValid
                          ? ''
                          : 'bg-red-50 dark:bg-red-900/10'
                      }
                    >
                      {row.getVisibleCells().map(cell => (
                        <td key={cell.id} className="px-4 py-2">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Error messages for invalid rows */}
          {invalidCount > 0 && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-yellow-800 dark:text-yellow-300">
                    {invalidCount} invalid row{invalidCount !== 1 ? 's' : ''}
                  </p>
                  <p className="text-sm text-yellow-700 dark:text-yellow-400 mt-1">
                    Each row must have either an application_number OR both wordmark and class_name
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleSubmit}
              disabled={validCount === 0 || isUploading}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? 'Uploading...' : `Upload ${validCount} Trademark${validCount !== 1 ? 's' : ''}`}
            </button>
            <button
              onClick={() => setCsvData([])}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Clear
            </button>
          </div>

          {/* Upload result */}
          {uploadResult && (
            <div
              className={`
                p-4 rounded-lg flex items-start gap-2
                ${uploadResult.success
                  ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                  : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                }
              `}
            >
              {uploadResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-500 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-500 flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <p className={uploadResult.success ? 'text-green-800 dark:text-green-300' : 'text-red-800 dark:text-red-300'}>
                  {uploadResult.message}
                </p>
                {uploadResult.jobId && (
                  <p className="text-sm text-green-700 dark:text-green-400 mt-1">
                    Job ID: {uploadResult.jobId}
                  </p>
                )}
              </div>
              <button
                onClick={() => setUploadResult(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CSVUploadForm;
