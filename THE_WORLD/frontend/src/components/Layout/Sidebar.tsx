import React, { useState } from 'react';
import FilterPanel from '../Panels/FilterPanel';
import ComparisonPanel from '../Panels/ComparisonPanel';
import DownloadPanel from '../Panels/DownloadPanel';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'filters' | 'comparison' | 'download';

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('filters');

  if (!isOpen) {
    return (
      <div className="w-12 bg-gray-800 text-white">
        <button
          onClick={() => {/* Open sidebar */}}
          className="w-full p-3 hover:bg-gray-700"
        >
          <svg className="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className="w-80 bg-white shadow-xl flex flex-col h-full">
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold">Controls</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-200 rounded"
          aria-label="Close sidebar"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('filters')}
          className={`flex-1 px-4 py-2 text-sm font-medium ${
            activeTab === 'filters'
              ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          Filters
        </button>
        <button
          onClick={() => setActiveTab('comparison')}
          className={`flex-1 px-4 py-2 text-sm font-medium ${
            activeTab === 'comparison'
              ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          Compare
        </button>
        <button
          onClick={() => setActiveTab('download')}
          className={`flex-1 px-4 py-2 text-sm font-medium ${
            activeTab === 'download'
              ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          Download
        </button>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'filters' && <FilterPanel />}
        {activeTab === 'comparison' && <ComparisonPanel />}
        {activeTab === 'download' && <DownloadPanel />}
      </div>
    </div>
  );
};

export default Sidebar;
