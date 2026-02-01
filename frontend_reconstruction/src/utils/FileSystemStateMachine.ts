// 任务状态枚举
export enum TaskStatus {
  PENDING = 'pending',
  QUEUED = 'queued',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// 进度信息接口
export interface ProgressInfo {
  current: number;
  total: number;
  percentage: number;
  message: string;
  timestamp: string;
}

// 任务状态接口
export interface TaskState {
  taskId: string;
  module: string;
  status: TaskStatus;
  progress: ProgressInfo;
  memoryLayer: {
    conversationHistory: any[];
    processingResults: any[];
    intermediateData: any[];
  };
  files: string[];
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  error?: string;
}

// 文件系统状态管理器（浏览器环境模拟版本）
export class FileSystemStateMachine {
  private storageKey = 'translator_agent_tasks';

  constructor() {
    console.log(`[FSM] Initialized with localStorage`);
  }

  // 初始化文件系统
  async initialize(): Promise<void> {
    try {
      // 检查 localStorage 是否可用
      if (typeof window === 'undefined' || !window.localStorage) {
        console.warn('[FSM] localStorage not available, using memory storage');
      } else {
        console.log(`[FSM] Initialized with localStorage`);
      }
    } catch (error) {
      console.error('[FSM] Failed to initialize:', error);
      throw error;
    }
  }

  // 获取所有任务数据
  private getAllTasks(): Record<string, Record<string, TaskState>> {
    if (typeof window === 'undefined' || !window.localStorage) {
      return {};
    }

    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : {};
    } catch (error) {
      console.error('[FSM] Failed to read from localStorage:', error);
      return {};
    }
  }

  // 保存所有任务数据
  private saveAllTasks(tasks: Record<string, Record<string, TaskState>>): void {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(tasks));
    } catch (error) {
      console.error('[FSM] Failed to save to localStorage:', error);
    }
  }

  // 创建任务状态
  async createTaskState(taskId: string, module: string, _taskName: string): Promise<TaskState> {
    // 创建初始状态
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

    // 保存到存储
    const allTasks = this.getAllTasks();
    if (!allTasks[module]) {
      allTasks[module] = {};
    }
    allTasks[module][taskId] = initialState;
    this.saveAllTasks(allTasks);

    console.log(`[FSM] Created task state: ${taskId} in module ${module}`);
    return initialState;
  }

  // 更新任务状态
  async updateTaskState(
    taskId: string,
    module: string,
    updates: Partial<TaskState>
  ): Promise<TaskState> {
    const allTasks = this.getAllTasks();
    
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
    this.saveAllTasks(allTasks);

    console.log(`[FSM] Updated task state: ${taskId}`);
    return updatedState;
  }

  // 读取任务状态
  async readTaskState(taskId: string, module: string): Promise<TaskState> {
    const allTasks = this.getAllTasks();
    
    if (!allTasks[module] || !allTasks[module][taskId]) {
      throw new Error(`Task ${taskId} not found in module ${module}`);
    }

    console.log(`[FSM] Read task state: ${taskId}`);
    return allTasks[module][taskId];
  }

  // 更新任务进度
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

    return await this.updateTaskState(taskId, module, {
      progress: updatedProgress,
      status: progress.percentage === 100 ? TaskStatus.COMPLETED : TaskStatus.PROCESSING
    });
  }

  // 添加文件到任务
  async addFileToTask(
    taskId: string,
    module: string,
    filePath: string,
    status: 'uploaded' | 'processed' | 'failed'
  ): Promise<TaskState> {
    const currentState = await this.readTaskState(taskId, module);
    
    // 直接添加到文件数组中
    const updatedFiles = Array.isArray(currentState.files) 
      ? [...currentState.files, filePath]
      : [filePath];

    return await this.updateTaskState(taskId, module, {
      files: updatedFiles
    });
  }

  // 添加对话历史到记忆层
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

    return await this.updateTaskState(taskId, module, {
      memoryLayer: updatedMemoryLayer
    });
  }

  // 获取模块的所有任务
  async getModuleTasks(module: string): Promise<TaskState[]> {
    const allTasks = this.getAllTasks();
    
    if (!allTasks[module]) {
      return [];
    }

    const tasks = Object.values(allTasks[module]);
    return tasks.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  // 删除任务
  async deleteTask(taskId: string, module: string): Promise<void> {
    const allTasks = this.getAllTasks();
    
    if (allTasks[module] && allTasks[module][taskId]) {
      delete allTasks[module][taskId];
      this.saveAllTasks(allTasks);
      console.log(`[FSM] Deleted task: ${taskId}`);
    }
  }

  // 清理完成的任务
  async cleanupCompletedTasks(maxAge: number = 30): Promise<void> {
    const allTasks = this.getAllTasks();
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
    
    this.saveAllTasks(allTasks);
  }
}

// 全局状态管理器实例
export const fsm = new FileSystemStateMachine();