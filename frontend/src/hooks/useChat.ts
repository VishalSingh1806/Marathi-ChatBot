import { useState, useCallback, useEffect } from 'react';
import { Message } from '../components/MessageBubble';
import { ChatSession } from '../components/Sidebar';
import { SecureApiClient } from '../utils/apiClient';

const API_BASE_URL = 'http://localhost:8000';

const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(() => localStorage.getItem('currentSessionId'));
  const [csrfToken, setCsrfToken] = useState<string | null>(null);

  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);

  // Load chat sessions from localStorage on mount
  useEffect(() => {
    try {
      const savedSessions = localStorage.getItem('chatSessions');
      if (savedSessions) {
        const parsedSessions = JSON.parse(savedSessions).map((session: any) => ({
          ...session,
          timestamp: new Date(session.timestamp),
          messages: Array.isArray(session.messages) ? session.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          })) : []
        }));
        setChatSessions(parsedSessions);
      }
    } catch (error) {
      console.error('Error loading chat sessions:', error);
      // Clear corrupted data
      localStorage.removeItem('chatSessions');
      setChatSessions([]);
    }
  }, []);

  // Save chat sessions to localStorage
  const saveChatSessions = useCallback((sessions: ChatSession[]) => {
    localStorage.setItem('chatSessions', JSON.stringify(sessions));
    setChatSessions(sessions);
  }, []);

  const generateId = useCallback(() => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  const addMessage = useCallback((text: string, isOutgoing: boolean) => {
    const newMessage: Message = {
      id: generateId(),
      text,
      isOutgoing,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  }, [generateId]);

  const sendMessage = useCallback(async (text: string) => {
    // Add user message
    addMessage(text, true);
    
    // Show typing indicator
    setIsTyping(true);
    
    try {
      // Use existing session or create new one
      let currentSessionId = sessionId;
      
      // For new sessions, get CSRF token
      if (!currentSessionId) {
        const csrfData = await SecureApiClient.getCsrfToken();
        currentSessionId = csrfData.session_id;
        setSessionId(currentSessionId);
        localStorage.setItem('currentSessionId', currentSessionId);
      }
      
      const data = await SecureApiClient.secureQuery(text, currentSessionId, null);
      
      // Add bot response
      const botMessageId = addMessage(data.answer, false);
      
      const finalSessionId = currentSessionId;
      
      // Get current session messages
      const currentSession = finalSessionId ? chatSessions.find(s => s.id === finalSessionId) : null;
      const existingMessages = currentSession?.messages || [];
      const userMessage = { id: generateId(), text: text, isOutgoing: true, timestamp: new Date() };
      const botMessage = { id: botMessageId, text: data.answer, isOutgoing: false, timestamp: new Date() };
      const allMessages = [...existingMessages, userMessage, botMessage];
      
      if (finalSessionId) {
        const existingSessionIndex = chatSessions.findIndex(s => s.id === finalSessionId);
        
        if (existingSessionIndex >= 0) {
          // Update existing session
          const updatedSessions = [...chatSessions];
          updatedSessions[existingSessionIndex] = {
            ...updatedSessions[existingSessionIndex],
            lastMessage: data.answer.length > 50 ? data.answer.substring(0, 50) + '...' : data.answer,
            timestamp: new Date(),
            messages: allMessages
          };
          saveChatSessions(updatedSessions);
        } else {
          // Create new session
          const newSession: ChatSession = {
            id: finalSessionId,
            title: text.length > 30 ? text.substring(0, 30) + '...' : text,
            lastMessage: data.answer.length > 50 ? data.answer.substring(0, 50) + '...' : data.answer,
            timestamp: new Date(),
            messages: allMessages
          };
          const updatedSessions = [newSession, ...chatSessions].slice(0, 10);
          saveChatSessions(updatedSessions);
        }
      }
      
      setIsTyping(false);
    } catch (error) {
      console.error('Error calling API:', error);
      setIsTyping(false);
      
      let errorMessage = 'माफ करा, सर्वरशी कनेक्शन करताना समस्या आली. कृपया पुन्हा प्रयत्न करा.';
      
      if (error instanceof TypeError) {
        errorMessage = 'इंटरनेट कनेक्शन तपासा आणि पुन्हा प्रयत्न करा.';
      } else if (error instanceof Error && error.message.includes('400')) {
        errorMessage = 'अयोग्य इनपुट. कृपया पुन्हा प्रयत्न करा.';
      } else if (error instanceof Error && error.message.includes('500')) {
        errorMessage = 'सर्वर समस्या. काही वेळानंतर पुन्हा प्रयत्न करा.';
      }
      
      addMessage(errorMessage, false);
    }
  }, [addMessage, sessionId, csrfToken, chatSessions, saveChatSessions, generateId]);

  const createNewChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setCsrfToken(null);
    localStorage.removeItem('currentSessionId');
  }, []);

  const selectChat = useCallback((chatSessionId: string) => {
    try {
      const selectedSession = chatSessions.find(session => session.id === chatSessionId);
      if (selectedSession) {
        // Ensure messages is an array
        const messages = Array.isArray(selectedSession.messages) ? selectedSession.messages : [];
        setMessages(messages);
        setSessionId(chatSessionId);
        localStorage.setItem('currentSessionId', chatSessionId);
        setCsrfToken(null); // Clear CSRF token for existing session
      } else {
        // If session not found, start fresh
        setMessages([]);
        setSessionId(chatSessionId);
        localStorage.setItem('currentSessionId', chatSessionId);
        setCsrfToken(null);
      }
    } catch (error) {
      console.error('Error selecting chat:', error);
      // Fallback to empty state
      setMessages([]);
      setSessionId(null);
      localStorage.removeItem('currentSessionId');
      setCsrfToken(null);
    }
  }, [chatSessions]);

  const deleteChat = useCallback((chatSessionId: string) => {
    const updatedSessions = chatSessions.filter(session => session.id !== chatSessionId);
    saveChatSessions(updatedSessions);
    
    // If deleting current chat, start new chat
    if (sessionId === chatSessionId) {
      setMessages([]);
      setSessionId(null);
    }
  }, [chatSessions, sessionId, saveChatSessions]);

  return {
    messages,
    isTyping,
    sendMessage,
    chatSessions,
    currentSessionId: sessionId,
    createNewChat,
    selectChat,
    deleteChat,
  };
};

export { useChat };