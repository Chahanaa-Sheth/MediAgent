import { useState, useEffect, useRef } from "react";
import { Send, Paperclip, Bot, User, Loader2, Plus, Trash2, Edit2, AlertCircle } from "lucide-react";
import { APIService } from "./services/api";
import { useAuth, useChat, useStream } from "./hooks";

function App() {
  const auth = useAuth();
  const chat = useChat();
  const stream = useStream();

  const [message, setMessage] = useState("");
  const [isInitialized, setIsInitialized] = useState(false);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat.messages]);

  // Initialize app
  useEffect(() => {
    const initApp = async () => {
      try {
        if (auth.token) {
          const chatsData = await APIService.getChats(auth.token);
          chat.setChats(chatsData.chats || []);
        }
        setIsInitialized(true);
      } catch (error) {
        console.error("Failed to initialize:", error);
        chat.setError("Failed to load chats");
        setIsInitialized(true);
      }
    };
    initApp();
  }, [auth.token]);

  const createNewChat = async () => {
    try {
      chat.setError(null);
      const result = await APIService.createChat(auth.token);
      chat.setCurrentChatId(result.chat_id);
      chat.clearMessages();

      const updatedChats = await APIService.getChats(auth.token);
      chat.setChats(updatedChats.chats || []);
    } catch (error) {
      chat.setError("Failed to create chat");
      console.error(error);
    }
  };

  const loadChat = async (selectedChat) => {
    try {
      chat.setError(null);
      // Fetch fresh chat history from server
      const chatData = await APIService.getChatHistory(selectedChat.chat_id);
      chat.setCurrentChatId(selectedChat.chat_id);
      chat.setMessages(chatData.messages || []);
    } catch (error) {
      chat.setError("Failed to load chat");
      console.error(error);
    }
  };

  const sendMessage = async () => {
    if (!message.trim()) return;
    if (!chat.currentChatId) await createNewChat();

    const userMessage = message;
    setMessage("");
    chat.setError(null);

    // Add user message immediately
    chat.addMessage("user", userMessage);

    // Add streaming assistant message placeholder
    const messageIndex = chat.addStreamingMessage("assistant");

    try {
      let fullResponse = "";
      let streamedChunks = 0;

      await stream.stream(userMessage, chat.currentChatId, (event) => {
        if (event.type === "chunk") {
          const content = event.data?.content || "";
          fullResponse += content;
          chat.updateStreamingMessage(messageIndex, content);
          streamedChunks++;
        } else if (event.type === "error") {
          chat.setError(event.data?.message || "Analysis failed");
          chat.completeStreamingMessage(messageIndex);
        } else if (event.type === "done") {
          chat.completeStreamingMessage(messageIndex);
        }
      });

      // Reload chat history
      const updatedChats = await APIService.getChats(auth.token);
      chat.setChats(updatedChats.chats || []);
    } catch (error) {
      chat.setError(error.message || "Failed to analyze symptom");
      chat.completeStreamingMessage(messageIndex);
      console.error(error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      chat.setIsLoading(true);
      chat.setError(null);
      await APIService.uploadPDF(file);
      event.target.value = "";
      chat.setError(null);
    } catch (error) {
      chat.setError("Failed to upload PDF");
      console.error(error);
    } finally {
      chat.setIsLoading(false);
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      chat.setError(null);
      await APIService.deleteChat(chatId);
      if (chat.currentChatId === chatId) {
        chat.setCurrentChatId(null);
        chat.clearMessages();
      }
      const updatedChats = await APIService.getChats(auth.token);
      chat.setChats(updatedChats.chats || []);
    } catch (error) {
      chat.setError("Failed to delete chat");
      console.error(error);
    }
  };

  if (!isInitialized) {
    return <div className="flex items-center justify-center h-screen bg-black text-white">Loading...</div>;
  }

  return (
    <div className="h-screen bg-black text-white flex overflow-hidden">
      {/* SIDEBAR */}
      <div className="w-80 bg-zinc-950 border-r border-zinc-800 flex flex-col">
        {/* TOP */}
        <div className="p-5 border-b border-zinc-800">
          <h1 className="text-4xl font-bold">MediAgent</h1>
          <p className="text-zinc-500 text-sm mt-2">AI Medical Research Assistant</p>

          <button
            onClick={createNewChat}
            className="mt-5 w-full bg-blue-600 hover:bg-blue-700 transition-all rounded-xl py-3 flex items-center justify-center gap-2"
          >
            <Plus size={18} />
            New Chat
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={chat.isLoading}
            className="mt-3 w-full bg-zinc-800 hover:bg-zinc-700 transition-all rounded-xl py-3 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Paperclip size={18} />
            {chat.isLoading ? "Uploading..." : "Upload PDF"}
          </button>

          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
        </div>

        {/* ERROR MESSAGE */}
        {chat.error && (
          <div className="mx-4 mt-3 p-3 bg-red-900/50 border border-red-700 rounded-lg flex gap-2">
            <AlertCircle size={16} className="shrink-0 mt-0.5" />
            <p className="text-sm text-red-200">{chat.error}</p>
          </div>
        )}

        {/* CHAT HISTORY */}
        <div className="flex-1 overflow-y-auto p-4">
          <p className="text-zinc-500 text-sm mb-3">Recent Chats</p>
          <div className="space-y-2">
            {chat.chats.slice().reverse().map((item) => (
              <div key={item.chat_id} className="group">
                <div
                  onClick={() => loadChat(item)}
                  className={`cursor-pointer transition-all rounded-lg p-3 border ${
                    chat.currentChatId === item.chat_id
                      ? "bg-zinc-800 border-blue-600"
                      : "bg-zinc-900 border-transparent hover:bg-zinc-800 hover:border-zinc-700"
                  }`}
                >
                  <p className="text-sm truncate font-medium">{item.title}</p>
                  <p className="text-xs text-zinc-500 mt-1">{item.messages?.length || 0} messages</p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChat(item.chat_id);
                  }}
                  className="hidden group-hover:block ml-2 mt-1 text-zinc-500 hover:text-red-500 transition-colors"
                  title="Delete chat"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* MAIN CHAT AREA */}
      <div className="flex-1 flex flex-col">
        {/* HEADER */}
        <div className="border-b border-zinc-800 px-8 py-5 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">MediAgent</h1>
            <p className="text-zinc-500 text-sm">Medical Analysis Assistant</p>
          </div>
          {auth.username && <div className="text-zinc-400 text-sm">👤 {auth.username}</div>}
        </div>

        {/* MESSAGES */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-6 py-10 space-y-6">
            {chat.messages.length === 0 && (
              <div className="h-[60vh] flex items-center justify-center">
                <div className="text-center max-w-2xl">
                  <h2 className="text-5xl font-bold mb-6">Welcome to MediAgent</h2>
                  <p className="text-zinc-400 text-lg leading-relaxed">
                    Your AI-powered medical copilot with PubMed research, PDF analysis, drug interaction intelligence, and intelligent symptom reasoning.
                  </p>
                  <p className="text-zinc-500 text-sm mt-6">Start a conversation by asking about your symptoms.</p>
                </div>
              </div>
            )}

            {chat.messages.map((item, index) => (
              <div key={index} className="space-y-4">
                {item.role === "user" && (
                  <div className="flex justify-end">
                    <div className="flex items-end gap-3 max-w-[75%]">
                      <div className="bg-blue-600 px-6 py-4 rounded-2xl text-base">{item.content}</div>
                      <div className="bg-zinc-800 p-3 rounded-full shrink-0">
                        <User size={18} />
                      </div>
                    </div>
                  </div>
                )}

                {item.role === "assistant" && (
                  <div className="flex justify-start">
                    <div className="flex gap-4 max-w-[85%]">
                      <div className="bg-zinc-800 p-3 rounded-full h-fit shrink-0">
                        <Bot size={18} />
                      </div>
                      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl px-6 py-4 whitespace-pre-wrap leading-relaxed text-sm">
                        {item.content ? (
                          <div>{item.content}</div>
                        ) : (
                          <div className="flex items-center gap-2 text-zinc-400">
                            <Loader2 size={16} className="animate-spin" />
                            Analyzing...
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* INPUT */}
        <div className="border-t border-zinc-800 px-6 py-5 bg-black">
          <div className="max-w-4xl mx-auto">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl px-5 py-3 flex items-center gap-4">
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={chat.isLoading}
                className="text-zinc-400 hover:text-white disabled:opacity-50 transition-colors"
              >
                <Paperclip size={20} />
              </button>

              <input
                type="text"
                placeholder="Describe your symptoms..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                disabled={stream.isStreaming}
                className="flex-1 bg-transparent outline-none text-base placeholder-zinc-500 disabled:opacity-50"
              />

              <button
                onClick={sendMessage}
                disabled={stream.isStreaming || !message.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-700 transition-all p-3 rounded-xl"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
