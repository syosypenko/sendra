import React from 'react';

const PredictiveInsights = ({ insights }) => {
  if (!insights || insights.total_applications === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">📊 Predictive Insights</h2>
        <p className="text-gray-500">Add emails to collections to see predictions</p>
      </div>
    );
  }

  const getMomentumColor = (momentum) => {
    switch (momentum) {
      case 'increasing': return 'text-green-600';
      case 'decreasing': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getMomentumIcon = (momentum) => {
    switch (momentum) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  const getMomentumText = (momentum) => {
    switch (momentum) {
      case 'increasing': return 'Activity is increasing';
      case 'decreasing': return 'Activity is declining';
      case 'neutral': return 'Activity is stable';
      default: return 'Insufficient data';
    }
  };

  const getProbabilityColor = (prob) => {
    if (prob >= 60) return 'text-green-600 bg-green-50 border-green-200';
    if (prob >= 30) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">📊 Predictive Insights</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Offer Probability */}
        <div className={`p-4 rounded-lg border-2 ${getProbabilityColor(insights.offer_probability_30d)}`}>
          <div className="text-sm font-medium mb-1">Offer Likelihood (30 days)</div>
          <div className="text-3xl font-bold mb-2">{insights.offer_probability_30d}%</div>
          <div className="text-xs">
            {insights.offer_probability_30d < 20 && "Low probability based on current trends"}
            {insights.offer_probability_30d >= 20 && insights.offer_probability_30d < 50 && "Moderate chance with continued activity"}
            {insights.offer_probability_30d >= 50 && "Strong likelihood with recent momentum"}
          </div>
        </div>

        {/* Expected Time to Offer */}
        <div className="p-4 rounded-lg border-2 border-blue-200 bg-blue-50">
          <div className="text-sm font-medium text-blue-900 mb-1">Expected Time to Offer</div>
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {insights.expected_days_to_offer ? `~${insights.expected_days_to_offer}` : 'N/A'}
            {insights.expected_days_to_offer && <span className="text-lg"> days</span>}
          </div>
          <div className="text-xs text-blue-700">
            {insights.expected_days_to_offer 
              ? "Based on historical pattern" 
              : "Need more offer data"}
          </div>
        </div>

        {/* Momentum */}
        <div className="p-4 rounded-lg border-2 border-purple-200 bg-purple-50">
          <div className="text-sm font-medium text-purple-900 mb-1">Application Momentum</div>
          <div className={`text-2xl font-bold mb-2 ${getMomentumColor(insights.momentum)}`}>
            {getMomentumIcon(insights.momentum)} {getMomentumText(insights.momentum)}
          </div>
          <div className="text-xs text-purple-700">
            {insights.recent_activity} applications in last 30 days
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="border-t pt-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">{insights.total_applications}</div>
            <div className="text-xs text-gray-600">Total Applications</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{insights.recent_activity}</div>
            <div className="text-xs text-gray-600">Recent (30d)</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{insights.conversion_rate}%</div>
            <div className="text-xs text-gray-600">Conversion Rate</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {insights.momentum === 'increasing' ? '🚀' : insights.momentum === 'decreasing' ? '⚠️' : '✓'}
            </div>
            <div className="text-xs text-gray-600">Trend</div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-4 p-3 bg-gray-50 rounded border border-gray-200">
        <p className="text-xs text-gray-600">
          <strong>Note:</strong> Predictions are probabilistic estimates based on historical patterns and recent activity. 
          Actual outcomes may vary based on market conditions, application quality, and timing.
        </p>
      </div>
    </div>
  );
};

export default PredictiveInsights;
