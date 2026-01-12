import React, { useState } from 'react';
import { downloadAPI } from '../../services/api';
import { useFilters } from '../../context/FilterContext';

type FormatType = 'csv' | 'json' | 'geojson';
type DataType = 'disasters' | 'aqi';

const DownloadPanel: React.FC = () => {
  const [format, setFormat] = useState<FormatType>('csv');
  const [dataType, setDataType] = useState<DataType>('disasters');
  const [downloading, setDownloading] = useState(false);
  const { filters } = useFilters();

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const params: any = { format };
      
      // Add filter parameters based on data type
      if (dataType === 'disasters') {
        if (filters.disasterType.length > 0) {
          params.disaster_type = filters.disasterType[0];
        }
        if (filters.dateRange.start) {
          params.start_date = filters.dateRange.start;
        }
        if (filters.dateRange.end) {
          params.end_date = filters.dateRange.end;
        }
      } else {
        if (filters.citySearch) {
          params.city_name = filters.citySearch;
        }
        if (filters.aqiRange.min !== null) {
          params.min_aqi = filters.aqiRange.min;
        }
        if (filters.aqiRange.max !== null) {
          params.max_aqi = filters.aqiRange.max;
        }
      }

      const blob = await downloadAPI[dataType](params);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${dataType}_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading data:', error);
      alert('Error downloading data. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <h3 className="text-lg font-semibold">Download Data</h3>

      {/* Data Type Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">Data Type</label>
        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              value="disasters"
              checked={dataType === 'disasters'}
              onChange={(e) => setDataType(e.target.value as DataType)}
              className="text-blue-600"
            />
            <span className="text-sm">Disasters</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              value="aqi"
              checked={dataType === 'aqi'}
              onChange={(e) => setDataType(e.target.value as DataType)}
              className="text-blue-600"
            />
            <span className="text-sm">AQI Measurements</span>
          </label>
        </div>
      </div>

      {/* Format Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">Format</label>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as FormatType)}
          className="w-full px-3 py-2 border rounded-md text-sm"
        >
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
          <option value="geojson">GeoJSON</option>
        </select>
      </div>

      {/* Info */}
      <div className="bg-blue-50 p-3 rounded-md text-sm text-blue-800">
        <p>
          Current filters will be applied to the download.
          {filters.disasterType.length > 0 || filters.citySearch || 
           filters.dateRange.start || filters.dateRange.end ? (
            <span className="font-medium"> Filters are active.</span>
          ) : (
            <span> No filters active - all data will be downloaded.</span>
          )}
        </p>
      </div>

      {/* Download Button */}
      <button
        onClick={handleDownload}
        disabled={downloading}
        className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {downloading ? 'Downloading...' : `Download ${dataType.toUpperCase()} as ${format.toUpperCase()}`}
      </button>
    </div>
  );
};

export default DownloadPanel;
