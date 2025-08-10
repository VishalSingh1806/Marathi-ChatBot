import React, { useEffect, useRef, useCallback } from 'react';
import MessageBubble, { Message } from './MessageBubble';

interface MessageAreaProps {
  messages: Message[];
}

const MessageArea: React.FC<MessageAreaProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🚀</span>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-3" style={{ fontFamily: 'Montserrat, sans-serif' }}>
                मराठी स्टार्टअप चॅटबॉटमध्ये आपले स्वागत आहे
              </h2>
              <p className="text-gray-600 text-lg max-w-md mx-auto" style={{ fontFamily: 'Open Sans, sans-serif' }}>
                महाराष्ट्रात तुमचा व्यवसाय सुरू करण्यासाठी आणि वाढवण्यासाठी तज्ञ मार्गदर्शन मिळवा
              </p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageArea;