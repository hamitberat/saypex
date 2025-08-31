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
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query) => {
    setSearchQuery(query);
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
                onSearch={handleSearch}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
              />
              
              <Sidebar />
              
              {/* Main Content with permanent sidebar space */}

              <main className="min-h-screen">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/watch" element={<Watch />} />
                  <Route path="/search" element={<SearchResults />} />
                  <Route path="/trending" element={<Trending />} />
                  <Route path="/explore" element={<Home />} />
                  <Route path="/shorts" element={<Home />} />
                  <Route path="/subscriptions" element={<Home />} />
                  <Route path="/history" element={<Home />} />
                  <Route path="/liked" element={<Home />} />
                  <Route path="/music" element={<Home />} />
                  <Route path="/gaming" element={<Home />} />
                  <Route path="/sports" element={<Home />} />
                  <Route path="/movies" element={<Home />} />
                  <Route path="/learning" element={<Home />} />
                  <Route path="/fashion" element={<Home />} />
                  <Route path="/channel/:channelName" element={<Home />} />
                  <Route path="/upload" element={<Upload />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/settings/2fa" element={<TFASettings />} />
                  <Route path="/help" element={<Home />} />
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