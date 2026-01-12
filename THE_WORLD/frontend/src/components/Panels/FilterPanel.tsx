import React, { useState } from 'react';
import { useFilters } from '../../context/FilterContext';

const disasterTypes = [
  'earthquake',
  'flood',
  'wildfire',
  'hurricane',
  'cyclone',
  'tornado',
  'storm',
  'tsunami',
  'volcanic_eruption',
];

const FilterPanel: React.FC = () => {
  const { filters, setFilters, resetFilters } = useFilters();
  const [localDateStart, setLocalDateStart] = useState(filters.dateRange.start || '');
  const [localDateEnd, setLocalDateEnd] = useState(filters.dateRange.end || '');

  const handleDisasterTypeToggle = (type: string) => {
    const current = filters.disasterType;
    const updated = current.includes(type)
      ? current.filter((t) => t !== type)
      : [...current, type];
    setFilters({ disasterType: updated });
  };

  const handleDateChange = (field: 'start' | 'end', value: string) => {
    if (field === 'start') {
      setLocalDateStart(value);
      setFilters({ dateRange: { ...filters.dateRange, start: value || null } });
    } else {
      setLocalDateEnd(value);
      setFilters({ dateRange: { ...filters.dateRange, end: value || null } });
    }
  };

  const handleAQIRangeChange = (field: 'min' | 'max', value: string) => {
    const numValue = value === '' ? null : parseInt(value);
    setFilters({
      aqiRange: {
        ...filters.aqiRange,
        [field]: numValue,
      },
    });
  };

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Filters</h3>
        <button
          onClick={resetFilters}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Reset
        </button>
      </div>

      {/* Disaster Types */}
      <div>
        <label className="block text-sm font-medium mb-2">Disaster Types</label>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {disasterTypes.map((type) => (
            <label key={type} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.disasterType.includes(type)}
                onChange={() => handleDisasterTypeToggle(type)}
                className="rounded"
              />
              <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Date Range */}
      <div>
        <label className="block text-sm font-medium mb-2">Date Range</label>
        <div className="space-y-2">
          <div>
            <label className="text-xs text-gray-600">Start Date</label>
            <input
              type="date"
              value={localDateStart}
              onChange={(e) => handleDateChange('start', e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">End Date</label>
            <input
              type="date"
              value={localDateEnd}
              onChange={(e) => handleDateChange('end', e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
            />
          </div>
        </div>
      </div>

      {/* AQI Range */}
      <div>
        <label className="block text-sm font-medium mb-2">AQI Range</label>
        <div className="space-y-2">
          <div>
            <label className="text-xs text-gray-600">Min AQI</label>
            <input
              type="number"
              min="0"
              max="500"
              value={filters.aqiRange.min || ''}
              onChange={(e) => handleAQIRangeChange('min', e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
              placeholder="0"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">Max AQI</label>
            <input
              type="number"
              min="0"
              max="500"
              value={filters.aqiRange.max || ''}
              onChange={(e) => handleAQIRangeChange('max', e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
              placeholder="500"
            />
          </div>
        </div>
      </div>

      {/* City Search */}
      <div>
        <label className="block text-sm font-medium mb-2">City Search</label>
        <input
          type="text"
          value={filters.citySearch}
          onChange={(e) => setFilters({ citySearch: e.target.value })}
          className="w-full px-3 py-2 border rounded-md text-sm"
          placeholder="Search cities..."
        />
      </div>
    </div>
  );
};

export default FilterPanel;
