import React, { useState } from 'react';
import MessageArea from './components/MessageArea';
import InputBar from './components/InputBar';
import TypingIndicator from './components/TypingIndicator';
import Sidebar from './components/Sidebar';
import { useChat } from './hooks/useChat';
import { Menu, X } from 'lucide-react';

function App() {
  const { 
    messages, 
    isTyping, 
    sendMessage, 
    chatSessions, 
    currentSessionId, 
    createNewChat, 
    selectChat,
    deleteChat 
  } = useChat();
  
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-gray-50">
      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-20 px-4 py-3 flex items-center justify-between">
        <h1 className="font-semibold text-gray-800">मराठी स्टार्टअप चॅटबॉट</h1>
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-lg hover:bg-gray-100"
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0 fixed md:relative z-10 transition-transform duration-300
      `}>
        <Sidebar 
          chatSessions={chatSessions}
          currentSessionId={currentSessionId}
          onNewChat={() => {
            createNewChat();
            setSidebarOpen(false);
          }}
          onSelectChat={(id) => {
            selectChat(id);
            setSidebarOpen(false);
          }}
          onDeleteChat={deleteChat}
        />
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-5"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col pt-16 md:pt-0">
        <MessageArea messages={messages} />
        {isTyping && (
          <div className="px-2 md:px-4">
            <div className="max-w-4xl mx-auto">
              <TypingIndicator />
            </div>
          </div>
        )}
        <InputBar onSendMessage={sendMessage} />
      </div>
    </div>
  );
}

export default App;