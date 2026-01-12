import React from 'react';

interface HeaderProps {
  onMenuClick: () => void;
  onChatbotClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick, onChatbotClick }) => {
  return (
    <header className="bg-gray-900 text-white shadow-lg z-10">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-xl font-bold">🌍 THE_WORLD</h1>
          <span className="text-sm text-gray-400 hidden md:inline">WebGIS Disaster & AQI Monitor</span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={onChatbotClick}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span className="hidden sm:inline">Chatbot</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
