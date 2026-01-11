import React, { useEffect, useState } from 'react';
import { analyticsService } from '../services/api';
import NaturalLanguageSearch from '../components/NaturalLanguageSearch';
import {
  ApplicationStatusChart,
  JobTypeChart,
  ApplicationFunnelChart,
  ExperienceLevelChart
} from '../components/AdvancedCharts';
import { useAuthStore } from '../hooks/useStore';

const AdvancedDashboardPage = () => {
  const { user } = useAuthStore();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchResults, setSearchResults] = useState(null);

  useEffect(() => {
    fetchDashboard();
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

  const handleSearchResults = (results) => {
    setSearchResults(results);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-screen text-gray-600">Loading dashboard...</div>;
  }

  const stats = dashboard?.stats || {};
  const funnel = dashboard?.funnel || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Application Dashboard</h1>
          <p className="text-gray-600">AI-powered email insights and opportunity tracking</p>
        </div>

        {/* Natural Language Search */}
        <NaturalLanguageSearch onResults={handleSearchResults} />

        {/* Email Search Results - Full Table View */}
        {searchResults?.emails && searchResults.emails.length > 0 && (
          <div className="mb-8 bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">Search Results</h2>
              <span className="text-lg font-semibold text-gray-600">
                Found: <span className="text-blue-600">{searchResults.count}</span> emails
              </span>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200 bg-gray-50">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Subject</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">From</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Preview</th>
                  </tr>
                </thead>
                <tbody>
                  {searchResults.emails.map((email, idx) => (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-blue-50 transition">
                      <td className="py-3 px-4">
                        <p className="font-medium text-gray-900 truncate">{email.subject || '(No Subject)'}</p>
                      </td>
                      <td className="py-3 px-4">
                        <p className="text-sm text-gray-600 truncate">{email.from}</p>
                      </td>
                      <td className="py-3 px-4">
                        <p className="text-sm text-gray-500">{new Date(email.received_at).toLocaleDateString()}</p>
                      </td>
                      <td className="py-3 px-4">
                        <p className="text-sm text-gray-600 truncate max-w-xs">
                          {email.body?.substring(0, 100) || '(No body)'}...
                        </p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Key Metrics */}
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-3xl font-bold">Dashboard</h1>
              {user && (
                <div className="text-sm text-gray-600">
                  Signed in as <span className="font-medium">{user.name || user.email}</span>
                </div>
              )}
            </div>
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Total Emails</p>
            <p className="text-3xl font-bold text-gray-900">{stats.total || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Applications</p>
            <p className="text-3xl font-bold text-green-600">{funnel.applied || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Interviews</p>
            <p className="text-3xl font-bold text-blue-600">{funnel.interview || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Offers</p>
            <p className="text-3xl font-bold text-orange-600">{funnel.offer || 0}</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          {/* Application Status */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Application Status</h2>
            {dashboard?.by_status?.length > 0 ? (
              <ApplicationStatusChart data={dashboard.by_status} />
            ) : (
              <p className="text-gray-500">No data available</p>
            )}
          </div>

          {/* Job Type Distribution */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Job Type Distribution</h2>
            {dashboard?.by_type?.length > 0 ? (
              <JobTypeChart data={dashboard.by_type} />
            ) : (
              <p className="text-gray-500">No data available</p>
            )}
          </div>

          {/* Application Funnel */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Application Funnel</h2>
            {funnel && Object.keys(funnel).length > 0 ? (
              <ApplicationFunnelChart data={funnel} />
            ) : (
              <p className="text-gray-500">No data available</p>
            )}
          </div>

          {/* Experience Level */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Experience Level</h2>
            {dashboard?.by_experience?.length > 0 ? (
              <ExperienceLevelChart data={dashboard.by_experience} />
            ) : (
              <p className="text-gray-500">No data available</p>
            )}
          </div>
        </div>

        {/* Top Companies and Positions */}
        <div className="grid grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Top Companies</h2>
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
              <p className="text-gray-500">No data available</p>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Top Positions</h2>
            {dashboard?.top_positions?.length > 0 ? (
              <div className="space-y-2">
                {dashboard.top_positions.map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                    <span className="text-gray-700 capitalize">{item._id || 'Unknown'}</span>
                    <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                      {item.count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedDashboardPage;
