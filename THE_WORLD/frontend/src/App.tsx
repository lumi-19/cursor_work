import React, { useState } from 'react';
import MapContainer from './components/Map/MapContainer';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import Chatbot from './components/Chatbot/Chatbot';
import { FilterProvider } from './context/FilterContext';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatbotOpen, setChatbotOpen] = useState(false);

  return (
    <FilterProvider>
      <div className="flex flex-col h-screen bg-gray-100">
        <Header 
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          onChatbotClick={() => setChatbotOpen(!chatbotOpen)}
        />
        
        <div className="flex flex-1 overflow-hidden">
          <Sidebar 
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />
          
          <div className="flex-1 relative">
            <MapContainer />
          </div>
        </div>

        <Chatbot 
          isOpen={chatbotOpen}
          onClose={() => setChatbotOpen(false)}
        />
      </div>
    </FilterProvider>
  );
}

export default App;
