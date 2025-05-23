import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Upload, Play } from 'lucide-react';

// Main App Component
export default function App() {
  const [currentPage, setCurrentPage] = useState(0);
  const [chatOpen, setChatOpen] = useState(false);
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const [extractedVideo, setExtractedVideo] = useState(null);
  const [messages, setMessages] = useState([
    { text: "Hi there! How can I assist you with your Cricket queries?", sender: "bot" }
  ]);
  const [newMessage, setNewMessage] = useState("");
  
  const pageRefs = [useRef(null), useRef(null)];
  
  // Scroll to page
  const scrollToPage = (pageIndex) => {
    pageRefs[pageIndex].current.scrollIntoView({ behavior: 'smooth' });
    setCurrentPage(pageIndex);
  };
  
  // Handle file upload
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (file && file.type.startsWith('video/')) {
    const videoUrl = URL.createObjectURL(file);
    setUploadedVideo(videoUrl);


    try {
      // Send the file to Flask (or just the path if running locally)
      const formData = new FormData();
      formData.append('video', file);

      const response = await fetch('http://localhost:8000/generate_highlight', {
        method: 'POST',
        body: formData, // Send as FormData (or JSON if using path)
      });

      if (!response.ok) throw new Error("Failed to generate highlights");

      const result = await response.json();
      
      // The API returns a path like "/get_highlight/output0/final_highlights_video0.mp4"
      const processedVideoPath = result.video_path;

      // Construct full URL to fetch the processed video
      const processedVideoUrl = `http://localhost:8000${processedVideoPath}`;
      
      // Update state to display the processed video
      setExtractedVideo(processedVideoUrl);
      
    } catch (err) {
      console.error("Error processing video:", err);
      // Fallback: Use the original video for demo purposes
      setExtractedVideo(videoUrl);
    }
  }
};  
const handleSendMessage = async () => {
  if (newMessage.trim() !== "") {
    const userMsg = newMessage.trim();
    setMessages([...messages, { text: userMsg, sender: "user" }]);
    setNewMessage("");

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: userMsg })
      });

      if (!response.ok) {
        throw new Error("Failed to get response from the chat API");
      }

      const result = await response.json();
      const botReply = result.response || "Sorry, I couldn't understand that.";

      setMessages(prev => [...prev, { text: botReply, sender: "bot" }]);
    } catch (err) {
      console.error("Error during chat:", err);
      setMessages(prev => [...prev, { text: "There was an error processing your message.", sender: "bot" }]);
    }
  }
};


  // Handle Enter key in chat
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };
  
  return (
    <div className="bg-gray-900 text-gray-100 min-h-screen flex flex-col">
      {/* First Page - Landing */}
      <div 
        ref={pageRefs[0]} 
        className="h-screen flex flex-col items-center justify-center relative"
      >
        <div className="text-center px-4">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-blue-500 text-transparent bg-clip-text">
            We are looking forward for Live highlights
          </h1>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Upload your videos and we'll extract the most exciting moments automatically
          </p>
          <button 
            onClick={() => scrollToPage(1)}
            className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full text-lg font-medium hover:opacity-90 transition-all"
          >
            Get Started
          </button>
        </div>
        
        {/* Animated scroll indicator */}
        <div className="absolute bottom-8 animate-bounce">
          <div className="w-8 h-12 rounded-full border-2 border-gray-400 flex items-start justify-center">
            <div className="w-2 h-2 bg-gray-400 rounded-full mt-2 animate-pulse"></div>
          </div>
        </div>
      </div>
      
      {/* Second Page - Upload/Results */}
      <div 
        ref={pageRefs[1]} 
        className="min-h-screen flex flex-col items-center justify-center p-8"
      >
        <div className="w-full max-w-4xl bg-gray-800 rounded-xl p-6 shadow-lg">
          <h2 className="text-3xl font-semibold mb-6 text-center">
            {!extractedVideo ? "Upload your video" : "Your Highlight Reel"}
          </h2>
          
          {!uploadedVideo ? (
            <div 
              className="border-2 border-dashed border-gray-600 rounded-lg p-12 flex flex-col items-center justify-center cursor-pointer hover:border-purple-500 transition-colors"
              onClick={() => document.getElementById('videoUpload').click()}
            >
              <Upload size={48} className="text-gray-500 mb-4" />
              <p className="text-gray-400 text-center mb-2">Drag and drop your video here or click to browse</p>
              <p className="text-gray-500 text-sm">Supports MP4, MOV, AVI (max 500MB)</p>
              <input 
                id="videoUpload" 
                type="file" 
                accept="video/*" 
                className="hidden" 
                onChange={handleFileUpload}
              />
            </div>
          ) : extractedVideo ? (
            <div className="space-y-6">
              <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
                <video 
                  src={extractedVideo} 
                  className="w-full h-full object-contain" 
                  controls
                />
              </div>
              <div className="flex justify-between">
                <button 
                  onClick={() => {setUploadedVideo(null); setExtractedVideo(null);}}
                  className="px-4 py-2 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors"
                >
                  Upload New Video
                </button>
                <button 
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-md hover:opacity-90 transition-colors flex items-center"
                >
                  <Play size={16} className="mr-2" />
                  Save Highlights
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-gray-300">Processing your video...</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Floating Chat Bot */}
      <div className="fixed bottom-6 right-6 z-50">
        {chatOpen ? (
          <div className="w-80 h-96 bg-gray-800 rounded-xl shadow-xl flex flex-col overflow-hidden border border-gray-700">
            {/* Chat Header */}
            <div className="bg-gray-900 p-3 flex justify-between items-center border-b border-gray-700">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <h3 className="font-medium">Chat Assistant</h3>
              </div>
              <button 
                onClick={() => setChatOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>
            
            {/* Messages Area */}
            <div className="flex-1 p-3 overflow-y-auto space-y-3">
              {messages.map((msg, index) => (
                <div 
                  key={index} 
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    className={`rounded-lg px-3 py-2 max-w-xs ${
                      msg.sender === 'user' 
                        ? 'bg-blue-600' 
                        : 'bg-gray-700'
                    }`}
                  >
                    <p className="text-sm">{msg.text}</p>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Input Area */}
            <div className="p-3 border-t border-gray-700 flex">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type a message..."
                className="flex-1 bg-gray-700 border-none rounded-l-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-purple-500 text-sm"
              />
              <button 
                onClick={handleSendMessage}
                className="bg-purple-600 rounded-r-md px-3 flex items-center justify-center hover:bg-purple-700"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        ) : (
          <button 
            onClick={() => setChatOpen(true)}
            className="w-14 h-14 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center shadow-lg hover:shadow-xl transition-shadow"
          >
            <MessageSquare size={24} />
          </button>
        )}
      </div>
      
      {/* Navigation Dots */}
      <div className="fixed right-6 top-1/2 transform -translate-y-1/2 z-40">
        <div className="flex flex-col space-y-3">
          {[0, 1].map((pageIndex) => (
            <button
              key={pageIndex}
              onClick={() => scrollToPage(pageIndex)}
              className={`w-3 h-3 rounded-full transition-all ${
                currentPage === pageIndex 
                  ? 'bg-purple-500 w-6' 
                  : 'bg-gray-600 hover:bg-gray-500'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

