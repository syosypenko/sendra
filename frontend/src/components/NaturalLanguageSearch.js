import React, { useMemo, useState } from 'react';
import { gmailSyncService, collectionService } from '../services/api';

const NaturalLanguageSearch = ({ onResults, onCollectionSaved, collections = [] }) => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [activeEmailId, setActiveEmailId] = useState(null);
  const [collectionName, setCollectionName] = useState('');
  const [selectedCollectionId, setSelectedCollectionId] = useState('');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleSearch = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    try {
      const response = await gmailSyncService.naturalQuery(prompt);
      setResult(response.data);
      setSelectedIds(new Set());
      setActiveEmailId(null);
      setFeedback(null);
      if (onResults) onResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
      alert('Error searching emails');
    } finally {
      setLoading(false);
    }
  };

  const toggleSelected = (gmailId) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(gmailId)) {
        next.delete(gmailId);
      } else {
        next.add(gmailId);
      }
      return next;
    });
  };

  const activeEmail = useMemo(() => {
    if (!result?.emails || !activeEmailId) return null;
    return result.emails.find((e) => e.gmail_id === activeEmailId || e.gmailId === activeEmailId);
  }, [activeEmailId, result]);

  const selectedEmails = useMemo(() => {
    if (!result?.emails) return [];
    return result.emails.filter((e) => selectedIds.has(e.gmail_id || e.gmailId));
  }, [result, selectedIds]);

  const handleSaveCollection = async () => {
    if (!collectionName.trim()) {
      setFeedback({ type: 'error', message: 'Please enter a collection name' });
      return;
    }
    if (selectedEmails.length === 0) {
      setFeedback({ type: 'error', message: 'Select at least one email to save' });
      return;
    }

    setSaving(true);
    setFeedback(null);
    try {
      console.log('💾 Saving collection:', { collectionName, emailCount: selectedEmails.length });
      await collectionService.create(collectionName.trim(), selectedEmails);
      console.log('✅ Collection saved successfully');
      setFeedback({ type: 'success', message: 'Saved to collection' });
      setCollectionName('');
      if (onCollectionSaved) {
        console.log('📢 Calling onCollectionSaved callback');
        onCollectionSaved();
      }
    } catch (error) {
      console.error('❌ Save collection error:', error);
      setFeedback({ type: 'error', message: 'Failed to save collection' });
    } finally {
      setSaving(false);
    }
  };

  const handleSaveToExisting = async () => {
    if (!selectedCollectionId) {
      setFeedback({ type: 'error', message: 'Select a collection' });
      return;
    }
    if (selectedEmails.length === 0) {
      setFeedback({ type: 'error', message: 'Select at least one email to save' });
      return;
    }

    setSaving(true);
    setFeedback(null);
    try {
      console.log('💾 Adding to collection:', { selectedCollectionId, emailCount: selectedEmails.length });
      await collectionService.addEmails(selectedCollectionId, selectedEmails);
      setFeedback({ type: 'success', message: 'Added to collection' });
      if (onCollectionSaved) onCollectionSaved();
    } catch (error) {
      console.error('❌ Save to existing error:', error);
      setFeedback({ type: 'error', message: 'Failed to add to collection' });
    } finally {
      setSaving(false);
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

          {/* Bulk Save Controls */}
          <div className="flex flex-wrap items-center gap-3 p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
            <input
              type="text"
              placeholder="New collection name"
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSaveCollection}
              disabled={saving}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400 transition"
            >
              {saving ? 'Saving...' : `Save ${selectedEmails.length} selected`}
            </button>

            <div className="flex items-center gap-2">
              <select
                value={selectedCollectionId}
                onChange={(e) => setSelectedCollectionId(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[200px]"
              >
                <option value="">Add to existing...</option>
                {collections.map((col) => (
                  <option key={col._id} value={col._id}>{col.name}</option>
                ))}
              </select>
              <button
                onClick={handleSaveToExisting}
                disabled={saving || !selectedCollectionId}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 transition"
              >
                {saving ? 'Saving...' : 'Add to selected'}
              </button>
            </div>

            {feedback && (
              <span className={feedback.type === 'error' ? 'text-red-600 text-sm' : 'text-green-600 text-sm'}>
                {feedback.message}
              </span>
            )}
          </div>

          {/* Email Results */}
          {result.emails && result.emails.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Subjects list with checkboxes */}
              <div className="lg:col-span-1 max-h-96 overflow-y-auto bg-white border border-gray-200 rounded-lg divide-y">
                {result.emails.map((email, idx) => {
                  const gmailId = email.gmail_id || email.gmailId || idx;
                  const isSelected = selectedIds.has(gmailId);
                  const isActive = activeEmailId === gmailId;
                  return (
                    <label
                      key={gmailId}
                      className={`flex items-start gap-3 p-3 cursor-pointer hover:bg-blue-50 transition ${isActive ? 'bg-blue-50' : ''}`}
                      onClick={() => setActiveEmailId(gmailId)}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          e.stopPropagation();
                          toggleSelected(gmailId);
                        }}
                        className="mt-1"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm text-blue-600 truncate cursor-pointer hover:underline">{email.subject || '(No Subject)'}</p>
                        <p className="text-xs text-gray-600 truncate">From: {email.from}</p>
                        <p className="text-xs text-gray-500">{email.received_at}</p>
                      </div>
                    </label>
                  );
                })}
              </div>

              {/* Email detail pane */}
              <div className="lg:col-span-2 bg-white border border-gray-200 rounded-lg p-4 min-h-[10rem]">
                {activeEmail ? (
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-lg font-semibold text-gray-900">{activeEmail.subject || '(No Subject)'}</p>
                        <p className="text-sm text-gray-600">From: {activeEmail.from}</p>
                        <p className="text-xs text-gray-500">{activeEmail.received_at}</p>
                      </div>
                    </div>
                    <div className="mt-3 p-3 bg-gray-50 rounded border border-gray-200 text-sm text-gray-800 whitespace-pre-wrap">
                      {activeEmail.body || 'No body available'}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Select an email to view its body.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NaturalLanguageSearch;
