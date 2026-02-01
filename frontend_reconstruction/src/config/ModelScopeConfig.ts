// ModelScope 配置
// 提供 OpenAI 的替代方案，支持多种翻译和处理模型

export interface ModelScopeConfig {
  // API 配置
  apiEndpoint: string;
  apiKey?: string;
  projectId: string;
  
  // 模型配置
  models: {
    translation: {
      name: string;
      version: string;
      capabilities: string[];
      languages: string[];
    };
    video: {
      name: string;
      version: string;
      capabilities: string[];
      formats: string[];
    };
    subtitle: {
      name: string;
      version: string;
      capabilities: string[];
      formats: string[];
    };
  };
  
  // 性能配置
  performance: {
    maxConcurrentRequests: number;
    timeout: number;
    retryAttempts: number;
    retryDelay: number;
  };
  
  // 成本控制
  cost: {
    pricePer1KTokens: number;
    freeTierLimit: number;
    budgetAlertThreshold: number;
  };
}

// ModelScope 配置管理器
export class ModelScopeConfigManager {
  private config: ModelScopeConfig;
  
  constructor() {
    this.config = {
      apiEndpoint: 'https://api.modelscope.cn',
      projectId: 'translator-agent',
      models: {
        translation: {
          name: 'modelscope/multi-lingual-translation',
          version: 'v1.0.0',
          capabilities: ['translation', 'summarization', 'sentiment'],
          languages: ['zh', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru']
        },
        video: {
          name: 'modelscope/video-processing',
          version: 'v1.0.0',
          capabilities: ['video-translate', 'subtitle-extract', 'video-enhance'],
          formats: ['mp4', 'avi', 'mov', 'mkv']
        },
        subtitle: {
          name: 'modelscope/subtitle-processor',
          version: 'v1.0.0',
          capabilities: ['subtitle-translate', 'subtitle-sync', 'subtitle-align'],
          formats: ['srt', 'vtt', 'ass']
        }
      },
      performance: {
        maxConcurrentRequests: 10,
        timeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000
      },
      cost: {
        pricePer1KTokens: 0.001,
        freeTierLimit: 1000000,
        budgetAlertThreshold: 100
      }
    };
  }

  // 获取配置
  getConfig(): ModelScopeConfig {
    return this.config;
  }

  // 更新 API 端点
  setApiEndpoint(endpoint: string) {
    this.config.apiEndpoint = endpoint;
  }

  // 设置 API 密钥
  setApiKey(apiKey: string) {
    this.config.apiKey = apiKey;
  }

  // 获取模型信息
  getModelInfo(modelType: 'translation' | 'video' | 'subtitle') {
    return this.config.models[modelType];
  }

  // 检查语言支持
  isLanguageSupported(language: string, modelType: 'translation' | 'video' | 'subtitle' = 'translation'): boolean {
    if (modelType === 'translation') {
      return this.config.models.translation.languages.includes(language);
    }
    return true;
  }

  // 获取支持的语言列表
  getSupportedLanguages(modelType: 'translation' | 'video' | 'subtitle' = 'translation'): string[] {
    if (modelType === 'translation') {
      return this.config.models.translation.languages;
    }
    return [];
  }

  // 检查格式支持
  isFormatSupported(format: string, modelType: 'video' | 'subtitle'): boolean {
    const model = this.config.models[modelType];
    return model.formats.includes(format.toLowerCase());
  }

  // 获取成本估算
  estimateCost(tokens: number): number {
    return (tokens / 1000) * this.config.cost.pricePer1KTokens;
  }

  // 检查预算限制
  checkBudget(currentUsage: number): boolean {
    return currentUsage < this.config.cost.freeTierLimit;
  }

  // 获取性能配置
  getPerformanceConfig() {
    return this.config.performance;
  }
}

// 全局 ModelScope 配置实例
export const modelScopeConfig = new ModelScopeConfigManager();

// 语言映射（ModelScope 语言代码到标准语言代码）
export const languageMapping: Record<string, string> = {
  'zh': 'zh-CN',
  'zh-CN': 'zh',
  'zh-TW': 'zh',
  'en': 'en-US',
  'en-US': 'en',
  'en-GB': 'en',
  'ja': 'ja',
  'ko': 'ko',
  'fr': 'fr',
  'de': 'de',
  'es': 'es',
  'ru': 'ru',
  'ar': 'ar',
  'pt': 'pt',
  'it': 'it',
  'nl': 'nl',
  'pl': 'pl',
  'tr': 'tr',
  'vi': 'vi',
  'th': 'th',
  'id': 'id',
  'ms': 'ms',
  'hi': 'hi',
  'bn': 'bn',
  'ur': 'ur',
  'fa': 'fa',
  'he': 'he',
  'el': 'el',
  'sv': 'sv',
  'no': 'no',
  'da': 'da',
  'fi': 'fi',
  'hu': 'hu',
  'cs': 'cs',
  'sk': 'sk',
  'sl': 'sl',
  'hr': 'hr',
  'ro': 'ro',
  'bg': 'bg',
  'uk': 'uk',
  'sr': 'sr',
  'lt': 'lt',
  'lv': 'lv',
  'et': 'et',
  'is': 'is',
  'ga': 'ga',
  'cy': 'cy',
  'mt': 'mt',
  'sq': 'sq',
  'hy': 'hy',
  'az': 'az',
  'ka': 'ka',
  'kk': 'kk',
  'ky': 'ky',
  'uz': 'uz',
  'tk': 'tk',
  'mn': 'mn',
  'ne': 'ne',
  'si': 'si',
  'lo': 'lo',
  'km': 'km',
  'my': 'my',
  'jw': 'jw',
  'tl': 'tl',
  'sw': 'sw',
  'so': 'so',
  'am': 'am',
  'om': 'om',
  'ti': 'ti',
  'ig': 'ig',
  'yo': 'yo',
  'zu': 'zu',
  'xh': 'xh',
  'st': 'st',
  'sn': 'sn',
  'ny': 'ny',
  'mg': 'mg',
  'haw': 'haw',
  'sm': 'sm',
  'to': 'to',
  'fj': 'fj',
  'ty': 'ty',
  'bo': 'bo',
  'dv': 'dv',
  'ps': 'ps',
  'ku': 'ku',
  'sd': 'sd',
  'ckb': 'ckb',
  'yi': 'yi',
  'ug': 'ug',
  'ug-Arab': 'ug',
  'chr': 'chr',
  'hmn': 'hmn',
  'loz': 'loz',
  'ln': 'ln',
  'lu': 'lu',
  'lg': 'lg',
  'rn': 'rn',
  'run': 'run',
  'ts': 'ts',
  'tn': 'tn',
  've': 've',
  'nso': 'nso',
  'ss': 'ss',
  'nr': 'nr',
  'nd': 'nd',
  'ng': 'ng',
  'kj': 'kj',
  'hz': 'hz',
  'na': 'na',
  'ki': 'ki',
  'rw': 'rw',
  'sg': 'sg',
  'kmb': 'kmb',
  'teo': 'teo',
  'cgg': 'cgg',
  'nyn': 'nyn',
  'xog': 'xog',
  'bem': 'bem',
  'kam': 'kam',
  'mer': 'mer',
  'kln': 'kln',
  'mas': 'mas',
  'dav': 'dav',
  'ebu': 'ebu',
  'guz': 'guz',
  'kde': 'kde',
  'lag': 'lag',
  'luo': 'luo',
  'mfe': 'mfe',
  'mgh': 'mgh',
  'mua': 'mua',
  'nmg': 'nmg',
  'nnh': 'nnh',
  'nus': 'nus',
  'rof': 'rof',
  'rwk': 'rwk',
  'sah': 'sah',
  'saq': 'saq',
  'seh': 'seh',
  'ses': 'ses',
  'sgx': 'sgx',
  'shi': 'shi',
  'smn': 'smn',
  'snk': 'snk',
  'srn': 'srn',
  'ssy': 'ssy',
  'swc': 'swc',
  'syr': 'syr',
  'tig': 'tig',
  'tzm': 'tzm',
  'vun': 'vun',
  'wae': 'wae',
  'wal': 'wal',
  'war': 'war',
  'wo': 'wo',
  'xal': 'xal',
  'yav': 'yav',
  'zgh': 'zgh',
  'zun': 'zun',
  'zza': 'zza'
};

// 专业模块映射
export const moduleMapping: Record<string, string> = {
  'video-translate': 'video',
  'subtitle-extract': 'subtitle',
  'text-translate': 'translation',
  'subtitle-translation': 'subtitle',
  'subtitle-sync': 'subtitle',
  'subtitle-align': 'subtitle',
  'subtitle-erasure': 'subtitle',
  'video-subtitle-pressing': 'video',
  'ai-video-narrative': 'video'
};

// 获取 ModelScope 模型名称
export function getModelScopeModelName(module: string): string {
  const modelType = moduleMapping[module] || 'translation';
  
  switch (modelType) {
    case 'translation':
      return 'modelscope/multi-lingual-translation';
    case 'video':
      return 'modelscope/video-processing';
    case 'subtitle':
      return 'modelscope/subtitle-processor';
    default:
      return 'modelscope/multi-lingual-translation';
  }
}

// 获取 ModelScope API 端点
export function getModelScopeEndpoint(module: string): string {
  const modelType = moduleMapping[module] || 'translation';
  
  switch (modelType) {
    case 'translation':
      return '/api/v1/translation/translate';
    case 'video':
      return '/api/v1/video/process';
    case 'subtitle':
      return '/api/v1/subtitle/process';
    default:
      return '/api/v1/translation/translate';
  }
}