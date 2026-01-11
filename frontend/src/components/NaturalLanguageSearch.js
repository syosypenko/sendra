import React, { useState } from 'react';
import { gmailSyncService } from '../services/api';

const NaturalLanguageSearch = ({ onResults }) => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSearch = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    try {
      const response = await gmailSyncService.naturalQuery(prompt);
      setResult(response.data);
      if (onResults) onResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
      alert('Error searching emails');
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = [
    "Show me all job offers",
    "Get me rejection letters",
    "Find backend developer roles",
    "Show contract positions",
    "Get interviews from FAANG companies",
    "Find senior level opportunities"
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">AI-Powered Email Search</h2>
      <p className="text-gray-600 mb-4">Type natural language queries to find emails</p>
      
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="e.g., 'Show me all job offers from tech companies'"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          onClick={handleSearch}
          disabled={loading || !prompt.trim()}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Example Prompts */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Try these:</p>
        <div className="flex flex-wrap gap-2">
          {examplePrompts.map((example, idx) => (
            <button
              key={idx}
              onClick={() => setPrompt(example)}
              className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded transition"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Search Results Summary */}
      {result && (
        <div className="mt-4 space-y-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-700">
              <strong>Intent:</strong> {result.query_intent} | 
              <strong className="ml-2">Found:</strong> {result.count} emails
            </p>
            <p className="text-sm text-gray-600 mt-2">{result.summary}</p>
            {result.error && (
              <p className="text-sm text-red-600 mt-2">⚠️ {result.error}</p>
            )}
          </div>

          {/* Email Results */}
          {result.emails && result.emails.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-800">Matching Emails:</h3>
              <div className="max-h-96 overflow-y-auto space-y-2">
                {result.emails.map((email, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition">
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm text-gray-900 truncate">{email.subject}</p>
                        <p className="text-xs text-gray-600 truncate">From: {email.from}</p>
                        <p className="text-xs text-gray-500 mt-1">{email.received_at}</p>
                      </div>
                      {email.body && (
                        <div className="flex-1 text-xs text-gray-700 line-clamp-2 bg-white p-2 rounded border border-gray-200">
                          {email.body.substring(0, 200)}...
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NaturalLanguageSearch;
