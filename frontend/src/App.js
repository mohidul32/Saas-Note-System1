import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import PublicNotesPage from './pages/PublicNotesPage';
import MyNotesPage from './pages/MyNotesPage';
import NoteEditorPage from './pages/NoteEditorPage';
import NoteDetailPage from './pages/NoteDetailPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Navigation from './components/Navigation';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token');

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Navigation />
          <div className="container">
            <Routes>
              <Route path="/" element={<PublicNotesPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route 
                path="/my-notes" 
                element={isAuthenticated ? <MyNotesPage /> : <Navigate to="/login" />} 
              />
              <Route 
                path="/notes/create" 
                element={isAuthenticated ? <NoteEditorPage /> : <Navigate to="/login" />} 
              />
              <Route 
                path="/notes/:id/edit" 
                element={isAuthenticated ? <NoteEditorPage /> : <Navigate to="/login" />} 
              />
              <Route path="/notes/:id" element={<NoteDetailPage />} />
            </Routes>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
