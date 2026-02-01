import React, { useState, useEffect } from 'react';
import { 
  Cloud,
  Database,
  Activity,
  RefreshCw,
  Server,
  Link,
  Shield,
  Cpu,
  AlertTriangle,
  BarChart2,
  Clock,
  TrendingUp,
  Download
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { getApiLatency } from '../utils/apiClient';
import { apiFsm } from '../utils/ApiFileSystemStateMachine';
import { ApiIntegrationStatus } from '../components/ApiIntegrationStatus';
import { 
  PerformanceMetricsDisplay,
} from '../components/PerformanceAlert';
import { 
  PerformanceChart, 
  StatsCard, 
  RealTimeMonitor 
} from '../components/PerformanceChart';
import { getPerformanceMonitor } from '../utils/PerformanceMonitor';
import { DataSyncStatus, ManualSyncButton } from '../components/ManualSyncButton';
import { ErrorHistory, useErrorHandler, EnhancedErrorDisplay } from '../components/EnhancedErrorDisplay';
import { SyncStatusIndicator } from '../components/SyncProgress';
import { PerformanceAlert } from '../components/PerformanceAlert';

interface ApiIntegrationPageProps {
  onBack: () => void;
}

export const ApiIntegrationPage: React.FC<ApiIntegrationPageProps> = ({
  onBack
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'endpoints' | 'monitoring' | 'settings'>('overview');
  const [apiHealth, setApiHealth] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [apiLatency, setApiLatency] = useState<number>(0);
  const [serviceStats, setServiceStats] = useState<any>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // 使用错误处理钩子
  const { currentError, handleError, dismissError } = useErrorHandler();

  useEffect(() => {
    // 初始化性能监控器
    const monitor = getPerformanceMonitor();
    monitor.start();

    checkApiHealth();
    loadServiceStats();
    
    const interval = setInterval(() => {
      checkApiHealth();
      loadServiceStats();
    }, 30000);

    return () => {
      clearInterval(interval);
      // 注意：不要在这里停止监控器，因为它可能在其他地方使用
    };
  }, []);

  const checkApiHealth = async () => {
    try {
      const latency = await getApiLatency();
      const isHealthy = latency >= 0;
      
      setApiLatency(latency);
      setApiHealth(isHealthy ? 'healthy' : 'unhealthy');

      // 记录到性能监控器
      const monitor = getPerformanceMonitor();
      monitor.recordMetrics({
        apiLatency: latency,
        apiStatus: isHealthy ? 'connected' : 'disconnected',
        errorRate: isHealthy ? 0 : 1,
        requestCount: 1,
        successCount: isHealthy ? 1 : 0,
        failureCount: isHealthy ? 0 : 1,
      });

      // 如果 API 不可用，记录错误
      if (!isHealthy) {
        handleError({
          code: 'API_UNAVAILABLE',
          message: 'API 连接失败',
          details: '无法连接到后端 API 服务',
          suggestion: '请检查后端 API 服务是否正在运行，网络连接是否正常',
          documentation: 'https://github.com/your-repo/translator-agent#api-configuration',
        });
      }
    } catch (error: any) {
      setApiHealth('unhealthy');
      setApiLatency(0);
      
      handleError({
        code: 'API_CHECK_FAILED',
        message: 'API 健康检查失败',
        details: error.message,
        suggestion: '请检查网络连接和 API 配置',
        documentation: 'https://github.com/your-repo/translator-agent#troubleshooting',
      });
    }
  };

  const loadServiceStats = async () => {
    try {
      const stats = await apiFsm.getTaskStats();
      setServiceStats(stats);
    } catch (error: any) {
      console.error('Failed to load service stats:', error);
      
      handleError({
        code: 'STATS_LOAD_FAILED',
        message: '服务统计加载失败',
        details: error.message,
        suggestion: '请检查 API 连接状态',
      });
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await checkApiHealth();
    await loadServiceStats();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const getHealthStatus = () => {
    switch (apiHealth) {
      case 'healthy': return { color: 'text-green-500', label: '健康' };
      case 'unhealthy': return { color: 'text-red-500', label: '异常' };
      default: return { color: 'text-blue-500', label: '检查中' };
    }
  };

  const healthStatus = getHealthStatus();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      {/* 性能告警组件 */}
      <PerformanceAlert autoHide={true} hideDelay={5000} maxVisible={3} />
      
      {/* 同步状态指示器 */}
      <SyncStatusIndicator />
      
      {/* 错误显示组件 */}
      {currentError && (
        <EnhancedErrorDisplay
          error={currentError}
          onDismiss={dismissError}
          onRetry={checkApiHealth}
        />
      )}

      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Cloud className="w-6 h-6" />
              API 集成监控
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              实时监控后端 API 连接状态和数据同步情况
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleRefresh} disabled={isRefreshing}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              刷新状态
            </Button>
            <Button variant="outline" onClick={onBack}>
              返回主页
            </Button>
          </div>
        </div>
      </div>

      {/* Current Task Info Placeholder - Removed due to context dependency */}

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex gap-1">
          {[
            { id: 'overview', label: '概览', icon: Activity },
            { id: 'endpoints', label: '服务端点', icon: Server },
            { id: 'monitoring', label: '实时监控', icon: Database },
            { id: 'settings', label: '配置', icon: Cpu }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 flex items-center gap-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* 性能统计卡片 */}
            <StatsCard />

            {/* 性能趋势图 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
              <PerformanceChart width={800} height={200} />
            </div>

            {/* 基础统计 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* API 状态 */}
              <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">API 状态</p>
                    <p className={`text-2xl font-bold ${healthStatus.color}`}>
                      {healthStatus.label}
                    </p>
                  </div>
                  <Server className="w-8 h-8 text-gray-400" />
                </div>
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  延迟: {apiLatency.toFixed(0)}ms
                </div>
              </div>

              {/* 连接状态 */}
              <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">连接状态</p>
                    <p className="text-2xl font-bold text-green-600">
                      {apiHealth === 'healthy' ? '正常' : '异常'}
                    </p>
                  </div>
                  <Link className="w-8 h-8 text-gray-400" />
                </div>
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  {apiHealth === 'healthy' ? 'API 可用' : 'API 不可用'}
                </div>
              </div>

              {/* 任务统计 */}
              <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">总任务数</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                      {serviceStats?.total || 0}
                    </p>
                  </div>
                  <Database className="w-8 h-8 text-gray-400" />
                </div>
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  运行中: {serviceStats?.byStatus?.processing || 0}
                </div>
              </div>

              {/* 数据同步 */}
              <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">数据同步</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {apiHealth === 'healthy' ? '实时' : '本地'}
                    </p>
                  </div>
                  <Activity className="w-8 h-8 text-gray-400" />
                </div>
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  {apiHealth === 'healthy' ? 'API 优先' : '降级模式'}
                </div>
              </div>
            </div>

            {/* 集成状态组件 */}
            <div className="md:col-span-2 lg:col-span-4">
              <ApiIntegrationStatus />
            </div>
          </div>
        )}

        {activeTab === 'endpoints' && (
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                服务端点配置
              </h3>
              <div className="space-y-3">
                {[
                  { name: '健康检查', endpoint: '/api/health', method: 'GET' },
                  { name: '任务创建', endpoint: '/api/v1/tasks', method: 'POST' },
                  { name: '任务状态', endpoint: '/api/v1/tasks/{id}', method: 'GET' },
                  { name: '任务更新', endpoint: '/api/v1/tasks/{id}/status', method: 'POST' },
                  { name: '进度更新', endpoint: '/api/v1/tasks/{id}/progress', method: 'POST' },
                  { name: '文件添加', endpoint: '/api/v1/tasks/{id}/files', method: 'POST' },
                  { name: '记忆层', endpoint: '/api/v1/tasks/{id}/memory', method: 'POST' },
                  { name: '任务列表', endpoint: '/api/v1/tasks', method: 'GET' },
                  { name: '任务清理', endpoint: '/api/v1/tasks/cleanup', method: 'POST' },
                  { name: '任务统计', endpoint: '/api/v1/tasks/stats', method: 'GET' }
                ].map((endpoint) => (
                  <div key={endpoint.name} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{endpoint.name}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 font-mono">{endpoint.endpoint}</div>
                    </div>
                    <div className="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                      {endpoint.method}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                集成架构
              </h3>
              <div className="space-y-3 text-sm">
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="font-medium text-gray-900 dark:text-gray-100 mb-2">主存储层</div>
                  <div className="text-gray-600 dark:text-gray-400">
                    后端 API (RESTful) → 数据库 → 文件存储
                  </div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="font-medium text-gray-900 dark:text-gray-100 mb-2">备用存储层</div>
                  <div className="text-gray-600 dark:text-gray-400">
                    浏览器 localStorage → 内存缓存
                  </div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="font-medium text-gray-900 dark:text-gray-100 mb-2">同步机制</div>
                  <div className="text-gray-600 dark:text-gray-400">
                    双写策略：同时写入主备存储，确保数据一致性
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="space-y-6">
            {/* 实时监控面板 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                实时监控面板
              </h3>
              
              {/* 实时监控组件 */}
              <RealTimeMonitor />

              {/* 性能指标显示 */}
              <div className="mt-4">
                <PerformanceMetricsDisplay />
              </div>
            </div>

            {/* 性能趋势图 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">性能趋势</h3>
              <PerformanceChart width={800} height={250} />
            </div>

            {/* 告警规则说明 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">告警规则</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded border border-yellow-200 dark:border-yellow-800">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-600" />
                    <span className="font-medium text-yellow-800 dark:text-yellow-200">高延迟告警</span>
                  </div>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">
                    当 API 响应延迟超过 1000ms 时触发
                  </p>
                </div>
                <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                    <span className="font-medium text-red-800 dark:text-red-200">API 断开告警</span>
                  </div>
                  <p className="text-sm text-red-700 dark:text-red-300">
                    当 API 连接断开时立即触发
                  </p>
                </div>
                <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                    <span className="font-medium text-red-800 dark:text-red-200">高错误率告警</span>
                  </div>
                  <p className="text-sm text-red-700 dark:text-red-300">
                    当 API 错误率超过 30% 时触发
                  </p>
                </div>
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-blue-800 dark:text-blue-200">严重延迟告警</span>
                  </div>
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    当 API 响应延迟超过 5000ms 时触发
                  </p>
                </div>
              </div>
            </div>

            {/* 任务状态分布 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">任务状态分布</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-2">
                    <Database className="w-4 h-4" />
                    <span className="text-sm">任务总数</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {serviceStats?.total || 0}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    成功率: {serviceStats?.byStatus?.completed ? 
                      ((serviceStats.byStatus.completed / serviceStats.total) * 100).toFixed(1) : 0}%
                  </div>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-2">
                    <Shield className="w-4 h-4" />
                    <span className="text-sm">连接状态</span>
                  </div>
                  <div className="text-2xl font-bold">
                    <span className={apiHealth === 'healthy' ? 'text-green-600' : 'text-red-600'}>
                      {apiHealth === 'healthy' ? '正常' : '异常'}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {apiHealth === 'healthy' ? 'API 可用' : 'API 不可用'}
                  </div>
                </div>
              </div>

              <div className="mt-4 space-y-3">
                {serviceStats?.byStatus && Object.entries(serviceStats.byStatus).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${
                        status === 'completed' ? 'bg-green-500' :
                        status === 'processing' ? 'bg-blue-500' :
                        status === 'error' ? 'bg-red-500' :
                        status === 'pending' ? 'bg-yellow-500' :
                        'bg-gray-500'
                      }`} />
                      <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">{status.replace('_', ' ')}</span>
                    </div>
                      <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{String(count)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 性能告警组件 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">性能告警</h3>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                告警会实时显示在页面右下角。您也可以在这里查看所有告警历史。
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const monitor = getPerformanceMonitor();
                    const alerts = monitor.getAlerts();
                    console.log('所有告警:', alerts);
                  }}
                >
                  <BarChart2 className="w-4 h-4 mr-2" />
                  查看告警历史
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const monitor = getPerformanceMonitor();
                    monitor.clearAllAlerts();
                  }}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  清除所有告警
                </Button>
              </div>
            </div>

            {/* 性能数据导出 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">性能数据导出</h3>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const monitor = getPerformanceMonitor();
                    const data = monitor.exportData();
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `performance-data-${Date.now()}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                >
                  <Download className="w-4 h-4 mr-2" />
                  导出 JSON
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const monitor = getPerformanceMonitor();
                    const stats = monitor.getStats();
                    console.log('性能统计:', stats);
                  }}
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  查看统计
                </Button>
              </div>
            </div>

            {/* 手动同步 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">手动同步</h3>
              <div className="space-y-4">
                <DataSyncStatus />
                <ManualSyncButton
                  onSyncStart={() => console.log('手动同步开始')}
                  onSyncComplete={(success) => console.log('手动同步完成:', success)}
                  onSyncError={(error) => console.error('手动同步失败:', error)}
                />
              </div>
            </div>

            {/* 错误历史 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">错误历史</h3>
              <ErrorHistory />
            </div>

            {/* 配置设置 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">监控配置</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-gray-600" />
                    <span className="font-medium text-gray-800 dark:text-gray-200">采样间隔</span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    30 秒
                  </div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-gray-600" />
                    <span className="font-medium text-gray-800 dark:text-gray-200">历史记录</span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    最近 100 条
                  </div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-gray-600" />
                    <span className="font-medium text-gray-800 dark:text-gray-200">告警冷却</span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    1 分钟
                  </div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="w-4 h-4 text-gray-600" />
                    <span className="font-medium text-gray-800 dark:text-gray-200">告警状态</span>
                  </div>
                  <div className="text-sm text-green-600 dark:text-green-400">
                    已启用
                  </div>
                </div>
              </div>
            </div>

            {/* 集成流程图 */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                集成流程图
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">1</div>
                  <div className="text-gray-700 dark:text-gray-300">用户操作触发 API 调用</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">2</div>
                  <div className="text-gray-700 dark:text-gray-300">系统优先调用后端 API</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">3</div>
                  <div className="text-gray-700 dark:text-gray-300">同时同步到本地缓存</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">4</div>
                  <div className="text-gray-700 dark:text-gray-300">API 失败时自动降级</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">5</div>
                  <div className="text-gray-700 dark:text-gray-300">恢复后自动同步数据</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                API 配置
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    API 基础地址
                  </label>
                  <input 
                    type="text" 
                    defaultValue="http://localhost:8000"
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded text-gray-900 dark:text-gray-100"
                    readOnly
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    API 密钥 (可选)
                  </label>
                  <input 
                    type="password" 
                    placeholder="输入 API 密钥"
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div className="flex gap-2">
                  <Button variant="outline">保存配置</Button>
                  <Button variant="outline">测试连接</Button>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                同步配置
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">双写模式</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">同时写入 API 和本地存储</div>
                  </div>
                  <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">自动降级</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">API 失败时自动切换到本地</div>
                  </div>
                  <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">自动同步</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">API 恢复后自动同步数据</div>
                  </div>
                  <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                高级选项
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    超时时间 (秒)
                  </label>
                  <input 
                    type="number" 
                    defaultValue="30"
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    重试次数
                  </label>
                  <input 
                    type="number" 
                    defaultValue="3"
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    同步间隔 (秒)
                  </label>
                  <input 
                    type="number" 
                    defaultValue="30"
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded text-gray-900 dark:text-gray-100"
                  />
                </div>
                <Button variant="outline">保存高级配置</Button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <Link className="w-4 h-4" />
            <span>API 集成状态: {apiHealth === 'healthy' ? '正常' : '异常'}</span>
          </div>
          <div className="flex items-center gap-4">
            <span>最后更新: {new Date().toLocaleString('zh-CN')}</span>
            <span>版本: v1.0.0</span>
          </div>
        </div>
      </div>
    </div>
  );
};