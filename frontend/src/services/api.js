/**
 * API Service - Handles all backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class APIService {
  static async createChat(token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to create chat:', error);
      throw error;
    }
  }

  static async getChats(token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/list`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch chats:', error);
      throw error;
    }
  }

  static async getChatHistory(chatId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId })
      });
      if (!response.ok) {
        throw new Error('Failed to fetch chat history');
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
      throw error;
    }
  }

  static async deleteChat(chatId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId })
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to delete chat:', error);
      throw error;
    }
  }

  static async renameChat(chatId, title) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/rename`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId, title })
      });
      return await response.json();
    } catch (error) {
      console.error('Failed to rename chat:', error);
      throw error;
    }
  }

  /**
   * Stream analysis with real-time event updates
   * Yields different event types as they arrive
   */
  static async analyzeWithStream(symptom, chatId, onEvent) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptom, chat_id: chatId })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        // Keep the last incomplete line in buffer
        buffer = lines[lines.length - 1];

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i];
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === "chunk") {
                console.log("RAW CHUNK:", JSON.stringify(data.data?.content));}

              onEvent(data);
            } catch (e) {
              console.error('Failed to parse event:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error);
      onEvent({ type: 'error', data: { message: error.message } });
    }
  }

  static async uploadPDF(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/api/upload-pdf`, {
        method: 'POST',
        body: formData
      });

      return await response.json();
    } catch (error) {
      console.error('Failed to upload PDF:', error);
      throw error;
    }
  }

  static async signup(username, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      return await response.json();
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  }

  static async login(username, password) {

  console.log("LOGIN REQUEST:", {
    username,
    password
  });

  const response = await fetch(
    `${API_BASE_URL}/api/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username,
        password
      })
    }
  );

  const data = await response.json();

  console.log("LOGIN RESPONSE:", data);

  if (!response.ok) {
    throw new Error(
      data.detail || "Login failed"
    );
  }

  return data;
}
}
