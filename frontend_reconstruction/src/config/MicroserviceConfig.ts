// 微服务架构配置
// 为每个专业模块实现独立的微服务接口

export interface MicroserviceEndpoint {
  name: string;
  url: string;
  healthCheck: string;
  capabilities: string[];
  status: 'active' | 'inactive' | 'maintenance';
}

export interface ModuleServiceConfig {
  moduleName: string;
  displayName: string;
  serviceEndpoint: MicroserviceEndpoint;
  dependencies: string[];
  options: {
    timeout: number;
    retry: number;
    priority: number;
    resourceLimits: {
      maxMemory: number;
      maxCpu: number;
      maxDuration: number;
    };
  };
}

// 微服务配置管理器
export class MicroserviceConfigManager {
  private services: Map<string, ModuleServiceConfig> = new Map();

  constructor() {
    this.initializeServices();
  }

  private initializeServices() {
    // 专业视频翻译服务
    this.services.set('video-translate', {
      moduleName: 'video-translate',
      displayName: '专业视频翻译',
      serviceEndpoint: {
        name: 'video-translation-service',
        url: 'http://localhost:8001',
        healthCheck: '/health',
        capabilities: ['video-translate', 'audio-extract', 'voice-cloning', 'subtitle-sync'],
        status: 'active'
      },
      dependencies: ['translation-service', 'video-processing-service'],
      options: {
        timeout: 300000, // 5分钟
        retry: 3,
        priority: 1,
        resourceLimits: {
          maxMemory: 4096, // 4GB
          maxCpu: 4,
          maxDuration: 600 // 10分钟
        }
      }
    });

    // 字幕提取服务
    this.services.set('subtitle-extract', {
      moduleName: 'subtitle-extract',
      displayName: '字幕提取',
      serviceEndpoint: {
        name: 'subtitle-extraction-service',
        url: 'http://localhost:8002',
        healthCheck: '/health',
        capabilities: ['subtitle-extract', 'speech-recognition', 'speaker-diarization'],
        status: 'active'
      },
      dependencies: ['video-processing-service'],
      options: {
        timeout: 180000, // 3分钟
        retry: 2,
        priority: 2,
        resourceLimits: {
          maxMemory: 2048,
          maxCpu: 2,
          maxDuration: 300
        }
      }
    });

    // 字幕翻译服务
    this.services.set('text-translate', {
      moduleName: 'text-translate',
      displayName: '字幕翻译',
      serviceEndpoint: {
        name: 'translation-service',
        url: 'http://localhost:8003',
        healthCheck: '/health',
        capabilities: ['translate', 'summarize', 'sentiment', 'context-preserve'],
        status: 'active'
      },
      dependencies: ['modelscope-service'],
      options: {
        timeout: 60000, // 1分钟
        retry: 3,
        priority: 1,
        resourceLimits: {
          maxMemory: 1024,
          maxCpu: 1,
          maxDuration: 60
        }
      }
    });

    // 字幕同步服务
    this.services.set('subtitle-sync', {
      moduleName: 'subtitle-sync',
      displayName: '字幕同步',
      serviceEndpoint: {
        name: 'subtitle-sync-service',
        url: 'http://localhost:8004',
        healthCheck: '/health',
        capabilities: ['time-align', 'sync-correction', 'conflict-detection'],
        status: 'active'
      },
      dependencies: ['subtitle-processing-service'],
      options: {
        timeout: 120000, // 2分钟
        retry: 2,
        priority: 2,
        resourceLimits: {
          maxMemory: 1024,
          maxCpu: 1,
          maxDuration: 120
        }
      }
    });

    // 字幕擦除服务
    this.services.set('subtitle-erasure', {
      moduleName: 'subtitle-erasure',
      displayName: '字幕擦除',
      serviceEndpoint: {
        name: 'subtitle-erasure-service',
        url: 'http://localhost:8005',
        healthCheck: '/health',
        capabilities: ['subtitle-remove', 'video-inpaint', 'quality-enhance'],
        status: 'active'
      },
      dependencies: ['video-processing-service'],
      options: {
        timeout: 240000, // 4分钟
        retry: 2,
        priority: 3,
        resourceLimits: {
          maxMemory: 3072,
          maxCpu: 3,
          maxDuration: 240
        }
      }
    });

    // 视频字幕压制服务
    this.services.set('video-subtitle-pressing', {
      moduleName: 'video-subtitle-pressing',
      displayName: '视频字幕压制',
      serviceEndpoint: {
        name: 'subtitle-pressing-service',
        url: 'http://localhost:8006',
        healthCheck: '/health',
        capabilities: ['subtitle-burn', 'style-customization', 'position-adjust'],
        status: 'active'
      },
      dependencies: ['video-processing-service', 'subtitle-processing-service'],
      options: {
        timeout: 300000, // 5分钟
        retry: 2,
        priority: 2,
        resourceLimits: {
          maxMemory: 4096,
          maxCpu: 4,
          maxDuration: 300
        }
      }
    });

    // AI 视频叙事服务
    this.services.set('ai-video-narrative', {
      moduleName: 'ai-video-narrative',
      displayName: 'AI 视频叙事',
      serviceEndpoint: {
        name: 'narrative-service',
        url: 'http://localhost:8007',
        healthCheck: '/health',
        capabilities: ['story-generation', 'voice-over', 'scene-detection', 'emotional-analysis'],
        status: 'active'
      },
      dependencies: ['modelscope-service', 'video-processing-service'],
      options: {
        timeout: 600000, // 10分钟
        retry: 3,
        priority: 1,
        resourceLimits: {
          maxMemory: 8192,
          maxCpu: 8,
          maxDuration: 600
        }
      }
    });

    // ModelScope 服务（核心依赖）
    this.services.set('modelscope-service', {
      moduleName: 'modelscope',
      displayName: 'ModelScope AI 模型',
      serviceEndpoint: {
        name: 'modelscope-service',
        url: 'http://localhost:8008',
        healthCheck: '/health',
        capabilities: ['translation', 'speech-recognition', 'video-processing', 'nlp'],
        status: 'active'
      },
      dependencies: [],
      options: {
        timeout: 120000, // 2分钟
        retry: 3,
        priority: 1,
        resourceLimits: {
          maxMemory: 4096,
          maxCpu: 4,
          maxDuration: 120
        }
      }
    });
  }

  // 获取服务配置
  getService(moduleName: string): ModuleServiceConfig | undefined {
    return this.services.get(moduleName);
  }

  // 获取所有服务
  getAllServices(): ModuleServiceConfig[] {
    return Array.from(this.services.values());
  }

  // 获取活跃服务
  getActiveServices(): ModuleServiceConfig[] {
    return Array.from(this.services.values()).filter(
      service => service.serviceEndpoint.status === 'active'
    );
  }

  // 检查服务健康状态
  async checkServiceHealth(moduleName: string): Promise<boolean> {
    const service = this.getService(moduleName);
    if (!service) return false;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(
        `${service.serviceEndpoint.url}${service.serviceEndpoint.healthCheck}`,
        { 
          method: 'GET', 
          signal: controller.signal
        }
      );
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      console.error(`Service health check failed for ${moduleName}:`, error);
      return false;
    }
  }

  // 获取服务依赖
  getServiceDependencies(moduleName: string): string[] {
    const service = this.getService(moduleName);
    return service ? service.dependencies : [];
  }

  // 获取服务选项
  getServiceOptions(moduleName: string) {
    const service = this.getService(moduleName);
    return service ? service.options : null;
  }

  // 更新服务状态
  updateServiceStatus(moduleName: string, status: 'active' | 'inactive' | 'maintenance'): boolean {
    const service = this.getService(moduleName);
    if (service) {
      service.serviceEndpoint.status = status;
      return true;
    }
    return false;
  }

  // 获取推荐服务（基于优先级和负载）
  getRecommendedService(moduleName: string): ModuleServiceConfig | null {
    const service = this.getService(moduleName);
    if (!service) return null;

    // 在实际应用中，这里应该考虑负载均衡
    // 这里简单返回主服务
    return service;
  }
}

// 全局微服务配置实例
export const microserviceConfig = new MicroserviceConfigManager();

// 服务发现配置
export interface ServiceDiscoveryConfig {
  registryUrl: string;
  refreshInterval: number;
  timeout: number;
}

export const serviceDiscovery: ServiceDiscoveryConfig = {
  registryUrl: 'http://localhost:8500', // Consul 或类似服务注册中心
  refreshInterval: 30000, // 30秒
  timeout: 5000
};

// 负载均衡配置
export interface LoadBalancerConfig {
  strategy: 'round-robin' | 'least-connections' | 'weighted';
  healthCheckInterval: number;
  timeout: number;
}

export const loadBalancer: LoadBalancerConfig = {
  strategy: 'round-robin',
  healthCheckInterval: 10000,
  timeout: 5000
};

// 获取模块对应的微服务端点
export function getModuleEndpoint(module: string): string {
  const service = microserviceConfig.getService(module);
  return service ? service.serviceEndpoint.url : 'http://localhost:8000';
}

// 获取模块对应的微服务名称
export function getModuleName(module: string): string {
  const service = microserviceConfig.getService(module);
  return service ? service.serviceEndpoint.name : 'default-service';
}

// 检查模块是否支持
export function isModuleSupported(module: string): boolean {
  return microserviceConfig.getService(module) !== undefined;
}

// 获取模块的依赖服务
export function getModuleDependencies(module: string): string[] {
  return microserviceConfig.getServiceDependencies(module);
}