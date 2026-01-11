import React from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

export const ApplicationStatusChart = ({ data }) => {
  const chartData = {
    labels: data.map((item) => (item._id || 'Unknown').toUpperCase()),
    datasets: [
      {
        label: 'Emails',
        data: data.map((item) => item.count),
        backgroundColor: [
          'rgba(34, 197, 94, 0.5)',
          'rgba(59, 130, 246, 0.5)',
          'rgba(251, 146, 60, 0.5)',
          'rgba(239, 68, 68, 0.5)',
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(251, 146, 60)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2
      }
    ]
  };

  return <Bar data={chartData} options={{ responsive: true, indexAxis: 'y' }} />;
};

export const JobTypeChart = ({ data }) => {
  const chartData = {
    labels: data.map((item) => item._id?.toUpperCase() || 'Unknown'),
    datasets: [
      {
        label: 'Opportunities',
        data: data.map((item) => item.count),
        backgroundColor: [
          'rgba(99, 102, 241, 0.5)',
          'rgba(168, 85, 247, 0.5)',
          'rgba(236, 72, 153, 0.5)',
          'rgba(6, 182, 212, 0.5)',
        ],
        borderColor: [
          'rgb(99, 102, 241)',
          'rgb(168, 85, 247)',
          'rgb(236, 72, 153)',
          'rgb(6, 182, 212)',
        ]
      }
    ]
  };

  return <Pie data={chartData} options={{ responsive: true }} />;
};

export const ApplicationFunnelChart = ({ data }) => {
  const funnel = [
    { label: 'Applied', value: data.applied || 0 },
    { label: 'Interview', value: data.interview || 0 },
    { label: 'Offer', value: data.offer || 0 },
    { label: 'Rejected', value: data.rejected || 0 }
  ];

  const chartData = {
    labels: funnel.map(item => item.label),
    datasets: [
      {
        label: 'Count',
        data: funnel.map(item => item.value),
        backgroundColor: [
          'rgba(34, 197, 94, 0.6)',
          'rgba(59, 130, 246, 0.6)',
          'rgba(251, 146, 60, 0.6)',
          'rgba(239, 68, 68, 0.6)',
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(251, 146, 60)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2
      }
    ]
  };

  return <Bar data={chartData} options={{ responsive: true }} />;
};

export const ExperienceLevelChart = ({ data }) => {
  const chartData = {
    labels: data.map((item) => item._id?.toUpperCase() || 'Unknown'),
    datasets: [
      {
        label: 'Opportunities',
        data: data.map((item) => item.count),
        backgroundColor: 'rgba(99, 102, 241, 0.5)',
        borderColor: 'rgb(99, 102, 241)',
        borderWidth: 2
      }
    ]
  };

  return <Bar data={chartData} options={{ responsive: true }} />;
};
