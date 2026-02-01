import React, { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface SyncProgressProps {
  status: 'idle' | 'syncing' | 'completed' | 'error' | 'degraded';
  progress: number;
  message: string;
  onManualSync?: () => void;
  onRetry?: () => void;
}

export const SyncProgress: React.FC<SyncProgressProps> = ({
  status,
  progress,
  message,
  onManualSync,
  onRetry,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (status !== 'idle') {
      setIsVisible(true);
    }
  }, [status]);

  const getStatusColor = () => {
    switch (status) {
      case 'syncing':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'degraded':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'syncing':
        return <RefreshCw className="w-4 h-4 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'error':
        return <AlertCircle className="w-4 h-4" />;
      case 'degraded':
        return <Clock className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'syncing':
        return '同步中...';
      case 'completed':
        return '同步完成';
      case 'error':
        return '同步失败';
      case 'degraded':
        return '降级模式';
      default:
        return '空闲';
    }
  };

  if (!isVisible && status === 'idle') {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className="p-3 bg-gray-800 rounded-lg shadow-lg border border-gray-700 min-w-80">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className={`p-1 rounded ${getStatusColor()}`}>
              {getStatusIcon()}
            </div>
            <span className="text-sm font-medium text-white">
              {getStatusText()}
            </span>
          </div>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-400 hover:text-white text-xs"
          >
            ✕
          </button>
        </div>

        {/* 进度条 */}
        {status === 'syncing' && (
          <div className="mb-2">
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${getStatusColor()}`} 
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="text-xs text-gray-400 mt-1 text-right">
              {progress}%
            </div>
          </div>
        )}

        {/* 消息 */}
        <div className="text-xs text-gray-300 mb-2">
          {message}
        </div>

        {/* 操作按钮 */}
        <div className="flex space-x-2">
          {status === 'error' && onRetry && (
            <button
              onClick={onRetry}
              className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
            >
              重试
            </button>
          )}
          {status !== 'syncing' && onManualSync && (
            <button
              onClick={onManualSync}
              className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
            >
              手动同步
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * 同步状态指示器组件
 */
export const SyncStatusIndicator: React.FC = () => {
  const [status, setStatus] = useState<'idle' | 'syncing' | 'completed' | 'error' | 'degraded'>('idle');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // 模拟同步过程
    const simulateSync = () => {
      setStatus('syncing');
      setProgress(0);
      setMessage('正在检查数据...');

      let currentProgress = 0;
      const interval = setInterval(() => {
        currentProgress += 10;
        setProgress(currentProgress);

        if (currentProgress < 30) {
          setMessage('正在检查数据...');
        } else if (currentProgress < 60) {
          setMessage('正在同步数据...');
        } else if (currentProgress < 90) {
          setMessage('正在验证数据...');
        } else {
          setMessage('即将完成...');
        }

        if (currentProgress >= 100) {
          clearInterval(interval);
          setStatus('completed');
          setMessage('数据同步完成');
          
          // 3秒后隐藏
          setTimeout(() => {
            setStatus('idle');
          }, 3000);
        }
      }, 200);
    };

    // 每30秒自动同步一次
    const interval = setInterval(simulateSync, 30000);
    
    // 立即执行一次
    simulateSync();

    return () => clearInterval(interval);
  }, []);

  const handleManualSync = () => {
    setStatus('syncing');
    setProgress(0);
    setMessage('手动同步开始...');

    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += 15;
      setProgress(currentProgress);

      if (currentProgress < 40) {
        setMessage('正在准备同步...');
      } else if (currentProgress < 80) {
        setMessage('正在同步数据...');
      } else {
        setMessage('正在完成...');
      }

      if (currentProgress >= 100) {
        clearInterval(interval);
        setStatus('completed');
        setMessage('手动同步完成');
        
        setTimeout(() => {
          setStatus('idle');
        }, 3000);
      }
    }, 150);
  };

  const handleRetry = () => {
    handleManualSync();
  };

  return (
    <SyncProgress
      status={status}
      progress={progress}
      message={message}
      onManualSync={handleManualSync}
      onRetry={handleRetry}
    />
  );
};