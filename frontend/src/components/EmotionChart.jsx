/**
 * EmotionChart Component
 * 
 * Displays emotion distribution as a simple bar chart.
 * Uses Recharts library for visualization.
 */

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function EmotionChart({ emotions }) {
  if (!emotions || typeof emotions !== 'object') {
    return <p>No emotion data to display</p>;
  }

  // Convert emotions object to array for Recharts
  const data = Object.entries(emotions).map(([emotion, count]) => ({
    emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
    count: count,
  }));

  // Sort by count descending
  data.sort((a, b) => b.count - a.count);

  return (
    <div style={{ width: '100%', height: 300, marginTop: 20 }}>
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="emotion" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default EmotionChart;
