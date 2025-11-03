import React, { useState } from 'react';
import { Download, FileSpreadsheet, FileText } from 'lucide-react';
import { APIClient } from '../services/api';

export const ExportButtons: React.FC = () => {
  const [isExportingCSV, setIsExportingCSV] = useState(false);
  const [isExportingExcel, setIsExportingExcel] = useState(false);

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleExportCSV = async () => {
    try {
      setIsExportingCSV(true);
      const blob = await APIClient.exportToCSV();
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      downloadFile(blob, `trademarks_export_${timestamp}.csv`);
    } catch (error) {
      console.error('Error exporting to CSV:', error);
      alert('Failed to export to CSV. Please try again.');
    } finally {
      setIsExportingCSV(false);
    }
  };

  const handleExportExcel = async () => {
    try {
      setIsExportingExcel(true);
      const blob = await APIClient.exportToExcel();
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      downloadFile(blob, `trademarks_export_${timestamp}.xlsx`);
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      alert('Failed to export to Excel. Please try again.');
    } finally {
      setIsExportingExcel(false);
    }
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={handleExportCSV}
        disabled={isExportingCSV}
        className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors"
      >
        {isExportingCSV ? (
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
        ) : (
          <FileText className="w-4 h-4" />
        )}
        Export CSV
      </button>
      <button
        onClick={handleExportExcel}
        disabled={isExportingExcel}
        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
      >
        {isExportingExcel ? (
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
        ) : (
          <FileSpreadsheet className="w-4 h-4" />
        )}
        Export Excel
      </button>
    </div>
  );
};
