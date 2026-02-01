import React, { useState, useEffect } from 'react';
import { getPerformanceMonitor, Alert, PerformanceMetrics } from '../utils/PerformanceMonitor';

interface PerformanceAlertProps {
  autoHide?: boolean;
  hideDelay?: number;
  maxVisible?: number;
}

export const PerformanceAlert: React.FC<PerformanceAlertProps> = ({
  autoHide = true,
  hideDelay = 5000,
  maxVisible = 3,
}) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    const monitor = getPerformanceMonitor();
    
    // 监听新告警
    const handleAlert = (alert: Alert) => {
      setAlerts(prev => {
        const newAlerts = [alert, ...prev].slice(0, maxVisible);
        
        // 自动隐藏
        if (autoHide) {
          setTimeout(() => {
            setAlerts(prevAlerts => prevAlerts.filter(a => a.id !== alert.id));
          }, hideDelay);
        }
        
        return newAlerts;
      });
    };

    monitor.addListener(handleAlert);

    return () => {
      monitor.removeListener(handleAlert);
    };
  }, [autoHide, hideDelay, maxVisible]);

  const handleAcknowledge = (alertId: string) => {
    const monitor = getPerformanceMonitor();
    monitor.acknowledgeAlert(alertId);
    setAlerts(prev => prev.filter(a => a.id !== alertId));
  };

  const handleClearAll = () => {
    const monitor = getPerformanceMonitor();
    monitor.clearAllAlerts();
    setAlerts([]);
  };

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'info':
        return 'bg-blue-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      case 'critical':
        return 'bg-red-600 animate-pulse';
      default:
        return 'bg-gray-500';
    }
  };

  const getSeverityIcon = (severity: Alert['severity']) => {
    switch (severity) {
      case 'info':
        return 'ℹ️';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'critical':
        return '🚨';
      default:
        return '🔔';
    }
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {/* 控制栏 */}
      <div className="flex justify-end space-x-2 mb-2">
        <button
          onClick={() => setIsMinimized(!isMinimized)}
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded transition-colors"
        >
          {isMinimized ? '展开' : '最小化'}
        </button>
        <button
          onClick={handleClearAll}
          className="px-3 py-1 bg-red-700 hover:bg-red-600 text-white text-xs rounded transition-colors"
        >
          清除全部
        </button>
      </div>

      {/* 告警列表 */}
      <div className={`space-y-2 transition-all duration-300 ${isMinimized ? 'max-h-0 overflow-hidden' : 'max-h-96 overflow-y-auto'}`}>
        {alerts.map(alert => (
          <div
            key={alert.id}
            className={`p-3 rounded-lg shadow-lg border-l-4 ${getSeverityColor(alert.severity)} bg-gray-800 text-white min-w-80`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-lg">{getSeverityIcon(alert.severity)}</span>
                  <span className="font-semibold text-sm">
                    [{alert.severity.toUpperCase()}] {alert.message}
                  </span>
                </div>
                <div className="text-xs text-gray-300 space-y-1">
                  <div>时间: {formatTime(alert.timestamp)}</div>
                  <div>延迟: {alert.metrics.apiLatency.toFixed(0)}ms</div>
                  <div>错误率: {(alert.metrics.errorRate * 100).toFixed(1)}%</div>
                  <div>状态: {alert.metrics.apiStatus}</div>
                </div>
              </div>
              <button
                onClick={() => handleAcknowledge(alert.id)}
                className="ml-2 px-2 py-1 bg-gray-600 hover:bg-gray-500 text-white text-xs rounded transition-colors"
              >
                确认
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 统计信息 */}
      {!isMinimized && (
        <div className="p-2 bg-gray-800 rounded-lg text-xs text-gray-300">
          <div className="flex justify-between">
            <span>活跃告警: {alerts.length}</span>
            <span>总计: {getPerformanceMonitor().getStats().totalAlerts}</span>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * 性能指标显示组件
 */
export const PerformanceMetricsDisplay: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const monitor = getPerformanceMonitor();
    
    // 定期更新显示
    const interval = setInterval(() => {
      const history = monitor.getMetricsHistory(1);
      if (history.length > 0) {
        setMetrics(history[0]);
      }
      setStats(monitor.getStats());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return null;
  }

  const getLatencyColor = (latency: number) => {
    if (latency < 200) return 'text-green-400';
    if (latency < 1000) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getErrorRateColor = (rate: number) => {
    if (rate < 0.1) return 'text-green-400';
    if (rate < 0.3) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate > 0.9) return 'text-green-400';
    if (rate > 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="p-3 bg-gray-800 rounded-lg text-xs text-gray-300 space-y-2">
      <div className="font-semibold text-white mb-2">实时性能指标</div>
      
      <div className="grid grid-cols-2 gap-2">
        <div>
          <span className="text-gray-400">延迟:</span>
          <span className={`ml-1 font-mono ${getLatencyColor(metrics.apiLatency)}`}>
            {metrics.apiLatency.toFixed(0)}ms
          </span>
        </div>
        <div>
          <span className="text-gray-400">状态:</span>
          <span className={`ml-1 font-mono ${
            metrics.apiStatus === 'connected' ? 'text-green-400' :
            metrics.apiStatus === 'disconnected' ? 'text-red-400' :
            'text-yellow-400'
          }`}>
            {metrics.apiStatus}
          </span>
        </div>
        <div>
          <span className="text-gray-400">错误率:</span>
          <span className={`ml-1 font-mono ${getErrorRateColor(metrics.errorRate)}`}>
            {(metrics.errorRate * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <span className="text-gray-400">请求:</span>
          <span className="ml-1 font-mono text-white">{metrics.requestCount}</span>
        </div>
      </div>

      {stats && (
        <div className="pt-2 border-t border-gray-700">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-gray-400">成功率:</span>
              <span className={`ml-1 font-mono ${getSuccessRateColor(stats.successRate)}`}>
                {(stats.successRate * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-gray-400">告警:</span>
              <span className="ml-1 font-mono text-white">{stats.unacknowledgedAlerts}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};