// 集成真实后端API的文件系统状态管理器
import { apiClient, checkApiHealth, getApiConfig } from './apiClient';
import { TaskStatus, ProgressInfo, TaskState } from './FileSystemStateMachine';

// API文件系统状态管理器（集成真实后端）
export class ApiFileSystemStateMachine {
  private storageKey = 'translator_agent_tasks'; // 本地缓存作为备份
  private apiEnabled: boolean;
  private apiAvailable: boolean = false;
  
  // 轮询节流机制
  private lastApiCallTime: Record<string, number> = {}; // taskId -> timestamp
  private apiCallInterval: number = 2000; // 2秒最小间隔（频繁轮询）
  private fallbackToLocalTime: Record<string, number> = {}; // taskId -> fallback timestamp
  private fallbackToLocalTimeout: number = 10000; // 10秒后回退到本地存储（快速恢复）
  private consecutiveFailures: Record<string, number> = {}; // taskId -> failure count
  private maxConsecutiveFailures: number = 3; // 最大连续失败次数
  private globalLastApiCallTime: number = 0; // 全局API调用时间，用于全局限流
  private globalApiCallInterval: number = 1000; // 全局最小间隔1秒（快速响应）

  constructor() {
    const config = getApiConfig();
    this.apiEnabled = (import.meta as any).env?.VITE_ENABLE_API_INTEGRATION === 'true';
    console.log(`[API-FSM] Initialized - API Enabled: ${this.apiEnabled}, Base URL: ${config.baseUrl}`);
  }

  // 映射后端状态到前端状态
  private mapBackendStatus(backendStatus: string): TaskStatus {
    const statusMap: Record<string, TaskStatus> = {
      'pending': TaskStatus.PENDING,
      'created': TaskStatus.PENDING,
      'queued': TaskStatus.PENDING,
      'processing': TaskStatus.PROCESSING,
      'completed': TaskStatus.COMPLETED,
      'failed': TaskStatus.FAILED,
      'cancelled': TaskStatus.CANCELLED
    };
    
    return statusMap[backendStatus] || TaskStatus.PENDING;
  }

  // 初始化文件系统
  async initialize(): Promise<void> {
    if (!this.apiEnabled) {
      console.log('[API-FSM] API integration disabled, using localStorage only');
      return;
    }

    try {
      // 检查后端API连接
      this.apiAvailable = await checkApiHealth();
      if (!this.apiAvailable) {
        console.warn('[API-FSM] Backend API not available, falling back to localStorage');
      } else {
        console.log(`[API-FSM] Connected to backend API successfully`);
      }
    } catch (error) {
      console.error('[API-FSM] Failed to initialize:', error);
      this.apiAvailable = false;
    }
  }

  // 检查API是否可用
  isApiAvailable(): boolean {
    return this.apiEnabled && this.apiAvailable;
  }

  // 获取API配置
  getApiConfig() {
    return getApiConfig();
  }

  // 获取本地缓存数据（作为备份）
  private getLocalCache(): Record<string, Record<string, TaskState>> {
    if (typeof window === 'undefined' || !window.localStorage) {
      return {};
    }

    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : {};
    } catch (error) {
      console.error('[API-FSM] Failed to read from localStorage:', error);
      return {};
    }
  }

  // 保存本地缓存数据
  private saveLocalCache(tasks: Record<string, Record<string, TaskState>>): void {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(tasks));
    } catch (error) {
      console.error('[API-FSM] Failed to save to localStorage:', error);
    }
  }

  // 创建任务状态（优先使用后端API）
  async createTaskState(taskId: string, module: string, taskName: string): Promise<TaskState> {
    try {
      // 尝试使用后端API创建任务
      const apiResponse = await apiClient.createTask({
        module,
        taskName,
        files: [],
        instructions: 'Task created from frontend',
        options: {}
      });
      
      if (apiResponse.success && apiResponse.data) {
        // 使用后端返回的任务ID和状态
        // 提取实际的任务数据（后端返回 {success: true, data: task, ...}）
        // 后端返回格式: { success: true, data: task, message: "...", timestamp: "..." }
        // 需要提取嵌套的 data 字段
        const responseWrapper = apiResponse.data as any;
        const backendTask = responseWrapper?.data || responseWrapper;
        console.log('[API-FSM] API Response data:', backendTask);
        
        const taskData = backendTask;
        const backendTaskId = taskData.taskId || taskData.id || taskId;
        
        console.log(`[API-FSM] Created task via API: ${backendTaskId} in module ${module}`);
        
        // 创建基于后端响应的状态
        const initialState: TaskState = {
          taskId: backendTaskId,
          module: backendTask.module || backendTask.taskType || backendTask.task_type || module,
          status: this.mapBackendStatus(backendTask.status),
          progress: {
            current: backendTask.progress?.current || 0,
            total: backendTask.progress?.total || 100,
            percentage: backendTask.progress?.percentage || 0,
            message: backendTask.progress?.message || '任务已创建，等待处理',
            timestamp: new Date().toISOString()
          },
          memoryLayer: {
            conversationHistory: backendTask.memory?.conversationHistory || [],
            processingResults: backendTask.memory?.processingResults || [],
            intermediateData: backendTask.memory?.intermediateData || []
          },
          files: Array.isArray(backendTask.files) ? backendTask.files : [],
          createdAt: backendTask.createdAt || backendTask.created_at || new Date().toISOString(),
          updatedAt: backendTask.updatedAt || backendTask.updated_at || new Date().toISOString()
        };
        
        // 保存到本地缓存作为备份
        const allTasks = this.getLocalCache();
        if (!allTasks[module]) {
          allTasks[module] = {};
        }
        if (backendTaskId) {
          allTasks[module][backendTaskId] = initialState;
        }
        this.saveLocalCache(allTasks);
        
        // 触发任务处理（异步，不阻塞返回）
        console.log(`[API-FSM] About to trigger task processing for ${backendTaskId}`);
        this.triggerTaskProcessing(backendTaskId).then(() => {
          console.log(`[API-FSM] Task processing triggered successfully: ${backendTaskId}`);
        }).catch(error => {
          console.error(`[API-FSM] Failed to trigger task processing: ${backendTaskId}`, error);
        });
        
        return initialState;
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API create failed, using localStorage: ${apiResponse.error}`);
        return await this.createTaskStateLocal(taskId, module, taskName);
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      return await this.createTaskStateLocal(taskId, module, taskName);
    }
  }

  // 本地创建任务状态（回退方案）
  private async createTaskStateLocal(taskId: string, module: string, _taskName: string): Promise<TaskState> {
    const initialState: TaskState = {
      taskId,
      module,
      status: TaskStatus.PENDING,
      progress: {
        current: 0,
        total: 100,
        percentage: 0,
        message: '任务已创建，等待处理',
        timestamp: new Date().toISOString()
      },
      memoryLayer: {
        conversationHistory: [],
        processingResults: [],
        intermediateData: []
      },
      files: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    const allTasks = this.getLocalCache();
    if (!allTasks[module]) {
      allTasks[module] = {};
    }
    allTasks[module][taskId] = initialState;
    this.saveLocalCache(allTasks);

    console.log(`[API-FSM] Created task state locally: ${taskId} in module ${module}`);
    return initialState;
  }

  // 更新任务状态（优先使用后端API，带限流）
  async updateTaskState(
    taskId: string,
    module: string,
    updates: Partial<TaskState>
  ): Promise<TaskState> {
    const now = Date.now();
    
    // 全局限流检查
    const globalTimeSinceLastCall = now - this.globalLastApiCallTime;
    if (globalTimeSinceLastCall < this.globalApiCallInterval) {
      console.log(`[API-FSM] Global rate limit active for update, using localStorage fallback`);
      return await this.updateTaskStateLocal(taskId, module, updates);
    }
    
    // 任务级别限流检查
    const lastCall = this.lastApiCallTime[taskId] || 0;
    const timeSinceLastCall = now - lastCall;
    if (timeSinceLastCall < this.apiCallInterval) {
      console.log(`[API-FSM] Update API call too frequent for ${taskId}, using localStorage fallback`);
      return await this.updateTaskStateLocal(taskId, module, updates);
    }
    
    try {
      // 尝试使用后端API更新任务
      this.lastApiCallTime[taskId] = now;
      this.globalLastApiCallTime = now;
      const apiResponse = await apiClient.updateTaskStatus(taskId, module, updates);
      
      if (apiResponse.success) {
        console.log(`[API-FSM] Updated task via API: ${taskId}`);
        
        // 同时更新本地缓存
        const allTasks = this.getLocalCache();
        if (!allTasks[module] || !allTasks[module][taskId]) {
          // 如果本地没有，创建本地记录
          if (!allTasks[module]) {
            allTasks[module] = {};
          }
          allTasks[module][taskId] = {
            taskId,
            module,
            ...updates,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          } as TaskState;
        } else {
          const currentState = allTasks[module][taskId];
          const updatedState: TaskState = {
            ...currentState,
            ...updates,
            updatedAt: new Date().toISOString()
          };
          allTasks[module][taskId] = updatedState;
        }
        this.saveLocalCache(allTasks);
        
        // 返回更新后的状态
        return await this.readTaskState(taskId, module);
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API update failed, using localStorage: ${apiResponse.error}`);
        return await this.updateTaskStateLocal(taskId, module, updates);
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      return await this.updateTaskStateLocal(taskId, module, updates);
    }
  }

  // 本地更新任务状态（回退方案）
  private async updateTaskStateLocal(
    taskId: string,
    module: string,
    updates: Partial<TaskState>
  ): Promise<TaskState> {
    const allTasks = this.getLocalCache();
    
    if (!allTasks[module] || !allTasks[module][taskId]) {
      throw new Error(`Task ${taskId} not found in module ${module}`);
    }

    const currentState = allTasks[module][taskId];
    const updatedState: TaskState = {
      ...currentState,
      ...updates,
      updatedAt: new Date().toISOString()
    };

    allTasks[module][taskId] = updatedState;
    this.saveLocalCache(allTasks);

    console.log(`[API-FSM] Updated task state locally: ${taskId}`);
    return updatedState;
  }

  // 读取任务状态（优先使用后端API，带轮询节流）
  async readTaskState(taskId: string, module: string): Promise<TaskState> {
    const now = Date.now();
    
    // 全局限流：防止所有任务同时调用API
    const globalTimeSinceLastCall = now - this.globalLastApiCallTime;
    if (globalTimeSinceLastCall < this.globalApiCallInterval) {
      console.log(`[API-FSM] Global rate limit active, using localStorage fallback`);
      return await this.readTaskStateLocal(taskId, module);
    }
    
    const lastCall = this.lastApiCallTime[taskId] || 0;
    const timeSinceLastCall = now - lastCall;
    
    // 检查是否应该使用本地存储（频率限制或回退状态）
    if (timeSinceLastCall < this.apiCallInterval) {
      console.log(`[API-FSM] API call too frequent for ${taskId}, using localStorage fallback`);
      return await this.readTaskStateLocal(taskId, module);
    }
    
    // 检查是否处于回退到本地存储的状态
    const fallbackTime = this.fallbackToLocalTime[taskId] || 0;
    if (fallbackTime > 0 && now - fallbackTime < this.fallbackToLocalTimeout) {
      console.log(`[API-FSM] Using localStorage fallback for ${taskId} (rate limited)`);
      return await this.readTaskStateLocal(taskId, module);
    }
    
    // 检查连续失败次数
    const failureCount = this.consecutiveFailures[taskId] || 0;
    if (failureCount >= this.maxConsecutiveFailures) {
      console.log(`[API-FSM] Too many consecutive failures for ${taskId}, using localStorage fallback`);
      return await this.readTaskStateLocal(taskId, module);
    }
    
    try {
      // 尝试使用后端API读取任务
      this.lastApiCallTime[taskId] = now; // 记录调用时间
      this.globalLastApiCallTime = now; // 更新全局调用时间
      const apiResponse = await apiClient.getTaskStatus(taskId);
      
      if (apiResponse.success && apiResponse.data) {
        console.log(`[API-FSM] Read task state via API: ${taskId}`);
        // 重置回退状态和失败计数
        delete this.fallbackToLocalTime[taskId];
        delete this.consecutiveFailures[taskId];
        
        // 同时更新本地缓存
        const allTasks = this.getLocalCache();
        if (!allTasks[module]) {
          allTasks[module] = {};
        }
        // 将API响应转换为TaskState格式
        const apiStatus = apiResponse.data.status;
        let taskStatus: TaskStatus;
        
        // 映射API状态到TaskStatus
        switch (apiStatus) {
          case 'created':
          case 'queued':
            taskStatus = TaskStatus.PENDING;
            break;
          case 'processing':
            taskStatus = TaskStatus.PROCESSING;
            break;
          case 'completed':
            taskStatus = TaskStatus.COMPLETED;
            break;
          case 'failed':
            taskStatus = TaskStatus.FAILED;
            break;
          default:
            taskStatus = TaskStatus.PENDING;
        }

        const taskState: TaskState = {
          ...apiResponse.data,
          module: module, // 确保包含模块信息
          status: taskStatus,
          progress: (apiResponse.data.progress as any) || {
            current: 0,
            total: 100,
            percentage: 0,
            message: '任务已创建',
            timestamp: new Date().toISOString()
          },
          memoryLayer: apiResponse.data.memoryLayer || {
            conversationHistory: [],
            processingResults: [],
            intermediateData: []
          },
          files: apiResponse.data.files || [],
          createdAt: apiResponse.data.createdAt || apiResponse.data.created_at || new Date().toISOString(),
          updatedAt: apiResponse.data.updatedAt || apiResponse.data.updated_at || new Date().toISOString()
        };
        allTasks[module][taskId] = taskState;
        this.saveLocalCache(allTasks);
        
        return taskState;
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API read failed, using localStorage: ${apiResponse.error}`);
        return await this.readTaskStateLocal(taskId, module);
      }
    } catch (error: any) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      
      // 检查是否是429频率限制错误
      if (error.message && (error.message.includes('HTTP 429') || 
          error.message?.includes('请求过于频繁') || 
          error.message?.includes('rate limit'))) {
        console.warn(`[API-FSM] Rate limit hit for ${taskId}, switching to localStorage fallback`);
        this.fallbackToLocalTime[taskId] = Date.now();
        // 增加失败计数
        this.consecutiveFailures[taskId] = (this.consecutiveFailures[taskId] || 0) + 1;
      } else {
        // 增加失败计数
        this.consecutiveFailures[taskId] = (this.consecutiveFailures[taskId] || 0) + 1;
      }
      
      return await this.readTaskStateLocal(taskId, module);
    }
  }

  // 本地读取任务状态（回退方案）
  private async readTaskStateLocal(taskId: string, module: string): Promise<TaskState> {
    const allTasks = this.getLocalCache();
    
    if (!allTasks[module] || !allTasks[module][taskId]) {
      throw new Error(`Task ${taskId} not found in module ${module}`);
    }

    console.log(`[API-FSM] Read task state locally: ${taskId}`);
    // 重置失败计数，因为本地读取成功
    delete this.consecutiveFailures[taskId];
    return allTasks[module][taskId];
  }

  // 更新任务进度（优先使用后端API）
  async updateTaskProgress(
    taskId: string,
    module: string,
    progress: Partial<ProgressInfo>
  ): Promise<TaskState> {
    const currentState = await this.readTaskState(taskId, module);
    
    const updatedProgress: ProgressInfo = {
      ...currentState.progress,
      ...progress,
      timestamp: new Date().toISOString()
    };

    // 尝试使用后端API更新进度
    try {
      const apiResponse = await apiClient.updateTaskProgress(taskId, module, updatedProgress);
      
      if (apiResponse.success) {
        console.log(`[API-FSM] Updated task progress via API: ${taskId}`);
        
        // 同时更新本地缓存
        const allTasks = this.getLocalCache();
        if (allTasks[module] && allTasks[module][taskId]) {
          allTasks[module][taskId].progress = updatedProgress;
          allTasks[module][taskId].status = progress.percentage === 100 ? TaskStatus.COMPLETED : TaskStatus.PROCESSING;
          allTasks[module][taskId].updatedAt = new Date().toISOString();
          this.saveLocalCache(allTasks);
        }
        
        return await this.readTaskState(taskId, module);
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API progress update failed, using localStorage: ${apiResponse.error}`);
        return await this.updateTaskStateLocal(taskId, module, {
          progress: updatedProgress,
          status: progress.percentage === 100 ? TaskStatus.COMPLETED : TaskStatus.PROCESSING
        });
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      return await this.updateTaskStateLocal(taskId, module, {
        progress: updatedProgress,
        status: progress.percentage === 100 ? TaskStatus.COMPLETED : TaskStatus.PROCESSING
      });
    }
  }

  // 添加文件到任务（优先使用后端API）
  async addFileToTask(
    taskId: string,
    module: string,
    filePath: string,
    status: 'uploaded' | 'processed' | 'failed'
  ): Promise<TaskState> {
    const currentState = await this.readTaskState(taskId, module);
    
    // 后端返回的 files 是字符串数组，直接添加到数组中
    const updatedFiles = Array.isArray(currentState.files) 
      ? [...currentState.files, filePath]
      : [filePath];

    // 尝试使用后端API添加文件
    try {
      const apiResponse = await apiClient.addFileToTask(taskId, module, filePath, status);
      
      if (apiResponse.success) {
        console.log(`[API-FSM] Added file via API: ${filePath} to task ${taskId}`);
        
        // 同时更新本地缓存
        const allTasks = this.getLocalCache();
        if (allTasks[module] && allTasks[module][taskId]) {
          allTasks[module][taskId].files = updatedFiles;
          allTasks[module][taskId].updatedAt = new Date().toISOString();
          this.saveLocalCache(allTasks);
        }
        
        return await this.readTaskState(taskId, module);
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API add file failed, using localStorage: ${apiResponse.error}`);
        return await this.updateTaskStateLocal(taskId, module, {
          files: updatedFiles
        });
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      return await this.updateTaskStateLocal(taskId, module, {
        files: updatedFiles
      });
    }
  }

  // 获取任务文件列表（优先使用后端API）
  async getTaskFiles(taskId: string, module: string): Promise<any[]> {
    try {
      // 尝试使用后端API获取文件列表
      const apiResponse = await apiClient.getTaskFiles(taskId);
      
      if (apiResponse.success && apiResponse.data?.files) {
        console.log(`[API-FSM] Retrieved task files via API: ${taskId}`);
        // 处理后端返回的文件数据格式
        if (Array.isArray(apiResponse.data.files)) {
          // 如果是字符串数组，转换为对象格式
          return apiResponse.data.files.map((path: string) => ({
            path,
            name: path.split('/').pop() || path,
            type: 'video'
          }));
        } else if (Array.isArray(apiResponse.data.files?.uploaded)) {
          // 如果是对象格式，直接返回
          return apiResponse.data.files.uploaded.map((path: string) => ({
            path,
            name: path.split('/').pop() || path,
            type: 'video'
          }));
        }
        return apiResponse.data.files || [];
      } else {
        // API失败，从任务状态中获取文件列表
        console.warn(`[API-FSM] API get files failed, using task state: ${apiResponse.error}`);
        const taskState = await this.readTaskState(taskId, module);
        
        // 处理不同格式的文件列表
        if (Array.isArray(taskState.files)) {
          // 文件列表是字符串数组
          return taskState.files.map((path: string) => ({ path, name: path.split('/').pop() || path, type: 'file' }));
        }
        return [];
      }
    } catch (error) {
      // 异常处理，从任务状态中获取文件列表
      console.error(`[API-FSM] API error, using task state:`, error);
      const taskState = await this.readTaskState(taskId, module);
      
      // 处理不同格式的文件列表
      if (Array.isArray(taskState.files)) {
        // 文件列表是字符串数组
        return taskState.files.map((path: string) => ({ path, name: path.split('/').pop() || path, type: 'file' }));
      }
      return [];
    }
  }

  // 下载任务文件（优先使用后端API）
  async downloadTaskFile(taskId: string, fileName: string): Promise<any> {
    try {
      // 尝试使用后端API下载文件
      const response = await apiClient.downloadTaskFile(taskId, fileName);
      
      if (response.ok) {
        console.log(`[API-FSM] Downloaded file via API: ${fileName} from task ${taskId}`);
        // 返回响应对象，让前端处理实际的文件下载
        return response;
      } else {
        // API失败，返回错误信息
        console.warn(`[API-FSM] API download file failed: ${response.status} ${response.statusText}`);
        return { error: `Download failed: ${response.status} ${response.statusText}` };
      }
    } catch (error) {
      // 异常处理，返回错误信息
      console.error(`[API-FSM] API error during file download:`, error);
      return { error: error instanceof Error ? error.message : String(error) };
    }
  }

  // 添加对话历史到记忆层（优先使用后端API）
  async addToMemoryLayer(
    taskId: string,
    module: string,
    type: 'conversation' | 'result' | 'intermediate',
    data: any
  ): Promise<TaskState> {
    const currentState = await this.readTaskState(taskId, module);
    
    const memoryKey = type === 'conversation' ? 'conversationHistory' : 
                      type === 'result' ? 'processingResults' : 'intermediateData';
    
    const updatedMemoryLayer = {
      ...currentState.memoryLayer,
      [memoryKey]: [...currentState.memoryLayer[memoryKey], data]
    };

    // 尝试使用后端API添加到记忆层
    try {
      const apiResponse = await apiClient.addToMemoryLayer(taskId, module, type, data);
      
      if (apiResponse.success) {
        console.log(`[API-FSM] Added to memory layer via API: ${type} to task ${taskId}`);
        
        // 同时更新本地缓存
        const allTasks = this.getLocalCache();
        if (allTasks[module] && allTasks[module][taskId]) {
          allTasks[module][taskId].memoryLayer = updatedMemoryLayer;
          allTasks[module][taskId].updatedAt = new Date().toISOString();
          this.saveLocalCache(allTasks);
        }
        
        return await this.readTaskState(taskId, module);
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API add to memory failed, using localStorage: ${apiResponse.error}`);
        return await this.updateTaskStateLocal(taskId, module, {
          memoryLayer: updatedMemoryLayer
        });
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      return await this.updateTaskStateLocal(taskId, module, {
        memoryLayer: updatedMemoryLayer
      });
    }
  }

  // 获取模块的所有任务（优先使用后端API）
  async getModuleTasks(module: string): Promise<TaskState[]> {
    try {
      // 尝试使用后端API获取任务列表
      const apiResponse = await apiClient.getModuleTasks(module);
      
      if (apiResponse.success && apiResponse.data) {
        console.log(`[API-FSM] Retrieved tasks via API for module: ${module}`);
        
        // 同时更新本地缓存
        const allTasks = this.getLocalCache();
        allTasks[module] = {};
        
        // 处理API响应数据（可能是数组或对象）
        const tasksArray = Array.isArray(apiResponse.data) ? apiResponse.data : 
                          [];
        
        // 简化处理，直接返回API响应数据
        return (tasksArray || []).map((task: any) => ({
          ...task,
          module: module
        })).sort((a: any, b: any) => 
          new Date(b.createdAt || b.created_at).getTime() - new Date(a.createdAt || a.created_at).getTime()
        );
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API get tasks failed, using localStorage: ${apiResponse.error}`);
        return await this.getModuleTasksLocal(module);
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      return await this.getModuleTasksLocal(module);
    }
  }

  // 本地获取模块任务（回退方案）
  private async getModuleTasksLocal(module: string): Promise<TaskState[]> {
    const allTasks = this.getLocalCache();
    
    if (!allTasks[module]) {
      return [];
    }

    const tasks = Object.values(allTasks[module]);
    return tasks.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  // 删除任务（优先使用后端API）
  async deleteTask(taskId: string, module: string): Promise<void> {
    try {
      // 尝试使用后端API删除任务
      const apiResponse = await apiClient.deleteTask(taskId);
      
      if (apiResponse.success) {
        console.log(`[API-FSM] Deleted task via API: ${taskId}`);
        
        // 同时删除本地缓存
        const allTasks = this.getLocalCache();
        if (allTasks[module] && allTasks[module][taskId]) {
          delete allTasks[module][taskId];
          this.saveLocalCache(allTasks);
        }
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API delete failed, using localStorage: ${apiResponse.error}`);
        await this.deleteTaskLocal(taskId, module);
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      await this.deleteTaskLocal(taskId, module);
    }
  }

  // 本地删除任务（回退方案）
  private async deleteTaskLocal(taskId: string, module: string): Promise<void> {
    const allTasks = this.getLocalCache();
    
    if (allTasks[module] && allTasks[module][taskId]) {
      delete allTasks[module][taskId];
      this.saveLocalCache(allTasks);
      console.log(`[API-FSM] Deleted task locally: ${taskId}`);
    }
  }

  // 清理完成的任务（优先使用后端API）
  async cleanupCompletedTasks(maxAge: number = 30): Promise<void> {
    try {
      // 尝试使用后端API清理任务
      const apiResponse = await apiClient.cleanupTasks(maxAge);
      
      if (apiResponse.success) {
        console.log(`[API-FSM] Cleaned up tasks via API`);
        
        // 同时清理本地缓存
        const allTasks = this.getLocalCache();
        const currentDate = new Date();
        
        for (const module in allTasks) {
          for (const taskId in allTasks[module]) {
            const task = allTasks[module][taskId];
            if (task.status === TaskStatus.COMPLETED && task.completedAt) {
              const completedDate = new Date(task.completedAt);
              const daysOld = (currentDate.getTime() - completedDate.getTime()) / (1000 * 60 * 60 * 24);
              
              if (daysOld > maxAge) {
                delete allTasks[module][taskId];
              }
            }
          }
        }
        
        this.saveLocalCache(allTasks);
      } else {
        // API失败，回退到本地清理
        console.warn(`[API-FSM] API cleanup failed, using localStorage: ${apiResponse.error}`);
        await this.cleanupCompletedTasksLocal(maxAge);
      }
    } catch (error) {
      // 异常处理，回退到本地清理
      console.error(`[API-FSM] API error, using localStorage:`, error);
      await this.cleanupCompletedTasksLocal(maxAge);
    }
  }

  // 本地清理完成的任务（回退方案）
  private async cleanupCompletedTasksLocal(maxAge: number = 30): Promise<void> {
    const allTasks = this.getLocalCache();
    const currentDate = new Date();
    
    for (const module in allTasks) {
      for (const taskId in allTasks[module]) {
        const task = allTasks[module][taskId];
        if (task.status === TaskStatus.COMPLETED && task.completedAt) {
          const completedDate = new Date(task.completedAt);
          const daysOld = (currentDate.getTime() - completedDate.getTime()) / (1000 * 60 * 60 * 24);
          
          if (daysOld > maxAge) {
            delete allTasks[module][taskId];
          }
        }
      }
    }
    
    this.saveLocalCache(allTasks);
    console.log(`[API-FSM] Cleaned up completed tasks locally`);
  }

  // 获取所有任务（用于调试）
  async getAllTasks(): Promise<Record<string, Record<string, TaskState>>> {
    try {
      // 尝试使用后端API获取所有任务
      const apiResponse = await apiClient.getAllTasks();
      
      if (apiResponse.success && apiResponse.data) {
        console.log(`[API-FSM] Retrieved all tasks via API`);
        
        // 同时更新本地缓存
        this.saveLocalCache(apiResponse.data);
        
        return apiResponse.data;
      } else {
        // API失败，回退到本地存储
        console.warn(`[API-FSM] API get all tasks failed, using localStorage: ${apiResponse.error}`);
        return this.getLocalCache();
      }
    } catch (error) {
      // 异常处理，回退到本地存储
      console.error(`[API-FSM] API error, using localStorage:`, error);
      return this.getLocalCache();
    }
  }

  // 获取任务统计信息
  async getTaskStats(module?: string): Promise<Record<string, any>> {
    try {
      // 尝试使用后端API获取统计信息
      const apiResponse = await apiClient.getTaskStats(module);
      
      if (apiResponse.success && apiResponse.data) {
        console.log(`[API-FSM] Retrieved task stats via API`);
        return apiResponse.data;
      } else {
        // API失败，计算本地统计
        console.warn(`[API-FSM] API get stats failed, calculating locally: ${apiResponse.error}`);
        return await this.calculateTaskStatsLocal(module);
      }
    } catch (error) {
      // 异常处理，计算本地统计
      console.error(`[API-FSM] API error, calculating locally:`, error);
      return await this.calculateTaskStatsLocal(module);
    }
  }

  // 本地计算任务统计（回退方案）
  private async calculateTaskStatsLocal(module?: string): Promise<Record<string, any>> {
    const allTasks = this.getLocalCache();
    const targetModules = module ? [module] : Object.keys(allTasks);
    
    const stats = {
      total: 0,
      byStatus: {} as Record<string, number>,
      byModule: {} as Record<string, number>,
      recent: [] as TaskState[]
    };

    for (const mod of targetModules) {
      if (allTasks[mod]) {
        const tasks = Object.values(allTasks[mod]);
        stats.total += tasks.length;
        stats.byModule[mod] = tasks.length;

        tasks.forEach(task => {
          stats.byStatus[task.status] = (stats.byStatus[task.status] || 0) + 1;
        });

        // 最近的任务（前10个）
        if (stats.recent.length < 10) {
          stats.recent = [...stats.recent, ...tasks]
            .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
            .slice(0, 10);
        }
      }
    }

    return stats;
  }

  // 上传实际文件到任务
  async uploadTaskFile(taskId: string, file: File): Promise<TaskState> {
    try {
      const apiResponse = await apiClient.uploadTaskFile(taskId, file);
      
      if (apiResponse.success) {
        console.log(`[API-FSM] Uploaded file via API: ${file.name} to task ${taskId}`);
        
        // 同时更新本地缓存
        const allTasks = this.getLocalCache();
        // 需要知道模块信息，这里假设是当前模块
        const module = 'video-translate'; // 在实际应用中应该从参数获取
        if (allTasks[module] && allTasks[module][taskId]) {
          // 添加上传的文件路径到文件列表
          // 后端返回的格式是 {success: true, task_id: "...", file_path: "...", filename: "..."}
          // 而不是 {success: true, data: {file_path: "...", file_name: "..."}}
          const filePath = apiResponse.data?.file_path || apiResponse.data?.file_name;
          if (filePath) {
            allTasks[module][taskId].files = Array.isArray(allTasks[module][taskId].files) 
              ? [...allTasks[module][taskId].files, filePath]
              : [filePath];
            allTasks[module][taskId].updatedAt = new Date().toISOString();
            this.saveLocalCache(allTasks);
          }
        }
        
        return await this.readTaskState(taskId, module);
      } else {
        // API失败，抛出错误
        throw new Error(apiResponse.error || 'File upload failed');
      }
    } catch (error) {
      // 异常处理，抛出错误
      console.error(`[API-FSM] API error during file upload:`, error);
      throw error;
    }
  }

  // 触发任务处理（调用后端处理端点）
  private async triggerTaskProcessing(taskId: string): Promise<void> {
    console.log(`[API-FSM] triggerTaskProcessing called for task ${taskId}`);
    try {
      console.log(`[API-FSM] Calling apiClient.processTask for ${taskId}`);
      const apiResponse = await apiClient.processTask(taskId);
      console.log(`[API-FSM] processTask response:`, apiResponse);
      if (apiResponse.success) {
        console.log(`[API-FSM] Task processing triggered successfully: ${taskId}`);
      } else {
        console.warn(`[API-FSM] Failed to trigger task processing: ${apiResponse.error}`);
      }
    } catch (error) {
      console.error(`[API-FSM] Error triggering task processing:`, error);
    }
  }
}

// 全局API文件系统状态管理器实例
export const apiFsm = new ApiFileSystemStateMachine();