import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from './services/api';
import { useAuthStore } from './hooks/useStore';
import AdvancedDashboardPage from './pages/AdvancedDashboardPage';

const CallbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      if (!code) {
        setError('No authorization code received');
        return;
      }

      try {
        // Send code to backend for exchange
        const response = await authService.exchangeCode(code);
        setUser(response.data.user);
        navigate('/dashboard');
      } catch (err) {
        console.error('Callback error:', err);
        setError('Authentication failed');
      }
    };

    handleCallback();
  }, [searchParams, navigate, setUser]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow">
          <p className="text-red-600">{error}</p>
          <button onClick={() => navigate('/')} className="mt-4 text-blue-600">
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <p className="text-gray-600">Authenticating...</p>
    </div>
  );
};

const LoginPage = () => {
  const handleLogin = async () => {
    try {
      await authService.login();
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
        <h1 className="text-4xl font-bold text-center mb-2">Sendra</h1>
        <p className="text-center text-gray-600 mb-8">AI-Powered Email Management</p>
        
        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-200 mb-4"
        >
          Sign in with Google
        </button>
        
        <div className="text-sm text-gray-600 space-y-2">
          <p className="font-semibold">Features:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Natural language email search</li>
            <li>AI-powered categorization</li>
            <li>Application tracking</li>
            <li>Advanced analytics</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  const { user, setUser } = useAuthStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authService.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
          <Route path="/callback" element={<CallbackPage />} />
        {!user ? (
          <Route path="*" element={<LoginPage />} />
        ) : (
          <>
            <Route path="/" element={<AdvancedDashboardPage />} />
            <Route path="/dashboard" element={<AdvancedDashboardPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        )}
      </Routes>
    </Router>
  );
};

export default App;
