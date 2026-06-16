import { useState, useCallback } from 'react';

/**
 * useLocalStorage - Hook for persisting data in localStorage
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Failed to read from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Failed to write to localStorage:', error);
    }
  }, [storedValue, key]);

  return [storedValue, setValue];
}

/**
 * useAuth - Hook for authentication state
 */
export function useAuth() {
  const [token, setToken] = useLocalStorage('auth_token', null);
  const [username, setUsername] = useLocalStorage('username', null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const logout = useCallback(() => {
    setToken(null);
    setUsername(null);
    setError(null);
  }, [setToken, setUsername]);

  return { token, username, setToken, setUsername, isLoading, setIsLoading, error, setError, logout };
}

/**
 * useStream - Hook for handling streaming responses
 */
export function useStream() {
  const [chunks, setChunks] = useState([]);
  const [events, setEvents] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);

  const stream = useCallback(async (symptom, chatId, streamCallback) => {
    setIsStreaming(true);
    setChunks([]);
    setEvents([]);
    setError(null);

    try {
      const { APIService } = await import("../services/api.js");

      await APIService.analyzeWithStream(symptom, chatId, (event) => {
        if (event.type === 'chunk') {
          const content = event.data?.content || '';
          setChunks(prev => [...prev, content]);
          if (streamCallback) streamCallback(event);
        } else if (event.type === 'error') {
          setError(event.data?.message || 'An error occurred');
        } else if (event.type === 'done') {
          setIsStreaming(false);
        } else {
          // Capture other event types (extraction, severity, routing, etc.)
          setEvents(prev => [...prev, event]);
          if (streamCallback) streamCallback(event);
        }
      });
    } catch (err) {
      setError(err.message);
      setIsStreaming(false);
    }
  }, []);

  const getFullResponse = useCallback(() => {
    return chunks.join('');
  }, [chunks]);

  return { chunks, events, isStreaming, error, stream, getFullResponse };
}

/**
 * useChat - Hook for managing chat state
 */
export function useChat() {
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const addMessage = useCallback((role, content, metadata = {}) => {
    setMessages(prev => [...prev, { role, content, timestamp: new Date(), metadata }]);
  }, []);

  const addStreamingMessage = useCallback((role) => {
    // Add a message that will be filled in by streaming
    setMessages(prev => [...prev, { role, content: null, timestamp: new Date(), isStreaming: true }]);
    return messages.length;
  }, [messages.length]);

  const updateStreamingMessage = useCallback((index, content) => {
    setMessages(prev => {
      const updated = [...prev];
      if (updated[index]) {
        updated[index].content = (updated[index].content || '') + content;
      }
      return updated;
    });
  }, []);

  const completeStreamingMessage = useCallback((index) => {
    setMessages(prev => {
      const updated = [...prev];
      if (updated[index]) {
        updated[index].isStreaming = false;
      }
      return updated;
    });
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    chats,
    setChats,
    currentChatId,
    setCurrentChatId,
    messages,
    setMessages,
    addMessage,
    addStreamingMessage,
    updateStreamingMessage,
    completeStreamingMessage,
    clearMessages,
    isLoading,
    setIsLoading,
    error,
    setError
  };
}
