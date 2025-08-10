import React, { useState, useRef, useCallback } from 'react';
import { Send, Mic, Loader } from 'lucide-react';
import { SecureApiClient } from '../utils/apiClient';

interface InputBarProps {
  onSendMessage: (message: string) => void;
}

const InputBar: React.FC<InputBarProps> = ({ onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const handleSend = useCallback(() => {
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  }, [inputValue, onSendMessage]);

  const handleMicClick = useCallback(async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm;codecs=opus' });
        transcribeAudio(audioBlob);
        // Stop all media tracks to turn off the mic indicator
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("मायक्रोफोन वापरण्यासाठी परवानगी आवश्यक आहे.");
    }
  }, [isRecording]);

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsTranscribing(true);
    
    try {
      // Get CSRF token first
      const csrfData = await SecureApiClient.getCsrfToken();
      
      // Use secure transcription
      const data = await SecureApiClient.secureTranscribe(audioBlob, csrfData.session_id, csrfData.csrf_token);
      setInputValue(data.transcript);
    } catch (error) {
      console.error("Transcription error:", error);
      alert("व्हॉइस ओळखण्यात समस्या आली. कृपया पुन्हा प्रयत्न करा.");
    } finally {
      setIsTranscribing(false);
    }
  };

  return (
    <div className="px-2 sm:px-4 py-4 sm:py-6 bg-gray-50">
      <div className="max-w-3xl mx-auto">
        <div className="relative">
          <div className="flex items-center bg-white rounded-full shadow-lg border border-gray-200 px-3 sm:px-4 py-2 sm:py-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="स्टार्टअप संबंधी प्रश्न विचारा..."
              className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-500 text-sm sm:text-base"
              disabled={isRecording || isTranscribing}
            />
            
            <button
              onClick={handleMicClick}
              disabled={isTranscribing}
              className={`ml-2 p-2 rounded-full transition-all duration-200 ${
                isRecording 
                  ? 'bg-red-100 text-red-600 animate-pulse'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
              title={isRecording ? 'रेकॉर्डिंग बंद करा' : 'व्हॉइस इनपुट'}
            >
              <Mic size={18} />
            </button>
            
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isRecording || isTranscribing}
              className={`ml-2 p-2 rounded-full transition-all duration-200 ${
                inputValue.trim() && !isRecording && !isTranscribing
                  ? 'bg-orange-500 hover:bg-orange-600 text-white'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }
              `}
              title="Send message"
            >
              {isTranscribing ? <Loader size={18} className="animate-spin" /> : <Send size={18} />}
            </button>
          </div>

          <div className="text-xs text-gray-500 text-center mt-2">
            {isTranscribing ? 'तुमचा आवाज ओळखत आहे...' : 'मराठी स्टार्टअप चॅटबॉट चूका करू शकतो. महत्वाची माहिती तपासून पहा.'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputBar;
