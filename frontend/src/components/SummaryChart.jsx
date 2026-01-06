/**
 * SummaryChart Component
 * 
 * Displays all people's dominant emotions over time in a single chart.
 * X-axis: Frame number, Y-axis: Person ID
 * Shows emotion changes as colored segments for each person.
 */

import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

// Emotion colors matching the video overlay colors
const EMOTION_COLORS = {
  happy: '#4CAF50',
  sad: '#2196F3',
  angry: '#F44336',
  neutral: '#9E9E9E',
  surprise: '#FF9800',
  fear: '#9C27B0',
  disgust: '#795548',
};

function SummaryChart({ emotionData }) {
  if (!emotionData || typeof emotionData !== 'object' || Object.keys(emotionData).length === 0) {
    return <p>No data to display</p>;
  }

  // Create scatter plot data - each point is a frame for a person with emotion color
  const scatterData = [];
  const people = Object.keys(emotionData).map(id => id.replace('person_', '')).sort((a, b) => parseInt(a) - parseInt(b));
  
  Object.entries(emotionData).forEach(([personId, data]) => {
    if (!data.frames || !Array.isArray(data.frames)) return;
    
    const personNum = parseInt(personId.replace('person_', ''));
    
    data.frames.forEach((frame, index) => {
      const frameNum = index + 1;
      const emotion = frame.emotion.toLowerCase();
      
      scatterData.push({
        frame: frameNum,
        person: personNum,
        emotion: emotion,
        color: EMOTION_COLORS[emotion] || '#607D8B'
      });
    });
  });
  
  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold' }}>Frame {data.frame}</p>
          <p style={{ margin: '4px 0', fontSize: '0.9em' }}>
            <span style={{ 
              color: data.color,
              fontWeight: 'bold'
            }}>
              Person {data.person}:
            </span> {data.emotion}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height: 400, marginTop: 20 }}>
      <ResponsiveContainer>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number"
            dataKey="frame" 
            name="Frame"
            label={{ value: 'Frame Number', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            type="number"
            dataKey="person"
            name="Person"
            label={{ value: 'Person', angle: -90, position: 'insideLeft' }}
            domain={[0, Math.max(...people.map(p => parseInt(p))) + 1]}
            ticks={people.map(p => parseInt(p))}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            payload={Object.keys(EMOTION_COLORS).map(emotion => ({
              value: emotion.charAt(0).toUpperCase() + emotion.slice(1),
              type: 'square',
              color: EMOTION_COLORS[emotion]
            }))}
          />
          <Scatter data={scatterData} shape="square">
            {scatterData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SummaryChart;
