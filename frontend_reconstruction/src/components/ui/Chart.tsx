import * as React from 'react';

interface ChartProps {
  type: 'bar' | 'line' | 'pie';
  data: any[];
  options?: {
    width?: number;
    height?: number;
    colors?: string[];
    title?: string;
  };
  className?: string;
}

const Chart: React.FC<ChartProps> = ({ type, data, options, className }) => {
  const { width = 400, height = 200, colors = ['#0ea5e9'], title } = options || {};

  // 简单的柱状图实现
  if (type === 'bar') {
    const maxValue = Math.max(...data.map(d => d.value || 0));
    
    return (
      <div className={className}>
        {title && <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">{title}</h3>}
        <div className="flex items-end gap-2" style={{ height: `${height}px` }}>
          {data.map((item, index) => {
            const value = item.value || 0;
            const barHeight = (value / maxValue) * (height - 20);
            const color = colors[index % colors.length];
            
            return (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div
                  className="w-full rounded-t transition-all duration-300"
                  style={{ height: `${barHeight}px`, backgroundColor: color }}
                />
                <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 text-center">
                  {item.label || value}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // 简单的折线图实现
  if (type === 'line') {
    const maxValue = Math.max(...data.map(d => d.value || 0));
    const minValue = Math.min(...data.map(d => d.value || 0));
    const range = maxValue - minValue || 1;
    
    const points = data.map((item, index) => {
      const x = (index / (data.length - 1)) * (width - 40) + 20;
      const y = height - 20 - ((item.value - minValue) / range) * (height - 40);
      return `${x},${y}`;
    }).join(' ');

    return (
      <div className={className}>
        {title && <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">{title}</h3>}
        <svg width={width} height={height} className="overflow-visible">
          <polyline
            fill="none"
            stroke={colors[0]}
            strokeWidth="2"
            points={points}
          />
          {data.map((item, index) => {
            const x = (index / (data.length - 1)) * (width - 40) + 20;
            const y = height - 20 - ((item.value - minValue) / range) * (height - 40);
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="4"
                fill={colors[0]}
              />
            );
          })}
        </svg>
      </div>
    );
  }

  // 简单的饼图实现
  if (type === 'pie') {
    const total = data.reduce((sum, item) => sum + (item.value || 0), 0);
    
    return (
      <div className={className}>
        {title && <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">{title}</h3>}
        <div className="flex items-center justify-center">
          <svg width={height} height={height} className="transform -rotate-90">
            {data.map((item, index) => {
              const value = item.value || 0;
              const percentage = (value / total) * 100;
              const color = colors[index % colors.length];
              
              return (
                <circle
                  key={index}
                  cx={height / 2}
                  cy={height / 2}
                  r={height / 2 - 10}
                  fill="none"
                  stroke={color}
                  strokeWidth="20"
                  strokeDasharray={`${(percentage / 100) * 2 * Math.PI * (height / 2 - 10)} ${2 * Math.PI * (height / 2 - 10)}`}
                />
              );
            })}
          </svg>
        </div>
      </div>
    );
  }

  return null;
};

export { Chart };