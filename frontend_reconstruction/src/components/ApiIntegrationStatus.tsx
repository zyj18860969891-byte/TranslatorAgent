import React, { useState, useEffect } from 'react';
import { checkApiHealth, getApiLatency, getApiConfig } from '../utils/apiClient';
import { apiFsm } from '../utils/ApiFileSystemStateMachine';

export const ApiIntegrationStatus: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [apiLatency, setApiLatency] = useState<number>(0);
  const [fsmStatus, setFsmStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [taskStats, setTaskStats] = useState<any>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [apiConfig, setApiConfig] = useState<any>(null);

  useEffect(() => {
    // 获取 API 配置
    const config = getApiConfig();
    setApiConfig(config);

    checkApiStatus();
    checkFsmStatus();
    loadTaskStats();
    
    const interval = setInterval(() => {
      checkApiStatus();
      loadTaskStats();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const checkApiStatus = async () => {
    try {
      const isHealthy = await checkApiHealth();
      const latency = await getApiLatency();
      
      setApiLatency(latency);
      setApiStatus(isHealthy ? 'connected' : 'disconnected');
    } catch (error) {
      setApiStatus('disconnected');
      setApiLatency(0);
    }
  };

  const checkFsmStatus = async () => {
    try {
      // 检查API FSM是否可用
      const isAvailable = apiFsm.isApiAvailable();
      setFsmStatus(isAvailable ? 'connected' : 'disconnected');
    } catch (error) {
      setFsmStatus('disconnected');
    }
  };

  const loadTaskStats = async () => {
    try {
      const stats = await apiFsm.getTaskStats();
      setTaskStats(stats);
    } catch (error) {
      console.error('Failed to load task stats:', error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await checkApiStatus();
    await checkFsmStatus();
    await loadTaskStats();
    setIsRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-500';
      case 'disconnected': return 'bg-red-500';
      case 'checking': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'connected': return '已连接';
      case 'disconnected': return '未连接';
      case 'checking': return '检查中';
      default: return '未知';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">API 集成状态</h3>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm transition-colors"
        >
          {isRefreshing ? '刷新中...' : '刷新状态'}
        </button>
      </div>

      {/* Current task info placeholder - removed due to context dependency */}

      <div className="space-y-3">
        {/* API 配置信息 */}
        {apiConfig && (
          <div className="p-2 bg-gray-700 rounded">
            <div className="text-xs text-gray-400 mb-2">API 配置</div>
            <div className="text-xs text-gray-300 space-y-1">
              <div>地址: {apiConfig.baseUrl}</div>
              <div>版本: {apiConfig.version}</div>
              <div>超时: {apiConfig.timeout}ms</div>
              <div>重试: {apiConfig.retryCount}次</div>
            </div>
          </div>
        )}

        {/* API 状态 */}
        <div className="flex items-center justify-between p-2 bg-gray-700 rounded">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(apiStatus)}`} />
            <div>
              <div className="text-sm font-medium text-white">后端 API</div>
              <div className="text-xs text-gray-400">
                {apiStatus === 'connected' ? `延迟: ${apiLatency.toFixed(0)}ms` : '无法连接'}
              </div>
            </div>
          </div>
          <div className="text-xs">
            <span className={`px-2 py-1 rounded ${
              apiStatus === 'connected' ? 'bg-green-900 text-green-300' :
              apiStatus === 'disconnected' ? 'bg-red-900 text-red-300' :
              'bg-blue-900 text-blue-300'
            }`}>
              {getStatusText(apiStatus)}
            </span>
          </div>
        </div>

        {/* FSM 状态 */}
        <div className="flex items-center justify-between p-2 bg-gray-700 rounded">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(fsmStatus)}`} />
            <div>
              <div className="text-sm font-medium text-white">API 文件系统状态机</div>
              <div className="text-xs text-gray-400">
                {fsmStatus === 'connected' ? '正常运行' : '无法访问'}
              </div>
            </div>
          </div>
          <div className="text-xs">
            <span className={`px-2 py-1 rounded ${
              fsmStatus === 'connected' ? 'bg-green-900 text-green-300' :
              fsmStatus === 'disconnected' ? 'bg-red-900 text-red-300' :
              'bg-blue-900 text-blue-300'
            }`}>
              {getStatusText(fsmStatus)}
            </span>
          </div>
        </div>

        {/* 任务统计 */}
        {taskStats && (
          <div className="mt-4 p-2 bg-gray-700 rounded">
            <div className="text-sm font-medium text-white mb-2">任务统计</div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-gray-600 p-2 rounded">
                <div className="text-gray-300">总任务数</div>
                <div className="text-white font-bold">{taskStats.total || 0}</div>
              </div>
              <div className="bg-gray-600 p-2 rounded">
                <div className="text-gray-300">运行中</div>
                <div className="text-blue-400 font-bold">{taskStats.byStatus?.processing || 0}</div>
              </div>
              <div className="bg-gray-600 p-2 rounded">
                <div className="text-gray-300">已完成</div>
                <div className="text-green-400 font-bold">{taskStats.byStatus?.completed || 0}</div>
              </div>
              <div className="bg-gray-600 p-2 rounded">
                <div className="text-gray-300">失败</div>
                <div className="text-red-400 font-bold">{taskStats.byStatus?.error || 0}</div>
              </div>
            </div>
          </div>
        )}

        {/* 集成模式 */}
        <div className="mt-4 p-2 bg-gray-700 rounded">
          <div className="text-sm font-medium text-white mb-2">集成模式</div>
          <div className="text-xs text-gray-400 space-y-1">
            <div className="flex items-center justify-between">
              <span>主模式:</span>
              <span className="text-blue-400">API 文件系统状态机</span>
            </div>
            <div className="flex items-center justify-between">
              <span>备用模式:</span>
              <span className="text-yellow-400">本地文件系统状态机</span>
            </div>
            <div className="flex items-center justify-between">
              <span>状态:</span>
              <span className={apiStatus === 'connected' ? 'text-green-400' : 'text-yellow-400'}>
                {apiStatus === 'connected' ? 'API 优先' : '降级到本地'}
              </span>
            </div>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="mt-4 flex gap-2">
          <button
            onClick={checkApiStatus}
            className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors"
          >
            测试 API 连接
          </button>
          <button
            onClick={checkFsmStatus}
            className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
          >
            测试 FSM 连接
          </button>
        </div>
      </div>

      {/* 说明 */}
      <div className="mt-4 p-3 bg-gray-700 rounded text-xs text-gray-300">
        <div className="font-medium mb-1">集成说明:</div>
        <ul className="space-y-1 list-disc list-inside">
          <li>系统优先使用后端 API 进行数据存储</li>
          <li>API 不可用时自动降级到本地存储</li>
          <li>所有操作都会同步到主备两个存储</li>
          <li>确保数据的高可用性和一致性</li>
        </ul>
      </div>
    </div>
  );
};