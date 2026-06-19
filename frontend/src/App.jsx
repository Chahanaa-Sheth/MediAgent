import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Paperclip, Bot, User, Loader2, Plus, Trash2, Edit2, AlertCircle } from "lucide-react";
import { APIService } from "./services/api";
import { useAuth, useChat, useStream } from "./hooks";
import AuthPage from "./components/AuthPage";

function App() {
  const auth = useAuth();
  const chat = useChat();

  useEffect(() => {

  const savedChatId =
    localStorage.getItem("current_chat_id");

  if (savedChatId) {
    chat.setCurrentChatId(savedChatId);
  }

}, []);
  const stream = useStream();

  const [message, setMessage] = useState("");
  const [analysisTrace, setAnalysisTrace] = useState([]);
  const [uploadMessage, setUploadMessage] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  

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

  useEffect(() => {

  const loadCurrentChat =
    async () => {

      if (
        !chat.currentChatId
      ) return;

      try {

        const chatData =
          await APIService.getChatHistory(
            chat.currentChatId
          );

        chat.setMessages(
          chatData.messages || []
        );

      } catch (err) {

        console.error(err);

      }

    };

  loadCurrentChat();

}, [chat.currentChatId]);

  if (!auth.token) {
    return <AuthPage auth={auth} />;
  }

  const createNewChat = async () => {
  try {
    chat.setError(null);

    const result = await APIService.createChat(auth.token);

    chat.setCurrentChatId(result.chat_id);
    localStorage.setItem(
  "current_chat_id",
  result.chat_id
);
    chat.clearMessages();
    setAnalysisTrace([]);

    const updatedChats = await APIService.getChats(auth.token);
    chat.setChats(updatedChats.chats || []);

    return result.chat_id;
  } catch (error) {
    chat.setError("Failed to create chat");
    throw error;
  }
};

  const loadChat = async (selectedChat) => {
    try {
      chat.setError(null);
      // Fetch fresh chat history from server
      const chatData = await APIService.getChatHistory(selectedChat.chat_id);
      chat.setCurrentChatId(selectedChat.chat_id);
      localStorage.setItem(
  "current_chat_id",
  selectedChat.chat_id
);
      setAnalysisTrace([]);
      chat.setMessages(chatData.messages || []);
    } catch (error) {
      chat.setError("Failed to load chat");
      console.error(error);
    }
  };

  const sendMessage = async () => {
    if (!message.trim()) return;
    let activeChatId = chat.currentChatId;

if (!activeChatId) {
  activeChatId = await createNewChat();
}

    const userMessage = message;
    setMessage("");
    chat.setError(null);

    // Add user message immediately
    chat.addMessage("user", userMessage);

    // Add streaming assistant message placeholder
    const messageIndex = chat.addStreamingMessage("assistant");

    console.log("MESSAGE INDEX:", messageIndex);
    setAnalysisTrace([]);

    try {
      let fullResponse = "";
      let streamedChunks = 0;

      await stream.stream(userMessage, activeChatId, (event) => {
        if (event.type === "chunk") {

  const content = event.data?.content || "";
  

  console.log("CHUNK:", JSON.stringify(content));

  fullResponse += content;

  chat.updateStreamingMessage(
    messageIndex,
    content
  );
  

  streamedChunks++;
} 
          
          else if (event.type === "error") {

  chat.updateStreamingMessage(
    messageIndex,
    "⚠️ Analysis failed.\n\n" +
    (event.data?.message || "Unknown error")
  );

  chat.completeStreamingMessage(
    messageIndex
  );

} else if (event.type === "done") {
          chat.completeStreamingMessage(messageIndex);
        }
        else if (event.type === "extraction") {
  setAnalysisTrace(prev => [
    ...prev,
    {
      type: "extraction",
      timestamp: new Date(),
      data: event.data
    }
  ]);
}

else if (event.type === "severity") {
  setAnalysisTrace(prev => [
    ...prev,
    {
      type: "severity",
      timestamp: new Date(),
      data: event.data
    }
  ]);
}

else if (event.type === "diagnosis") {
  setAnalysisTrace(prev => [
    ...prev,
    {
      type: "diagnosis",
      timestamp: new Date(),
      data: event.data
    }
  ]);
}

else if (event.type === "followup") {

  setAnalysisTrace(prev => [
    ...prev,
    {
      type: "followup",
      timestamp: new Date(),
      data: event.data
    }
  ]);
}

else if (event.type === "routing") {
  setAnalysisTrace(prev => [
    ...prev,
    {
      type: "routing",
      timestamp: new Date(),
      data: event.data
    }
  ]);
}

else if (event.type === "rag") {
  setAnalysisTrace(prev => [
    ...prev,
    {
      type: "rag",
      timestamp: new Date(),
      data: event.data
    }
  ]);
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

    setUploadMessage({
      success: true,
      filename: file.name
    });

    setTimeout(() => {
      setUploadMessage(null);
    }, 4000);

    event.target.value = "";

  } catch (error) {

    setUploadMessage({
      success: false,
      filename: file.name
    });

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
        {/* HEADER */}
<div className="border-b border-zinc-800 px-8 py-5 flex justify-between items-center">

  <div>
    <h1 className="text-3xl font-bold">
      MediAgent
    </h1>

    <p className="text-zinc-500 text-sm">
      Medical Analysis Assistant
    </p>
  </div>

  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: 10
    }}
  >
    <span>
      👤 {auth.username}
    </span>

    

    <button
      onClick={() => auth.logout()}
      style={{
        background: "transparent",
        border: "1px solid #444",
        color: "white",
        padding: "6px 12px",
        borderRadius: 8,
        cursor: "pointer"
      }}
    >
      Logout
    </button>
  </div>

</div>

{uploadMessage && (
  <div className="max-w-4xl mx-auto px-6 pt-4">

    <div
      className={`rounded-xl border p-4 ${
        uploadMessage.success
          ? "bg-green-900/20 border-green-700"
          : "bg-red-900/20 border-red-700"
      }`}
    >

      <div className="font-semibold">
        {uploadMessage.success
          ? "✅ PDF Uploaded Successfully"
          : "❌ Upload Failed"}
      </div>

      <div className="text-sm text-zinc-400 mt-1">
        {uploadMessage.filename}
      </div>

    </div>

  </div>
)}


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
                          <ReactMarkdown
  components={{
    h1: ({children}) => (
      <h1 className="text-2xl font-bold mb-3">
        {children}
      </h1>
    ),
    h2: ({children}) => (
      <h2 className="text-xl font-semibold mt-4 mb-2">
        {children}
      </h2>
    ),
    h3: ({children}) => (
      <h3 className="text-lg font-semibold mt-3 mb-2">
        {children}
      </h3>
    ),
    ul: ({children}) => (
      <ul className="list-disc ml-5 space-y-1">
        {children}
      </ul>
    ),
    ol: ({children}) => (
      <ol className="list-decimal ml-5 space-y-1">
        {children}
      </ol>
    ),
    p: ({children}) => (
      <p className="mb-3">
        {children}
      </p>
    )
  }}
>
  {item.content}
</ReactMarkdown>
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

        {/* ANALYSIS TRACE */}
{/* ANALYSIS TRACE */}

{analysisTrace.length > 0 && (

  <div className="border-t border-zinc-800 bg-zinc-950">

    <button
      onClick={() => setShowTrace(!showTrace)}
      className="w-full p-4 flex items-center justify-between hover:bg-zinc-900 transition"
    >
      <h3 className="font-bold text-lg">
        Analysis Trace ({analysisTrace.length})
      </h3>

      <span className="text-zinc-400">
        {showTrace ? "▼" : "▶"}
      </span>
    </button>

    {showTrace && (

      <div className="p-4 max-h-96 overflow-y-auto">

        {analysisTrace.map((item, index) => (

          <div
            key={index}
            className="mb-3 p-3 bg-zinc-900 rounded-lg border border-zinc-800"
          >

            <div className="text-xs text-zinc-500">
              {new Date(item.timestamp).toLocaleTimeString()}
            </div>

            <div className="font-semibold capitalize mb-2">
              {item.type}
            </div>

            {item.type === "followup" ? (

              <div className="mt-2 space-y-2">
                {item.data.questions?.map((q, idx) => (
                  <div
                    key={idx}
                    className="bg-zinc-800 p-2 rounded-lg text-sm"
                  >
                    {idx + 1}. {q}
                  </div>
                ))}
              </div>

            ) : item.type === "diagnosis" ? (

              <div className="space-y-3 mt-3">

                {item.data.conditions?.map((condition, idx) => (

                  <div
                    key={idx}
                    className="bg-zinc-800 rounded-xl p-3"
                  >
                    <div className="flex justify-between">
                      <span className="font-medium">
                        {condition.name}
                      </span>

                      <span className="text-blue-400">
                        {condition.confidence}%
                      </span>
                    </div>

                    <p className="text-sm text-zinc-400 mt-2">
                      {condition.reasoning}
                    </p>
                  </div>

                ))}

                <div className="bg-blue-900/20 border border-blue-700 rounded-xl p-3">
                  <div className="text-xs text-zinc-400">
                    Recommended Specialist
                  </div>

                  <div className="font-medium mt-1">
                    {item.data.recommended_specialist}
                  </div>
                </div>

              </div>

            ) : item.type === "extraction" ? (

              <div className="space-y-3 mt-3">

                <div className="bg-zinc-800 rounded-xl p-3">
                  <div className="text-xs text-zinc-400">
                    Symptoms Detected
                  </div>

                  <div className="mt-2 flex flex-wrap gap-2">
                    {item.data.symptoms?.map((symptom, idx) => (
                      <span
                        key={idx}
                        className="bg-blue-600 px-3 py-1 rounded-full text-sm"
                      >
                        {symptom}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-zinc-800 rounded-xl p-3">
                  <div className="text-xs text-zinc-400">
                    Confidence
                  </div>

                  <div className="mt-1">
                    {(item.data.confidence * 100).toFixed(0)}%
                  </div>
                </div>

              </div>

            ) : item.type === "severity" ? (

              <div className="bg-zinc-800 rounded-xl p-4 mt-3">

                <div className="flex justify-between items-center">

                  <span className="font-medium">
                    Severity Score
                  </span>

                  <span
                    className={`px-3 py-1 rounded-full text-sm ${
                      item.data.level === "HIGH"
                        ? "bg-red-600"
                        : item.data.level === "MEDIUM"
                        ? "bg-yellow-600"
                        : "bg-green-600"
                    }`}
                  >
                    {item.data.level}
                  </span>

                </div>

                <div className="mt-3 text-sm text-zinc-400">
                  {item.data.reasoning}
                </div>

              </div>

            ) : item.type === "routing" ? (

              <div className="bg-zinc-800 rounded-xl p-4 mt-3">

                <div className="text-sm text-zinc-400 mb-3">
                  Agents Activated
                </div>

                <div className="flex flex-wrap gap-2">
                  {item.data.agents?.map((agent, idx) => (
                    <span
                      key={idx}
                      className="bg-purple-600 px-3 py-1 rounded-full text-sm"
                    >
                      {agent}
                    </span>
                  ))}
                </div>

              </div>

            ) : item.type === "rag" ? (

              <div className="grid grid-cols-2 gap-3 mt-3">

                <div className="bg-zinc-800 rounded-xl p-4">
                  <div className="text-zinc-400 text-sm">
                    PubMed Papers
                  </div>

                  <div className="text-2xl font-bold mt-2">
                    {item.data.pubmed_papers?.length || 0}
                  </div>
                </div>

                <div className="bg-zinc-800 rounded-xl p-4">
                  <div className="text-zinc-400 text-sm">
                    Local Documents
                  </div>

                  <div className="text-2xl font-bold mt-2">
                    {item.data.local_documents?.length || 0}
                  </div>
                </div>

              </div>

            ) : (

              <pre className="text-xs mt-2 whitespace-pre-wrap">
                {JSON.stringify(item.data, null, 2)}
              </pre>

            )}

          </div>

        ))}

      </div>

    )}

  </div>

)}

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
