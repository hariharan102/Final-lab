/**
 * EmotionChart Component
 * 
 * Displays emotion variation over time as line charts.
 * X-axis: Time (timestamp), Y-axis: Percentage (0-100)
 * Each emotion has its own colored line.
 */

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

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

function EmotionChart({ emotions, frames }) {
  if (!frames || !Array.isArray(frames) || frames.length === 0) {
    return <p>No timeline data to display</p>;
  }

  // Sort frames by timestamp
  const sortedFrames = [...frames].sort((a, b) => a.timestamp - b.timestamp);
  
  // Smoothing function - moving average
  const smoothData = (data, windowSize = 5) => {
    const smoothed = [];
    for (let i = 0; i < data.length; i++) {
      const start = Math.max(0, i - Math.floor(windowSize / 2));
      const end = Math.min(data.length, i + Math.ceil(windowSize / 2));
      const window = data.slice(start, end);
      
      const avg = {};
      Object.keys(EMOTION_COLORS).forEach(emotion => {
        const sum = window.reduce((acc, item) => acc + (item[emotion] || 0), 0);
        avg[emotion] = sum / window.length;
      });
      
      smoothed.push({
        ...data[i],
        ...avg
      });
    }
    return smoothed;
  };
  
  // Create timeline data with emotion scores at each frame
  const timelineData = sortedFrames.map((frame, index) => {
    const dataPoint = {
      frame: index + 1,
      time: parseFloat(frame.timestamp).toFixed(2),
      timestamp: parseFloat(frame.timestamp)
    };
    
    // Initialize all emotions to 0
    Object.keys(EMOTION_COLORS).forEach(emotion => {
      dataPoint[emotion] = 0;
    });
    
    // Use all emotion scores from the frame
    if (frame.all_emotions && typeof frame.all_emotions === 'object') {
      Object.entries(frame.all_emotions).forEach(([emotion, score]) => {
        const emotionKey = emotion.toLowerCase();
        if (EMOTION_COLORS[emotionKey]) {
          dataPoint[emotionKey] = parseFloat(score) || 0;
        }
      });
    } else if (frame.emotion && frame.confidence) {
      // Fallback: if no all_emotions, show confidence for dominant emotion
      const emotionKey = frame.emotion.toLowerCase();
      if (EMOTION_COLORS[emotionKey]) {
        dataPoint[emotionKey] = parseFloat(frame.confidence) || 0;
      }
    }
    
    return dataPoint;
  });
  
  // Apply smoothing to reduce jaggedness
  const smoothedData = smoothData(timelineData, 5);
  
  // Only show emotions that appear as dominant in the summary
  // This prevents showing negligible emotion scores as lines
  const activeEmotions = Object.keys(emotions || {});

  return (
    <div style={{ width: '100%', height: 350, marginTop: 20 }}>
      <ResponsiveContainer>
        <LineChart data={smoothedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="frame" 
            label={{ value: 'Frame Number', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }}
            domain={[0, 100]}
          />
          <Tooltip />
          <Legend />
          {activeEmotions.map(emotion => (
            <Line 
              key={emotion}
              type="natural" 
              dataKey={emotion} 
              stroke={EMOTION_COLORS[emotion] || '#607D8B'}
              strokeWidth={2.5}
              dot={false}
              name={emotion.charAt(0).toUpperCase() + emotion.slice(1)}
              animationDuration={300}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default EmotionChart;
