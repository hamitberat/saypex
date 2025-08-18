import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Watch from './pages/Watch';
import SearchResults from './pages/SearchResults';
import Trending from './pages/Trending';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Upload from './pages/Upload';
import Settings from './pages/Settings';
import TFASettings from './pages/TFASettings';
import { Toaster } from './components/ui/sonner';
import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleMenuClick = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const handleOverlayClick = () => {
    if (isMobile && sidebarOpen) {
      setSidebarOpen(false);
    }
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-purple-50/30 via-white to-blue-50/30">
        <Routes>
          {/* Auth Routes (No Header/Sidebar) */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          {/* Main App Routes */}
          <Route path="/*" element={
            <>
              <Header 
                onMenuClick={handleMenuClick}
                onSearch={handleSearch}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
              />
              
              <Sidebar 
                isOpen={sidebarOpen} 
                isMobile={isMobile}
              />
              
              {/* Mobile overlay */}
              {isMobile && sidebarOpen && (
                <div 
                  className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
                  onClick={handleOverlayClick}
                />
              )}

              <main className="min-h-screen">
                <Routes>
                  <Route path="/" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/watch" element={<Watch sidebarOpen={sidebarOpen} />} />
                  <Route path="/results" element={<SearchResults sidebarOpen={sidebarOpen} />} />
                  <Route path="/trending" element={<Trending sidebarOpen={sidebarOpen} />} />
                  <Route path="/explore" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/shorts" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/subscriptions" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/history" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/liked" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/music" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/gaming" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/sports" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/movies" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/learning" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/fashion" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/channel/:channelName" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/upload" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/settings" element={<Home sidebarOpen={sidebarOpen} />} />
                  <Route path="/help" element={<Home sidebarOpen={sidebarOpen} />} />
                </Routes>
              </main>
            </>
          } />
        </Routes>

        <Toaster 
          position="bottom-right"
          toastOptions={{
            style: {
              background: 'linear-gradient(to right, #7c3aed, #2563eb)',
              color: 'white',
              border: 'none',
            },
          }}
        />
      </div>
    </BrowserRouter>
  );
}

export default App;