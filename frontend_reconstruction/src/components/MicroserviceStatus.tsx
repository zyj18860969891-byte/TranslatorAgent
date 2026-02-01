import React, { useState, useEffect } from 'react';
import { microserviceConfig, ModuleServiceConfig } from '../config/MicroserviceConfig';

interface ServiceStatus {
  name: string;
  status: 'active' | 'inactive' | 'maintenance' | 'checking';
  latency: number;
  lastCheck: Date;
  error?: string;
}

export const MicroserviceStatus: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    loadServices();
    const interval = setInterval(loadServices, 30000); // 每30秒刷新一次
    return () => clearInterval(interval);
  }, []);

  const loadServices = async () => {
    const allServices = microserviceConfig.getAllServices();
    const statusPromises = allServices.map(async (service) => {
      const startTime = Date.now();
      try {
        const isHealthy = await microserviceConfig.checkServiceHealth(service.moduleName);
        const latency = Date.now() - startTime;
        
        return {
          name: service.serviceEndpoint.name,
          status: isHealthy ? 'active' : 'inactive',
          latency,
          lastCheck: new Date(),
          error: isHealthy ? undefined : 'Health check failed'
        };
      } catch (error) {
        return {
          name: service.serviceEndpoint.name,
          status: 'inactive' as const,
          latency: Date.now() - startTime,
          lastCheck: new Date(),
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    });

    const results = await Promise.all(statusPromises);
    setServices(results as ServiceStatus[]);
  };

  const checkAllServices = async () => {
    setIsChecking(true);
    await loadServices();
    setIsChecking(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-red-500';
      case 'maintenance': return 'bg-yellow-500';
      case 'checking': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const formatLatency = (ms: number) => {
    if (ms < 100) return `${ms}ms`;
    if (ms < 1000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', { hour12: false });
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">微服务状态</h3>
        <button
          onClick={checkAllServices}
          disabled={isChecking}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm transition-colors"
        >
          {isChecking ? '检查中...' : '刷新状态'}
        </button>
      </div>

      {/* Current task info placeholder - removed due to context dependency */}

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {services.map((service) => (
          <div
            key={service.name}
            className="flex items-center justify-between p-2 bg-gray-700 rounded hover:bg-gray-650 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(service.status)}`} />
              <div>
                <div className="text-sm font-medium text-white">{service.name}</div>
                <div className="text-xs text-gray-400">
                  延迟: {formatLatency(service.latency)} | 最后检查: {formatTime(service.lastCheck)}
                </div>
                {service.error && (
                  <div className="text-xs text-red-400 mt-1">{service.error}</div>
                )}
              </div>
            </div>
            <div className="text-xs">
              <span className={`px-2 py-1 rounded ${
                service.status === 'active' ? 'bg-green-900 text-green-300' :
                service.status === 'inactive' ? 'bg-red-900 text-red-300' :
                service.status === 'maintenance' ? 'bg-yellow-900 text-yellow-300' :
                'bg-blue-900 text-blue-300'
              }`}>
                {service.status === 'active' ? '运行中' :
                 service.status === 'inactive' ? '离线' :
                 service.status === 'maintenance' ? '维护中' : '检查中'}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="flex justify-between text-xs text-gray-400">
          <span>总计: {services.length}</span>
          <span>活跃: {services.filter(s => s.status === 'active').length}</span>
          <span>离线: {services.filter(s => s.status === 'inactive').length}</span>
        </div>
      </div>
    </div>
  );
};

// 模块专用服务状态组件
export const ModuleServiceStatus: React.FC<{ module: string }> = ({ module }) => {
  const [service, setService] = useState<ModuleServiceConfig | null>(null);
  const [status, setStatus] = useState<'active' | 'inactive' | 'checking'>('checking');
  const [latency, setLatency] = useState<number>(0);

  useEffect(() => {
    loadServiceStatus();
    const interval = setInterval(loadServiceStatus, 15000);
    return () => clearInterval(interval);
  }, [module]);

  const loadServiceStatus = async () => {
    const serviceConfig = microserviceConfig.getService(module);
    if (!serviceConfig) {
      setStatus('inactive');
      return;
    }

    setService(serviceConfig);
    setStatus('checking');

    const startTime = Date.now();
    try {
      const isHealthy = await microserviceConfig.checkServiceHealth(module);
      setLatency(Date.now() - startTime);
      setStatus(isHealthy ? 'active' : 'inactive');
    } catch (error) {
      setLatency(Date.now() - startTime);
      setStatus('inactive');
    }
  };

  if (!service) {
    return (
      <div className="text-sm text-gray-400">
        模块 {module} 未配置微服务
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${
        status === 'active' ? 'bg-green-500' :
        status === 'inactive' ? 'bg-red-500' :
        'bg-blue-500'
      }`} />
      <span className="text-gray-300">{service.serviceEndpoint.name}</span>
      <span className="text-gray-500">|</span>
      <span className="text-gray-400">{formatLatency(latency)}</span>
      <span className={`px-2 py-0.5 rounded text-xs ${
        status === 'active' ? 'bg-green-900 text-green-300' :
        status === 'inactive' ? 'bg-red-900 text-red-300' :
        'bg-blue-900 text-blue-300'
      }`}>
        {status === 'active' ? '正常' : status === 'inactive' ? '离线' : '检查中'}
      </span>
    </div>
  );
};

// 服务依赖树组件
export const ServiceDependencyTree: React.FC<{ module: string }> = ({ module }) => {
  const [dependencies, setDependencies] = useState<string[]>([]);
  const [healthStatus, setHealthStatus] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadDependencies();
  }, [module]);

  const loadDependencies = async () => {
    const deps = microserviceConfig.getServiceDependencies(module);
    setDependencies(deps);

    const status: Record<string, boolean> = {};
    for (const dep of deps) {
      try {
        status[dep] = await microserviceConfig.checkServiceHealth(dep);
      } catch (error) {
        status[dep] = false;
      }
    }
    setHealthStatus(status);
  };

  if (dependencies.length === 0) {
    return (
      <div className="text-sm text-gray-400">
        无依赖服务
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="text-sm font-medium text-gray-300">依赖服务:</div>
      <div className="space-y-1">
        {dependencies.map((dep) => (
          <div key={dep} className="flex items-center space-x-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${
              healthStatus[dep] ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-gray-400">{dep}</span>
            <span className={`px-1.5 py-0.5 rounded text-xs ${
              healthStatus[dep] ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
            }`}>
              {healthStatus[dep] ? '正常' : '异常'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

// 服务配置详情组件
export const ServiceConfigDetails: React.FC<{ module: string }> = ({ module }) => {
  const service = microserviceConfig.getService(module);

  if (!service) {
    return (
      <div className="text-sm text-gray-400">
        未找到服务配置
      </div>
    );
  }

  return (
    <div className="space-y-3 text-sm">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <div className="text-gray-500">服务名称</div>
          <div className="text-white">{service.serviceEndpoint.name}</div>
        </div>
        <div>
          <div className="text-gray-500">服务地址</div>
          <div className="text-white">{service.serviceEndpoint.url}</div>
        </div>
        <div>
          <div className="text-gray-500">健康检查</div>
          <div className="text-white">{service.serviceEndpoint.healthCheck}</div>
        </div>
        <div>
          <div className="text-gray-500">状态</div>
          <div className={`px-2 py-0.5 rounded text-xs inline-block ${
            service.serviceEndpoint.status === 'active' ? 'bg-green-900 text-green-300' :
            service.serviceEndpoint.status === 'inactive' ? 'bg-red-900 text-red-300' :
            'bg-yellow-900 text-yellow-300'
          }`}>
            {service.serviceEndpoint.status === 'active' ? '活跃' :
             service.serviceEndpoint.status === 'inactive' ? '非活跃' : '维护中'}
          </div>
        </div>
      </div>

      <div>
        <div className="text-gray-500 mb-1">支持能力</div>
        <div className="flex flex-wrap gap-1">
          {service.serviceEndpoint.capabilities.map((cap) => (
            <span key={cap} className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs">
              {cap}
            </span>
          ))}
        </div>
      </div>

      <div className="border-t border-gray-700 pt-3">
        <div className="text-gray-500 mb-2">资源限制</div>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="bg-gray-700 p-2 rounded">
            <div className="text-gray-400">最大内存</div>
            <div className="text-white">{service.options.resourceLimits.maxMemory} MB</div>
          </div>
          <div className="bg-gray-700 p-2 rounded">
            <div className="text-gray-400">最大CPU</div>
            <div className="text-white">{service.options.resourceLimits.maxCpu} 核</div>
          </div>
          <div className="bg-gray-700 p-2 rounded">
            <div className="text-gray-400">超时时间</div>
            <div className="text-white">{service.options.timeout / 1000} 秒</div>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-700 pt-3">
        <div className="text-gray-500 mb-2">依赖服务</div>
        {service.dependencies.length > 0 ? (
          <div className="flex flex-wrap gap-1">
            {service.dependencies.map((dep) => (
              <span key={dep} className="px-2 py-0.5 bg-blue-900 text-blue-300 rounded text-xs">
                {dep}
              </span>
            ))}
          </div>
        ) : (
          <div className="text-gray-400 text-xs">无依赖服务</div>
        )}
      </div>
    </div>
  );
};

// 辅助函数
function formatLatency(ms: number): string {
  if (ms < 100) return `${ms}ms`;
  if (ms < 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 1000).toFixed(1)}s`;
}