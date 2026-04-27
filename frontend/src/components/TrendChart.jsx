import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const EMOTION_TO_SCORE = {
  joy: 5,
  neutral: 3,
  sadness: 2,
  fear: 1,
  anger: 1,
};

export default function TrendChart({ latestEmotions }) {
  const data = latestEmotions.map((entry, index) => ({
    idx: index + 1,
    moodScore: EMOTION_TO_SCORE[entry.emotion] || 3,
  }));

  return (
    <div className="trend-card">
      <h3>Emotion Trend</h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d8d6ff" />
          <XAxis dataKey="idx" />
          <YAxis domain={[1, 5]} />
          <Tooltip />
          <Line type="monotone" dataKey="moodScore" stroke="#5e60ce" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
