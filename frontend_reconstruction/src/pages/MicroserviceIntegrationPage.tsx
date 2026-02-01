import React, { useState, useEffect } from 'react';
import { 
  Server, 
  Activity, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw,
  Shield,
  Cpu,
  Database,
  Network
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { 
  MicroserviceStatus, 
  ModuleServiceStatus, 
  ServiceDependencyTree,
  ServiceConfigDetails 
} from '../components/MicroserviceStatus';
import { microserviceConfig } from '../config/MicroserviceConfig';

interface MicroserviceIntegrationPageProps {
  onBack: () => void;
}

export const MicroserviceIntegrationPage: React.FC<MicroserviceIntegrationPageProps> = ({
  onBack
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'services' | 'config' | 'monitoring'>('overview');
  const [serviceStats, setServiceStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
    maintenance: 0,
    avgLatency: 0
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    updateServiceStats();
    const interval = setInterval(updateServiceStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const updateServiceStats = async () => {
    const services = microserviceConfig.getAllServices();
    let activeCount = 0;
    let inactiveCount = 0;
    let maintenanceCount = 0;
    let totalLatency = 0;
    let checkedCount = 0;

    for (const service of services) {
      try {
        const isHealthy = await microserviceConfig.checkServiceHealth(service.moduleName);
        if (isHealthy) {
          activeCount++;
        } else {
          inactiveCount++;
        }
        checkedCount++;
      } catch (error) {
        inactiveCount++;
      }
    }

    const maintenanceServices = services.filter(s => s.serviceEndpoint.status === 'maintenance');
    maintenanceCount = maintenanceServices.length;

    setServiceStats({
      total: services.length,
      active: activeCount,
      inactive: inactiveCount,
      maintenance: maintenanceCount,
      avgLatency: checkedCount > 0 ? totalLatency / checkedCount : 0
    });
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await updateServiceStats();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const getHealthStatus = () => {
    const { total, active } = serviceStats;
    const healthPercentage = total > 0 ? (active / total) * 100 : 0;
    
    if (healthPercentage >= 90) return { color: 'text-green-500', label: '健康' };
    if (healthPercentage >= 70) return { color: 'text-yellow-500', label: '一般' };
    return { color: 'text-red-500', label: '异常' };
  };

  const healthStatus = getHealthStatus();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Server className="w-6 h-6" />
              微服务集成监控
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              实时监控所有微服务的健康状态和性能指标
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
            { id: 'services', label: '服务列表', icon: Server },
            { id: 'config', label: '配置详情', icon: Cpu },
            { id: 'monitoring', label: '监控', icon: Network }
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Services */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">总服务数</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{serviceStats.total}</p>
                </div>
                <Server className="w-8 h-8 text-gray-400" />
              </div>
            </div>

            {/* Active Services */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">运行中</p>
                  <p className="text-2xl font-bold text-green-600">{serviceStats.active}</p>
                </div>
                <CheckCircle2 className="w-8 h-8 text-green-500" />
              </div>
            </div>

            {/* Inactive Services */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">离线</p>
                  <p className="text-2xl font-bold text-red-600">{serviceStats.inactive}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-red-500" />
              </div>
            </div>

            {/* Maintenance Services */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">维护中</p>
                  <p className="text-2xl font-bold text-yellow-600">{serviceStats.maintenance}</p>
                </div>
                <Database className="w-8 h-8 text-yellow-500" />
              </div>
            </div>

            {/* Health Status */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800 md:col-span-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">系统健康状态</p>
                  <p className={`text-2xl font-bold ${healthStatus.color}`}>
                    {healthStatus.label}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    健康率: {serviceStats.total > 0 ? ((serviceStats.active / serviceStats.total) * 100).toFixed(1) : 0}%
                  </p>
                </div>
                <Activity className="w-8 h-8 text-gray-400" />
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800 md:col-span-2">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">快速操作</p>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleRefresh}>
                  <RefreshCw className="w-4 h-4 mr-1" />
                  刷新所有
                </Button>
                <Button size="sm" variant="outline">
                  <Shield className="w-4 h-4 mr-1" />
                  健康检查
                </Button>
                <Button size="sm" variant="outline">
                  <Cpu className="w-4 h-4 mr-1" />
                  资源监控
                </Button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'services' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="lg:col-span-2">
              <MicroserviceStatus />
            </div>
            <div className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                专业模块服务
              </h3>
              <div className="space-y-3">
                {['video-translate', 'subtitle-extract', 'text-translate', 'subtitle-sync', 'subtitle-erasure', 'video-subtitle-pressing', 'ai-video-narrative'].map((module) => (
                  <div key={module} className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {module.replace('-', ' ').toUpperCase()}
                      </span>
                      <ModuleServiceStatus module={module} />
                    </div>
                    <ServiceDependencyTree module={module} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'config' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {['video-translate', 'subtitle-extract', 'text-translate'].map((module) => (
              <div key={module} className="bg-white dark:bg-gray-950 rounded-lg p-4 border border-gray-200 dark:border-gray-800">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  {module.replace('-', ' ').toUpperCase()} 配置
                </h3>
                <ServiceConfigDetails module={module} />
              </div>
            ))}
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                实时监控面板
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-2">
                    <Cpu className="w-4 h-4" />
                    <span className="text-sm">CPU 使用率</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">45%</div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '45%' }} />
                  </div>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-2">
                    <Database className="w-4 h-4" />
                    <span className="text-sm">内存使用</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">2.4 GB</div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '60%' }} />
                  </div>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-2">
                    <Network className="w-4 h-4" />
                    <span className="text-sm">网络延迟</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">120ms</div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '30%' }} />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-md font-medium text-gray-900 dark:text-gray-100">服务调用统计</h4>
                <div className="space-y-2">
                  {[
                    { name: '翻译服务', calls: 1245, success: 1230, avgLatency: 45 },
                    { name: '视频处理', calls: 342, success: 338, avgLatency: 120 },
                    { name: '字幕提取', calls: 567, success: 560, avgLatency: 85 },
                    { name: 'AI 模型', calls: 892, success: 885, avgLatency: 150 }
                  ].map((service) => (
                    <div key={service.name} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{service.name}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          成功率: {((service.success / service.calls) * 100).toFixed(1)}% | 平均延迟: {service.avgLatency}ms
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-gray-900 dark:text-gray-100">{service.calls}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">调用次数</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-950 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                依赖关系拓扑
              </h3>
              <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <div className="mb-2">核心依赖链:</div>
                  <div className="space-y-1 font-mono text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-green-500 rounded-full" />
                      <span>ModelScope 服务 → 翻译服务 → 字幕处理</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-500 rounded-full" />
                      <span>视频处理服务 → 字幕提取 → 字幕同步</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-purple-500 rounded-full" />
                      <span>AI 模型服务 → 视频叙事 → 语音合成</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            <span>微服务架构已就绪</span>
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