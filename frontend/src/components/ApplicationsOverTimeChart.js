import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ApplicationsOverTimeChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">Applications Over Time</h2>
        <p className="text-gray-500">No application data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Applications Over Time</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            angle={-45}
            textAnchor="end"
            height={80}
            interval={Math.max(0, Math.floor(data.length / 6))}
          />
          <YAxis />
          <Tooltip 
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
            formatter={(value) => value}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="applied" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={false}
            name="Applied"
          />
          <Line 
            type="monotone" 
            dataKey="interview" 
            stroke="#8b5cf6" 
            strokeWidth={2}
            dot={false}
            name="Interview"
          />
          <Line 
            type="monotone" 
            dataKey="offer" 
            stroke="#10b981" 
            strokeWidth={2}
            dot={false}
            name="Offer"
          />
          <Line 
            type="monotone" 
            dataKey="rejected" 
            stroke="#ef4444" 
            strokeWidth={2}
            dot={false}
            name="Rejected"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ApplicationsOverTimeChart;
