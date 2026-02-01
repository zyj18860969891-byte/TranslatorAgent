import React, { useState, useEffect, useRef } from 'react';
import { getPerformanceMonitor, PerformanceMetrics } from '../utils/PerformanceMonitor';

interface PerformanceChartProps {
  width?: number;
  height?: number;
  showLegend?: boolean;
  refreshInterval?: number;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
  width = 400,
  height = 200,
  showLegend = true,
  refreshInterval = 1000,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [metricsHistory, setMetricsHistory] = useState<PerformanceMetrics[]>([]);

  useEffect(() => {
    const monitor = getPerformanceMonitor();
    
    // 定期更新图表数据
    const interval = setInterval(() => {
      const history = monitor.getMetricsHistory(30); // 最近30个样本
      setMetricsHistory(history);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  useEffect(() => {
    if (!canvasRef.current || metricsHistory.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 清空画布
    ctx.clearRect(0, 0, width, height);

    // 绘制背景
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, width, height);

    // 绘制网格
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;
    
    // 水平网格线
    for (let i = 0; i <= 4; i++) {
      const y = (height / 4) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // 垂直网格线
    for (let i = 0; i <= 6; i++) {
      const x = (width / 6) * i;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    if (metricsHistory.length < 2) return;

    // 计算最大值（用于缩放）
    const maxLatency = Math.max(...metricsHistory.map(m => m.apiLatency), 1000);
    const maxErrorRate = 1; // 100%

    // 绘制延迟曲线
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();

    metricsHistory.forEach((metric, index) => {
      const x = (width / (metricsHistory.length - 1)) * index;
      const y = height - (metric.apiLatency / maxLatency) * height;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // 绘制错误率曲线
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();

    metricsHistory.forEach((metric, index) => {
      const x = (width / (metricsHistory.length - 1)) * index;
      const y = height - (metric.errorRate / maxErrorRate) * height;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // 绘制成功率曲线（使用右Y轴）
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2;
    ctx.beginPath();

    metricsHistory.forEach((metric, index) => {
      const x = (width / (metricsHistory.length - 1)) * index;
      const total = metric.requestCount;
      const successRate = total > 0 ? metric.successCount / total : 1;
      const y = height - successRate * height;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // 绘制图例
    if (showLegend) {
      const legendY = height - 20;
      const legendX = 10;
      const itemWidth = 80;

      // 延迟图例
      ctx.fillStyle = '#3b82f6';
      ctx.fillRect(legendX, legendY, 15, 3);
      ctx.fillStyle = '#e5e7eb';
      ctx.font = '10px sans-serif';
      ctx.fillText('延迟', legendX + 20, legendY + 8);

      // 错误率图例
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(legendX + itemWidth, legendY, 15, 3);
      ctx.fillStyle = '#e5e7eb';
      ctx.fillText('错误率', legendX + itemWidth + 20, legendY + 8);

      // 成功率图例
      ctx.fillStyle = '#10b981';
      ctx.fillRect(legendX + itemWidth * 2, legendY, 15, 3);
      ctx.fillStyle = '#e5e7eb';
      ctx.fillText('成功率', legendX + itemWidth * 2 + 20, legendY + 8);
    }

    // 绘制坐标轴标签
    ctx.fillStyle = '#9ca3af';
    ctx.font = '10px sans-serif';
    
    // Y轴标签（左侧）
    ctx.fillText('0', 2, height - 2);
    ctx.fillText(maxLatency.toFixed(0) + 'ms', 2, 10);

    // X轴标签（时间）
    if (metricsHistory.length > 0) {
      const firstTime = new Date(metricsHistory[0].timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      const lastTime = new Date(metricsHistory[metricsHistory.length - 1].timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      ctx.fillText(firstTime, 5, height - 5);
      ctx.fillText(lastTime, width - 40, height - 5);
    }
  }, [metricsHistory, width, height, showLegend]);

  return (
    <div className="p-3 bg-gray-800 rounded-lg">
      <div className="text-xs text-gray-300 mb-2">性能趋势图</div>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="rounded"
      />
      <div className="text-xs text-gray-500 mt-1">
        蓝色: 延迟 | 红色: 错误率 | 绿色: 成功率
      </div>
    </div>
  );
};

/**
 * 统计卡片组件
 */
export const StatsCard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const monitor = getPerformanceMonitor();
    
    const interval = setInterval(() => {
      setStats(monitor.getStats());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!stats) {
    return null;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="p-3 bg-gray-800 rounded-lg">
        <div className="text-xs text-gray-400">平均延迟</div>
        <div className="text-xl font-bold text-blue-400">
          {stats.avgLatency.toFixed(0)}ms
        </div>
      </div>
      <div className="p-3 bg-gray-800 rounded-lg">
        <div className="text-xs text-gray-400">错误率</div>
        <div className="text-xl font-bold text-red-400">
          {(stats.errorRate * 100).toFixed(1)}%
        </div>
      </div>
      <div className="p-3 bg-gray-800 rounded-lg">
        <div className="text-xs text-gray-400">成功率</div>
        <div className="text-xl font-bold text-green-400">
          {(stats.successRate * 100).toFixed(1)}%
        </div>
      </div>
      <div className="p-3 bg-gray-800 rounded-lg">
        <div className="text-xs text-gray-400">未确认告警</div>
        <div className="text-xl font-bold text-yellow-400">
          {stats.unacknowledgedAlerts}
        </div>
      </div>
    </div>
  );
};

/**
 * 实时监控面板组件
 */
export const RealTimeMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [history, setHistory] = useState<PerformanceMetrics[]>([]);

  useEffect(() => {
    const monitor = getPerformanceMonitor();
    
    const interval = setInterval(() => {
      const recent = monitor.getMetricsHistory(1);
      if (recent.length > 0) {
        setMetrics(recent[0]);
      }
      setHistory(monitor.getMetricsHistory(10));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg text-center text-gray-400">
        等待性能数据...
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'text-green-400';
      case 'disconnected':
        return 'text-red-400';
      case 'degraded':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-4">
      {/* 当前状态 */}
      <div className="p-4 bg-gray-800 rounded-lg">
        <div className="text-sm text-gray-400 mb-2">当前状态</div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-500">API 状态</div>
            <div className={`text-lg font-bold ${getStatusColor(metrics.apiStatus)}`}>
              {metrics.apiStatus}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">延迟</div>
            <div className="text-lg font-bold text-blue-400">
              {metrics.apiLatency.toFixed(0)}ms
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">错误率</div>
            <div className="text-lg font-bold text-red-400">
              {(metrics.errorRate * 100).toFixed(1)}%
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">请求总数</div>
            <div className="text-lg font-bold text-white">
              {metrics.requestCount}
            </div>
          </div>
        </div>
      </div>

      {/* 历史趋势 */}
      <div className="p-4 bg-gray-800 rounded-lg">
        <div className="text-sm text-gray-400 mb-2">最近10次请求</div>
        <div className="space-y-1 max-h-40 overflow-y-auto">
          {history.map((metric, index) => (
            <div key={index} className="flex justify-between text-xs text-gray-300 p-1 bg-gray-700 rounded">
              <span>{new Date(metric.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
              <span className={metric.apiStatus === 'connected' ? 'text-green-400' : 'text-red-400'}>
                {metric.apiStatus}
              </span>
              <span className="text-blue-400">{metric.apiLatency.toFixed(0)}ms</span>
              <span className="text-red-400">{(metric.errorRate * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};