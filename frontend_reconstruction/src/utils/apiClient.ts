// Translator Agent API 客户端
// 集成真实后端 API，支持翻译、视频处理、字幕处理等微服务

// API 配置接口
export interface ApiConfig {
  baseUrl: string;
  version: string;
  timeout: number;
  retryCount: number;
  apiKey?: string;
}

// API 配置
const apiConfig: ApiConfig = {
  baseUrl: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000',
  version: (import.meta as any).env?.VITE_API_VERSION || 'v1',
  timeout: parseInt((import.meta as any).env?.VITE_API_TIMEOUT || '30000'),
  retryCount: parseInt((import.meta as any).env?.VITE_API_RETRY_COUNT || '3'),
  apiKey: (import.meta as any).env?.VITE_API_KEY
};

// 构建 API URL
const buildUrl = (endpoint: string, params?: Record<string, any>): string => {
  // 如果endpoint已经包含完整的路径，直接使用
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    const baseUrl = endpoint;
    
    if (params) {
      const queryString = new URLSearchParams(params).toString();
      return `${baseUrl}?${queryString}`;
    }
    
    return baseUrl;
  }
  
  // 如果endpoint已经包含/api/前缀，只添加baseUrl
  if (endpoint.startsWith('/api/')) {
    const baseUrl = `${apiConfig.baseUrl}${endpoint}`;
    
    if (params) {
      const queryString = new URLSearchParams(params).toString();
      return `${baseUrl}?${queryString}`;
    }
    
    return baseUrl;
  }
  
  // 如果endpoint已经包含/tasks/前缀，添加/api/v1前缀
  if (endpoint.startsWith('/tasks/')) {
    const baseUrl = `${apiConfig.baseUrl}/api/v1${endpoint}`;
    
    if (params) {
      const queryString = new URLSearchParams(params).toString();
      return `${baseUrl}?${queryString}`;
    }
    
    return baseUrl;
  }
  
  // 否则添加标准前缀
  const baseUrl = `${apiConfig.baseUrl}/api/${apiConfig.version}${endpoint}`;
  
  if (params) {
    const queryString = new URLSearchParams(params).toString();
    return `${baseUrl}?${queryString}`;
  }
  
  return baseUrl;
};

// 带重试的 fetch 请求
const fetchWithRetry = async (url: string, options: RequestInit, retryCount = 0): Promise<Response> => {
  try {
    const response = await fetch(url, options);
    
    // 如果是网络错误或服务器错误，且还有重试次数，进行重试
    if (!response.ok && retryCount < apiConfig.retryCount) {
      console.warn(`请求失败，${retryCount + 1}/${apiConfig.retryCount} 次重试: ${url}`);
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1))); // 指数退避
      return fetchWithRetry(url, options, retryCount + 1);
    }
    
    return response;
  } catch (error) {
    if (retryCount < apiConfig.retryCount) {
      console.warn(`请求异常，${retryCount + 1}/${apiConfig.retryCount} 次重试: ${url}`, error);
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
      return fetchWithRetry(url, options, retryCount + 1);
    }
    throw error;
  }
};

// API 响应接口
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp?: string;
}

export interface TranslationRequest {
  text: string;
  targetLanguage: string;
  sourceLanguage?: string;
  preserveTone?: boolean;
  context?: string;
}

export interface TranslationResponse {
  translatedText: string;
  detectedLanguage?: string;
  confidence: number;
  processingTime: number;
}

export interface VideoProcessingRequest {
  videoUrl: string;
  operation: string; // 允许任意操作类型
  targetLanguage?: string;
  subtitleFormat?: 'srt' | 'vtt' | 'ass';
  options?: Record<string, any>;
}

export interface VideoProcessingResponse {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  resultUrl?: string;
  estimatedTime?: number;
}

export interface SubtitleProcessingRequest {
  subtitleUrl: string;
  operation: 'translate' | 'sync' | 'align' | 'detect_conflict';
  targetLanguage?: string;
  timeOffset?: number;
  options?: Record<string, any>;
}

export interface SubtitleProcessingResponse {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  resultUrl?: string;
  estimatedTime?: number;
  operation?: string;
  targetLanguage?: string;
  timestamp?: string;
}

export interface TaskCreationRequest {
  module: string;
  taskName: string;
  files?: Array<{
    name: string;
    type: string;
    url: string;
  }>;
  instructions?: string;
  options?: Record<string, any>;
}

export interface TaskCreationResponse {
  taskId: string;
  id?: string;
  module?: string;
  taskType?: string;
  task_type?: string;
  status: 'created' | 'queued' | 'processing' | 'completed' | 'failed';
  workspace?: string;
  progress?: {
    current: number;
    total: number;
    percentage: number;
    message: string;
  };
  memory?: {
    conversationHistory: any[];
    processingResults: any[];
    intermediateData: any[];
  };
  files?: string[];
  createdAt: string;
  created_at?: string;
  updatedAt?: string;
  updated_at?: string;
  completedAt?: string;
  error?: string;
}

export interface TaskStatusResponse {
  taskId: string;
  id?: string;
  status: 'created' | 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  files: string[];
  memoryLayer: {
    conversationHistory: any[];
    processingResults: any[];
    intermediateData: any[];
  };
  createdAt: string;
  created_at?: string;
  updatedAt: string;
  updated_at?: string;
  completedAt?: string;
  error?: string;
}

export interface ModelInfo {
  name: string;
  provider: 'modelscope' | 'openai' | 'custom';
  version: string;
  capabilities: string[];
  status: 'active' | 'inactive';
}

// API 客户端类
export class APIClient {
  private baseURL: string;
  private apiKey?: string;

  constructor(baseURL: string = 'http://localhost:8000', apiKey?: string) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
  }

  // 设置 API 密钥
  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
  }

  // 翻译API
  async translate(request: TranslationRequest): Promise<ApiResponse<TranslationResponse>> {
    return this.post('/api/v1/translation/translate', request);
  }

  // 文本翻译（简化接口）
  async translateText(request: { text: string; targetLanguage: string; sourceLanguage?: string }): Promise<ApiResponse<{ translatedText: string }>> {
    return this.translate({
      text: request.text,
      targetLanguage: request.targetLanguage,
      sourceLanguage: request.sourceLanguage
    });
  }

  // 视频处理API
  async processVideo(request: VideoProcessingRequest): Promise<ApiResponse<VideoProcessingResponse>> {
    return this.post('/api/v1/video/process', request);
  }

  // 字幕处理API
  async processSubtitle(request: SubtitleProcessingRequest): Promise<ApiResponse<SubtitleProcessingResponse>> {
    return this.post('/api/v1/subtitle/process', request);
  }

  // 创建任务
  async createTask(request: TaskCreationRequest): Promise<ApiResponse<TaskCreationResponse>> {
    return this.post('/tasks', request);
  }

  // 获取任务状态
  async getTaskStatus(taskId: string): Promise<ApiResponse<TaskStatusResponse>> {
    return this.get(`/tasks/${taskId}`);
  }

  // 获取模块任务列表
  async getModuleTasks(module: string, status?: string): Promise<ApiResponse<TaskStatusResponse[]>> {
    const params = new URLSearchParams();
    if (module) params.append('task_type', module);
    if (status) params.append('status', status);
    
    return this.get(`/tasks?${params.toString()}`);
  }

  // 取消任务
  async cancelTask(taskId: string): Promise<ApiResponse<void>> {
    return this.post(`/tasks/${taskId}/cancel`, {});
  }

  // 删除任务
  async deleteTask(taskId: string): Promise<ApiResponse<void>> {
    return this.delete(`/tasks/${taskId}`);
  }

  // 更新任务状态
  async updateTaskStatus(taskId: string, _module: string, updates: any): Promise<ApiResponse<any>> {
    return this.post(`/tasks/${taskId}/status`, updates);
  }

  // 更新任务进度
  async updateTaskProgress(taskId: string, module: string, progress: any): Promise<ApiResponse<any>> {
    return this.post(`/tasks/${taskId}/progress`, { module, progress });
  }

  // 添加文件到任务
  async addFileToTask(taskId: string, module: string, filePath: string, status: string): Promise<ApiResponse<any>> {
    return this.post(`/tasks/${taskId}/files`, { module, file_path: filePath, status });
  }

  // 添加到记忆层
  async addToMemoryLayer(taskId: string, module: string, type: string, data: any): Promise<ApiResponse<any>> {
    return this.post(`/tasks/${taskId}/memory`, { module, type, data });
  }

  // 获取所有任务
  async getAllTasks(): Promise<ApiResponse<Record<string, Record<string, any>>>> {
    return this.get('/tasks/all');
  }

  // 清理任务
  async cleanupTasks(maxAge: number): Promise<ApiResponse<void>> {
    return this.post('/tasks/cleanup', { maxAge });
  }

  // 获取任务统计
  async getTaskStats(module?: string): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (module) params.append('module', module);
    return this.get(`/tasks/stats?${params.toString()}`);
  }

  // 获取任务文件列表
  async getTaskFiles(taskId: string): Promise<ApiResponse<any>> {
    return this.get(`/tasks/${taskId}/files`);
  }

  // 下载任务文件
  async downloadTaskFile(taskId: string, fileName: string): Promise<any> {
    // 直接返回原始响应，因为后端返回的是 StreamingResponse
    const response = await fetch(`${this.baseURL}/api/v1/tasks/${taskId}/files/${encodeURIComponent(fileName)}`, {
      method: 'GET',
      headers: this.getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Download failed: ${response.status} ${response.statusText}`);
    }
    
    return response;
  }

  // 获取模型信息
  async getModelInfo(): Promise<ApiResponse<ModelInfo[]>> {
    return this.get('/models');
  }

  // 健康检查
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: number }>> {
    return this.get('/health');
  }

  // 上传文件到通用存储
  async uploadFile(file: File): Promise<ApiResponse<{ file_path: string; file_name: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadUrl = buildUrl('/upload');
    const response = await fetch(uploadUrl, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed: ${response.status} ${response.statusText} - ${errorText}`);
    }
    
    return response.json();
  }

  // 上传实际文件到任务（先上传到通用存储，再关联到任务）
  async uploadTaskFile(taskId: string, file: File): Promise<ApiResponse<{ file_path: string; file_name: string }>> {
    // 步骤1：上传文件到通用存储
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadUrl = buildUrl('/upload');
    const uploadResponse = await fetch(uploadUrl, {
      method: 'POST',
      body: formData,
    });
    
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      throw new Error(`Upload failed: ${uploadResponse.status} ${uploadResponse.statusText} - ${errorText}`);
    }
    
    const uploadResult = await uploadResponse.json();
    
    if (!uploadResult.success || !uploadResult.data) {
      throw new Error(uploadResult.error || 'File upload failed');
    }
    
    const { file_path } = uploadResult.data;
    
    // 步骤2：将文件关联到任务
    const taskFileResponse = await this.post(`/tasks/${taskId}/files`, {
      filePath: file_path,
      status: 'uploaded'
    });
    
    return taskFileResponse as unknown as Promise<ApiResponse<{ file_path: string; file_name: string }>>;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Accept': '*/*',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  private async get(endpoint: string): Promise<ApiResponse<any>> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    try {
      const url = buildUrl(endpoint);
      const response = await fetch(url, {
        method: 'GET',
        headers
      });

      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          error: `HTTP ${response.status}: ${errorText}`
        };
      }

      const data = await response.json();
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  private async post(endpoint: string, data: any, options: RequestInit = {}): Promise<ApiResponse<any>> {
    const isFormData = data instanceof FormData;
    const body = isFormData ? data : JSON.stringify(data);
    
    const headers: HeadersInit = isFormData ? {} : { 'Content-Type': 'application/json' };

    if (this.apiKey && !isFormData) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    try {
      const url = buildUrl(endpoint);
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body,
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          error: `HTTP ${response.status}: ${errorText}`
        };
      }

      const data = await response.json();
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  private async delete(endpoint: string): Promise<ApiResponse<any>> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    try {
      const url = buildUrl(endpoint);
      const response = await fetch(url, {
        method: 'DELETE',
        headers
      });

      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          error: `HTTP ${response.status}: ${errorText}`
        };
      }

      return {
        success: true,
        data: undefined
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
}

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
  }
}

// 导出配置信息
export const getApiConfig = (): ApiConfig => ({ ...apiConfig });

// 检查 API 连接状态
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(buildUrl('/health'), {
      method: 'GET',
      signal: AbortSignal.timeout(5000) // 健康检查使用较短超时
    });
    return response.ok;
  } catch (error) {
    return false;
  }
};

// 获取 API 延迟
export const getApiLatency = async (): Promise<number> => {
  const start = performance.now();
  try {
    await fetch(buildUrl('/health'), {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    });
    return performance.now() - start;
  } catch (error) {
    return -1; // 表示连接失败
  }
};

// 全局 API 客户端实例
export const apiClient = new APIClient(apiConfig.baseUrl);