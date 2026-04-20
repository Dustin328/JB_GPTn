import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import Login from './components/Login'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState('')
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  const [sidebarKey, setSidebarKey] = useState(0) // Force sidebar refresh

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUsername = localStorage.getItem('username')
    if (token && savedUsername) {
      setIsAuthenticated(true)
      setUsername(savedUsername)
    }
  }, [])

  const handleLogin = (_token: string, user: string) => {
    setIsAuthenticated(true)
    setUsername(user)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setIsAuthenticated(false)
    setUsername('')
    setCurrentConversationId(null)
  }

  const handleNewChat = () => {
    setCurrentConversationId(null)
  }

  const handleSelectConversation = (conversationId: number) => {
    setCurrentConversationId(conversationId)
  }

  const handleConversationCreated = (conversationId: number) => {
    setCurrentConversationId(conversationId)
    // Refresh sidebar to show new conversation
    setSidebarKey(prev => prev + 1)
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="min-h-screen bg-gray-900 flex">
      <Sidebar
        key={sidebarKey}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        currentConversationId={currentConversationId}
        onLogout={handleLogout}
        username={username}
      />
      
      <div className="flex-1 flex flex-col">
        <header className="bg-gray-800 border-b border-gray-700 py-4 px-6">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">
              JailbrokeGPT
            </h1>
            <span className="text-sm text-gray-400">
              Uncensored AI Chat
            </span>
          </div>
        </header>
        
        <main className="flex-1">
          <ChatInterface 
            conversationId={currentConversationId}
            onConversationCreated={handleConversationCreated}
          />
        </main>
        
        <footer className="bg-gray-800 border-t border-gray-700 py-2 px-6 text-center">
          <p className="text-xs text-gray-500">
            Built by Peter Surowski | Copyright 2026
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
