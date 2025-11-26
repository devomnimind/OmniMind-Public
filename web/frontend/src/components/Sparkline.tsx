import React from 'react';

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  min?: number;
  max?: number;
}

export const Sparkline: React.FC<SparklineProps> = ({
  data,
  width = 100,
  height = 30,
  color = '#4ade80',
  min = 0,
  max = 100
}) => {
  if (data.length < 2) return null;

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * width;
    const normalizedVal = Math.max(min, Math.min(max, val));
    const y = height - ((normalizedVal - min) / (max - min)) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};
