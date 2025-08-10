import React from 'react';

interface Message {
  id: string;
  text: string;
  isOutgoing: boolean;
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

// Utility function for formatting time
const formatTime = (date: Date | string): string => {
  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    return dateObj.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      hour12: true 
    });
  } catch (error) {
    return '--:--';
  }
};

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {

  return (
    <div className={`flex ${message.isOutgoing ? 'justify-end' : 'justify-start'} mb-3 sm:mb-4`}>
      <div className="max-w-[85%] sm:max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl">
        <div
          className={`
            px-3 py-2 sm:px-4 sm:py-3 rounded-xl shadow-sm
            ${message.isOutgoing
              ? 'bg-orange-400 text-white ml-auto'
              : 'bg-gray-100 text-black'
            }
          `}
          style={{ fontFamily: 'Open Sans, sans-serif' }}
        >
          <p className="text-sm sm:text-base leading-relaxed">{message.text}</p>
        </div>
        <div className={`text-xs text-gray-500 mt-1 ${message.isOutgoing ? 'text-right' : 'text-left'}`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
export type { Message };