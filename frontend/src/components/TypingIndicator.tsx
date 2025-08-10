import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start mb-3 sm:mb-4">
      <div className="max-w-xs">
        <div className="bg-gray-100 px-3 py-2 sm:px-4 sm:py-3 rounded-xl">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          <span className="hidden sm:inline">चॅटबॉट उत्तर तयार करत आहे...</span>
          <span className="sm:hidden">उत्तर तयार करत आहे...</span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;