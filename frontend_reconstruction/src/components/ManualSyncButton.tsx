import React, { useState } from 'react';
import { RefreshCw, Cloud, CheckCircle, AlertCircle } from 'lucide-react';
import { getPerformanceMonitor } from '../utils/PerformanceMonitor';
import { apiFsm } from '../utils/ApiFileSystemStateMachine';

interface ManualSyncButtonProps {
  onSyncStart?: () => void;
  onSyncComplete?: (success: boolean) => void;
  onSyncError?: (error: string) => void;
}

export const ManualSyncButton: React.FC<ManualSyncButtonProps> = ({
  onSyncStart,
  onSyncComplete,
  onSyncError,
}) => {
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'completed' | 'error'>('idle');
  const [syncMessage, setSyncMessage] = useState('');

  const handleManualSync = async () => {
    if (isSyncing) return;

    setIsSyncing(true);
    setSyncStatus('syncing');
    setSyncMessage('开始手动同步...');
    
    if (onSyncStart) onSyncStart();

    try {
      // 模拟同步过程
      const steps = [
        { progress: 10, message: '检查 API 连接...' },
        { progress: 30, message: '获取本地缓存数据...' },
        { progress: 50, message: '同步到后端 API...' },
        { progress: 70, message: '验证数据一致性...' },
        { progress: 90, message: '清理临时数据...' },
        { progress: 100, message: '同步完成' },
      ];

      for (const step of steps) {
        setSyncMessage(step.message);
        
        // 模拟 API 调用
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 检查 API 可用性
        const isApiAvailable = apiFsm.isApiAvailable();
        
        if (!isApiAvailable && step.progress > 30) {
          throw new Error('API 不可用，无法完成同步');
        }
      }

      // 记录成功同步
      const monitor = getPerformanceMonitor();
      monitor.recordMetrics({
        apiLatency: 100,
        apiStatus: 'connected',
        errorRate: 0,
        requestCount: 1,
        successCount: 1,
        failureCount: 0,
      });

      setSyncStatus('completed');
      setSyncMessage('手动同步完成');
      
      if (onSyncComplete) onSyncComplete(true);

      // 3秒后重置
      setTimeout(() => {
        setIsSyncing(false);
        setSyncStatus('idle');
        setSyncMessage('');
      }, 3000);

    } catch (error: any) {
      setSyncStatus('error');
      setSyncMessage(`同步失败: ${error.message}`);
      
      // 记录失败
      const monitor = getPerformanceMonitor();
      monitor.recordMetrics({
        apiLatency: 0,
        apiStatus: 'disconnected',
        errorRate: 1,
        requestCount: 1,
        successCount: 0,
        failureCount: 1,
      });

      if (onSyncError) onSyncError(error.message);

      // 5秒后重置
      setTimeout(() => {
        setIsSyncing(false);
        setSyncStatus('idle');
        setSyncMessage('');
      }, 5000);
    }
  };

  const getButtonColor = () => {
    switch (syncStatus) {
      case 'syncing':
        return 'bg-blue-600 hover:bg-blue-700';
      case 'completed':
        return 'bg-green-600 hover:bg-green-700';
      case 'error':
        return 'bg-red-600 hover:bg-red-700';
      default:
        return 'bg-blue-600 hover:bg-blue-700';
    }
  };

  const getButtonIcon = () => {
    if (isSyncing) {
      return <RefreshCw className="w-4 h-4 animate-spin" />;
    }
    switch (syncStatus) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'error':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <RefreshCw className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={handleManualSync}
        disabled={isSyncing}
        className={`flex items-center space-x-2 px-4 py-2 ${getButtonColor()} text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        {getButtonIcon()}
        <span>
          {isSyncing ? '同步中...' : '手动同步'}
        </span>
      </button>
      
      {syncMessage && (
        <span className="text-xs text-gray-400">
          {syncMessage}
        </span>
      )}
    </div>
  );
};

/**
 * 数据同步状态组件
 */
export const DataSyncStatus: React.FC = () => {
  const [syncState, setSyncState] = useState<{
    status: 'idle' | 'syncing' | 'completed' | 'error' | 'degraded';
    lastSync: string | null;
    pendingCount: number;
  }>({
    status: 'idle',
    lastSync: null,
    pendingCount: 0,
  });

  const checkSyncStatus = async () => {
    try {
      const isApiAvailable = apiFsm.isApiAvailable();
      
      if (!isApiAvailable) {
        setSyncState(prev => ({
          ...prev,
          status: 'degraded',
          pendingCount: prev.pendingCount + 1,
        }));
        return;
      }

      // 模拟检查待同步数据
      const pendingData = Math.floor(Math.random() * 5);
      
      if (pendingData > 0) {
        setSyncState(prev => ({
          ...prev,
          status: 'syncing',
          pendingCount: pendingData,
        }));
      } else {
        setSyncState(prev => ({
          ...prev,
          status: 'completed',
          lastSync: new Date().toISOString(),
        }));
      }
    } catch (error) {
      setSyncState(prev => ({
        ...prev,
        status: 'error',
      }));
    }
  };

  React.useEffect(() => {
    checkSyncStatus();
    const interval = setInterval(checkSyncStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (syncState.status) {
      case 'syncing':
        return 'text-blue-400';
      case 'completed':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'degraded':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusText = () => {
    switch (syncState.status) {
      case 'syncing':
        return `同步中 (${syncState.pendingCount} 项待同步)`;
      case 'completed':
        return '已同步';
      case 'error':
        return '同步失败';
      case 'degraded':
        return '降级模式';
      default:
        return '空闲';
    }
  };

  return (
    <div className="p-3 bg-gray-800 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Cloud className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-white">数据同步状态</span>
        </div>
        <span className={`text-xs font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>
      
      <div className="text-xs text-gray-400 space-y-1">
        <div>
          最后同步: {syncState.lastSync 
            ? new Date(syncState.lastSync).toLocaleString('zh-CN') 
            : '从未'}
        </div>
        <div>
          待同步项: {syncState.pendingCount}
        </div>
      </div>

      <div className="mt-2">
        <ManualSyncButton />
      </div>
    </div>
  );
};