import React, { useMemo, useState } from 'react';
import { Plus, MessageSquare, MoreVertical, Trash2 } from 'lucide-react';

interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messages: Message[];
}

interface SidebarProps {
  chatSessions: ChatSession[];
  currentSessionId: string | null;
  onNewChat: () => void;
  onSelectChat: (sessionId: string) => void;
  onDeleteChat: (sessionId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  chatSessions, 
  currentSessionId, 
  onNewChat, 
  onSelectChat,
  onDeleteChat 
}) => {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const now = useMemo(() => new Date(), []);
  
  const formatTime = useMemo(() => (date: Date) => {
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'आज';
    if (days === 1) return 'काल';
    if (days < 7) return `${days} दिवस आधी`;
    return date.toLocaleDateString('mr-IN');
  }, [now]);

  return (
    <div className="w-64 sm:w-72 md:w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-2 sm:px-3 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors text-sm"
        >
          <Plus size={14} className="sm:w-4 sm:h-4" />
          नवीन चॅट
        </button>
      </div>

      {/* Chat History */}
      <div 
        className="flex-1 overflow-y-auto"
        onClick={() => setOpenMenuId(null)}
      >
        {chatSessions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare size={24} className="mx-auto mb-2 opacity-50" />
            <p className="text-xs sm:text-sm">अजून कोणतीही चॅट नाही</p>
          </div>
        ) : (
          <div className="p-1 sm:p-2">
            {chatSessions.map((session) => (
              <div
                key={session.id}
                className={`relative p-2 sm:p-3 rounded-lg mb-1 sm:mb-2 transition-colors ${
                  currentSessionId === session.id
                    ? 'bg-orange-50 border border-orange-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <button
                  onClick={() => onSelectChat(session.id)}
                  className="w-full text-left pr-8"
                >
                  <div className="font-medium text-xs sm:text-sm text-gray-800 truncate">
                    {session.title}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 truncate">
                    {session.lastMessage}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {formatTime(session.timestamp)}
                  </div>
                </button>
                
                <div className="absolute top-2 right-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenMenuId(openMenuId === session.id ? null : session.id);
                    }}
                    className="p-1 rounded hover:bg-gray-200 transition-colors"
                  >
                    <MoreVertical size={14} className="text-gray-500" />
                  </button>
                  
                  {openMenuId === session.id && (
                    <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-24">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteChat(session.id);
                          setOpenMenuId(null);
                        }}
                        className="w-full px-3 py-2 text-left text-xs text-red-600 hover:bg-red-50 rounded-lg flex items-center gap-2"
                      >
                        <Trash2 size={12} />
                        डिलीट करा
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
export type { ChatSession };