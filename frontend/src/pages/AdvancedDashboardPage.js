import React, { useEffect, useState } from 'react';
import { analyticsService, collectionService } from '../services/api';
import NaturalLanguageSearch from '../components/NaturalLanguageSearch';
import ApplicationsOverTimeChart from '../components/ApplicationsOverTimeChart';
import PredictiveInsights from '../components/PredictiveInsights';
import { useAuthStore } from '../hooks/useStore';

const AdvancedDashboardPage = () => {
  const { user } = useAuthStore();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchResults, setSearchResults] = useState(null);
  const [collections, setCollections] = useState([]);
  const [expandedCollection, setExpandedCollection] = useState(null);
  const [activeEmailInCollection, setActiveEmailInCollection] = useState(null);

  useEffect(() => {
    fetchDashboard();
    fetchCollections();
  }, []);
  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const response = await analyticsService.getDashboardSummary();
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchResults = (results) => setSearchResults(results);
  const fetchCollections = async () => {
    try {
      const response = await collectionService.list();
      setCollections(response.data || []);
    } catch (error) {
      console.error('❌ Error fetching collections:', error);
    }
  };

  const handleDeleteCollection = async (collectionId) => {
    if (!window.confirm('Are you sure you want to delete this collection?')) return;
    try {
      await collectionService.delete(collectionId);
      setExpandedCollection(null);
      fetchCollections();
    } catch (error) {
      console.error('❌ Error deleting collection:', error);
      alert('Failed to delete collection');
    }
  };

  const handleDeleteEmail = async (collectionId, gmailId) => {
  if (!gmailId) return;
  if (!window.confirm('Delete this email from the collection?')) return;
  try {
      await collectionService.deleteEmail(collectionId, gmailId);
      fetchCollections();
    } catch (error) {
      console.error('❌ Error deleting email:', error);
      alert('Failed to delete email');
    }
  };

  if (loading) return <div className="flex items-center justify-center h-screen text-gray-600">Loading dashboard...</div>;
  const stats = dashboard?.stats || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Application Dashboard</h1>
          <p className="text-gray-600">AI-powered email insights and opportunity tracking</p>
  </div>

  {/* Natural Language Search */}
        <NaturalLanguageSearch
          onResults={handleSearchResults}
          onCollectionSaved={fetchCollections}
          collections={collections}
        />

        {/* Saved Collections Section */}
        <div className="mb-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Saved Collections</h2>
          {collections && collections.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {collections.map((collection) => (
                <div key={collection._id} className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-lg text-gray-900">{collection.name}</h3>
                    <button
                      onClick={() => handleDeleteCollection(collection._id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded transition"
                      title="Delete collection"
                    >
                      🗑️
                    </button>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600 mb-3">
                    <p><span className="font-medium">Emails:</span> {collection.emails?.length || 0}</p>
                    <p><span className="font-medium">Created:</span> {new Date(collection.created_at).toLocaleDateString()}</p>
                  </div>
                  <button
                    onClick={() => setExpandedCollection(expandedCollection === collection._id ? null : collection._id)}
                    className="text-sm bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded transition"
                  >
                    {expandedCollection === collection._id ? '▼ Hide' : '▶ Show'} Emails
                  </button>
                  
                  {/* Expanded emails view */}
                  {expandedCollection === collection._id && collection.emails && collection.emails.length > 0 && (
                    <div className="mt-4 bg-white rounded p-3 max-h-96 overflow-y-auto border border-gray-200">
                      <div className="space-y-3">
                        {collection.emails.map((email, idx) => {
                          const emailKey = email.gmail_id || idx;
                          const isActive = activeEmailInCollection === emailKey;
                          return (
                            <div key={idx} className="border-b border-gray-200 pb-3 last:border-b-0">
                              <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                  <p 
                                    className="font-bold text-blue-600 text-sm mb-1 cursor-pointer hover:underline"
                                    onClick={() => setActiveEmailInCollection(isActive ? null : emailKey)}
                                  >
                                    {isActive ? '▼ ' : '▶ '}{email.subject || '(no subject)'}
                                  </p>
                                  <p className="text-xs text-gray-600 mb-1">
                                    <span className="font-semibold">From:</span> {email.from || 'unknown'}
                                  </p>
                                  {email.received_at && (
                                    <p className="text-xs text-gray-500 mb-2">
                                      <span className="font-semibold">Date:</span> {new Date(email.received_at).toLocaleString()}
                                    </p>
                                  )}
                                  {isActive && email.body && (
                                    <div className="mt-2 bg-gray-50 p-3 rounded border border-gray-200">
                                      <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
                                        {email.body}
                                      </p>
                                    </div>
                                  )}
                                </div>
                                {email.gmail_id && (
                                  <button
                                    onClick={() => handleDeleteEmail(collection._id, email.gmail_id)}
                                    className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded transition"
                                    title="Delete email"
                                  >
                                    🗑️
                                  </button>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No collections saved yet</p>
          )}
  </div>

  {/* Totals */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Total Emails</p>
            <p className="text-3xl font-bold text-gray-900">{stats.total || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Total Companies</p>
            <p className="text-3xl font-bold text-gray-900">{dashboard?.company_count ?? (dashboard?.top_companies?.length || 0)}</p>
          </div>
  </div>

        {/* Predictive Insights */}
        {dashboard?.predictive_insights && (
          <div className="mb-8">
            <PredictiveInsights insights={dashboard.predictive_insights} />
          </div>
        )}

        {/* Applications Over Time Chart */}
        {dashboard && (
          <div className="mb-8">
            {dashboard?.applications_over_time && dashboard.applications_over_time.length > 0 ? (
              <ApplicationsOverTimeChart data={dashboard.applications_over_time} />
            ) : (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-2xl font-bold mb-4">Applications Over Time</h2>
                <p className="text-gray-500">Add emails to collections to see application trends</p>
              </div>
            )}
          </div>
        )}

        {/* Top Companies */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-4">Top Companies</h2>
          {dashboard?.top_companies?.length > 0 ? (
            <div className="space-y-2">
              {dashboard.top_companies.map((item, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                  <span className="text-gray-700">{item._id || 'Unknown'}</span>
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                    {item.count}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No company data available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedDashboardPage;
