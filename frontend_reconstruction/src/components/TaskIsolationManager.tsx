import React, { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { 
  FolderOpen, 
  Shield, 
  Database,
  Layers,
  Activity,
  AlertCircle,
  Loader2,
  EyeOff
} from 'lucide-react';
import { FileSystemStateMachine, TaskStatus } from '../utils/FileSystemStateMachine';
import { ApiFileSystemStateMachine, apiFsm } from '../utils/ApiFileSystemStateMachine';
import { observationMask } from '../utils/ObservationMask';

// 任务隔离上下文
interface TaskIsolationContextType {
  currentTaskId: string | null;
  currentModule: string | null;
  taskWorkspace: string | null;
  createSubAgentSession: (module: string, taskName: string) => Promise<string>;
  switchTask: (taskId: string) => void;
  getTaskContext: (taskId: string) => TaskContext | null;
  clearTaskContext: (taskId: string) => void;
  setCurrentTaskId: (taskId: string | null) => void;
}

interface TaskContext {
  id: string;
  module: string;
  name: string;
  workspace: string;
  memoryLayer: {
    conversationHistory: any[];
    processingResults: any[];
    intermediateData: any[];
  };
  status: 'active' | 'completed' | 'paused' | 'error';
  createdAt: string;
  updatedAt: string;
}

const TaskIsolationContext = createContext<TaskIsolationContextType | null>(null);

export const useTaskIsolation = () => {
  const context = useContext(TaskIsolationContext);
  if (!context) {
    throw new Error('useTaskIsolation must be used within TaskIsolationProvider');
  }
  return context;
};

interface TaskIsolationManagerProps {
  children: React.ReactNode;
}

export const TaskIsolationManager: React.FC<TaskIsolationManagerProps> = ({ children }) => {
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [currentModule, setCurrentModule] = useState<string | null>(null);
  const [taskWorkspace, setTaskWorkspace] = useState<string | null>(null);
  const [taskContexts, setTaskContexts] = useState<Map<string, TaskContext>>(new Map());
  const [fsm, setFsm] = useState<ApiFileSystemStateMachine | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  // 初始化文件系统状态机
  useEffect(() => {
    const initializeFSM = async () => {
      try {
        // 使用API集成的状态机
        await apiFsm.initialize();
        setFsm(apiFsm);
        console.log('[Task Isolation] API file system state machine initialized');
      } catch (error) {
        console.error('[Task Isolation] Failed to initialize API FSM:', error);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeFSM();
  }, []);

  // 创建子智能体会话
  const createSubAgentSession = useCallback(async (module: string, taskName: string): Promise<string> => {
    if (!fsm) {
      throw new Error('File system state machine not initialized');
    }

    // 生成临时任务ID（用于前端标识）
    const tempTaskId = `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      // 使用文件系统状态机创建任务状态（会使用后端返回的真实任务ID）
      const taskState = await fsm.createTaskState(tempTaskId, module, taskName);
      
      // 使用后端返回的真实任务ID
      const taskId = taskState.taskId;
      const workspace = `tasks/${module}/${taskId}`;
      
      const newTaskContext: TaskContext = {
        id: taskId,
        module,
        name: taskName,
        workspace,
        memoryLayer: {
          conversationHistory: taskState.memoryLayer.conversationHistory,
          processingResults: taskState.memoryLayer.processingResults,
          intermediateData: taskState.memoryLayer.intermediateData
        },
        status: 'active',
        createdAt: taskState.createdAt,
        updatedAt: taskState.updatedAt
      };

      setTaskContexts(prev => {
        const newMap = new Map(prev);
        newMap.set(taskId, newTaskContext);
        return newMap;
      });

      setCurrentTaskId(taskId);
      setCurrentModule(module);
      setTaskWorkspace(workspace);

      console.log(`[Task Isolation] Created sub-agent session: ${taskId}`);
      console.log(`[Task Isolation] Workspace: ${workspace}`);
      console.log(`[Task Isolation] Module: ${module}`);
      console.log(`[Task Isolation] Task state persisted to: ${workspace}/status.json`);

      return taskId;
    } catch (error) {
      console.error(`[Task Isolation] Failed to create sub-agent session:`, error);
      throw error;
    }
  }, [fsm]);

  // 切换任务
  const switchTask = (taskId: string) => {
    const task = taskContexts.get(taskId);
    if (task) {
      setCurrentTaskId(taskId);
      setCurrentModule(task.module);
      setTaskWorkspace(task.workspace);
      console.log(`[Task Isolation] Switched to task: ${taskId}`);
    }
  };

  // 获取任务上下文
  const getTaskContext = (taskId: string): TaskContext | null => {
    return taskContexts.get(taskId) || null;
  };

  // 清除任务上下文
  const clearTaskContext = (taskId: string) => {
    setTaskContexts(prev => {
      const newMap = new Map(prev);
      newMap.delete(taskId);
      return newMap;
    });
    
    if (currentTaskId === taskId) {
      setCurrentTaskId(null);
      setCurrentModule(null);
      setTaskWorkspace(null);
    }
    
    console.log(`[Task Isolation] Cleared task context: ${taskId}`);
  };



  return (
    <TaskIsolationContext.Provider
      value={{
        currentTaskId,
        currentModule,
        taskWorkspace,
        createSubAgentSession,
        switchTask,
        getTaskContext,
        clearTaskContext,
        setCurrentTaskId
      }}
    >
      {isInitializing ? (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
            <p className="text-gray-600 dark:text-gray-400">正在初始化文件系统状态机...</p>
          </div>
        </div>
      ) : (
        children
      )}
    </TaskIsolationContext.Provider>
  );
};

// 任务隔离状态指示器组件
export const TaskIsolationIndicator: React.FC = () => {
  const { currentTaskId, currentModule, taskWorkspace } = useTaskIsolation();

  if (!currentTaskId) {
    return null;
  }

  return (
    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mb-4">
      <div className="flex items-center gap-2 mb-2">
        <Shield className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        <span className="text-sm font-semibold text-blue-900 dark:text-blue-100">
          任务隔离模式
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-1">
          <Database className="w-3 h-3 text-blue-500" />
          <span className="text-blue-700 dark:text-blue-300">任务ID: {currentTaskId.substr(0, 8)}...</span>
        </div>
        <div className="flex items-center gap-1">
          <Layers className="w-3 h-3 text-blue-500" />
          <span className="text-blue-700 dark:text-blue-300">模块: {currentModule}</span>
        </div>
        <div className="flex items-center gap-1 col-span-2">
          <FolderOpen className="w-3 h-3 text-blue-500" />
          <span className="text-blue-700 dark:text-blue-300 truncate">
            工作空间: {taskWorkspace}
          </span>
        </div>
      </div>
    </div>
  );
};

// 模块化历史任务列表组件
export const ModularTaskList: React.FC<{ module: string }> = ({ module }) => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { switchTask, clearTaskContext } = useTaskIsolation();
  const [fsm, setFsm] = useState<ApiFileSystemStateMachine | null>(null);

  // 初始化文件系统状态机
  useEffect(() => {
    const initializeFSM = async () => {
      try {
        // 使用API集成的状态机
        await apiFsm.initialize();
        setFsm(apiFsm);
      } catch (error) {
        console.error('[ModularTaskList] Failed to initialize API FSM:', error);
      }
    };

    initializeFSM();
  }, []);

  useEffect(() => {
    // 从文件系统加载模块化任务
    const loadModuleTasks = async () => {
      if (!fsm) return;

      setLoading(true);
      
      try {
        // 从文件系统状态机加载真实任务
        const moduleTasks = await fsm.getModuleTasks(module);
        
        // 转换为UI需要的格式
        const formattedTasks = moduleTasks.map(task => ({
          id: task.taskId,
          name: task.taskId,
          status: task.status,
          createdAt: new Date(task.createdAt).toLocaleString('zh-CN'),
          progress: task.progress.percentage,
          result: task.status === TaskStatus.COMPLETED ? '处理完成' : undefined,
          error: task.status === TaskStatus.ERROR ? task.error : undefined
        }));

        setTasks(formattedTasks);
      } catch (error) {
        console.error(`[ModularTaskList] Failed to load tasks for module ${module}:`, error);
        // 如果失败，显示模拟数据
        const mockTasks = [
          {
            id: `task-${module}-1`,
            name: `${module} 任务 1`,
            status: 'completed',
            createdAt: '2026-01-21 10:30:00',
            progress: 100,
            result: '处理完成'
          },
          {
            id: `task-${module}-2`,
            name: `${module} 任务 2`,
            status: 'processing',
            createdAt: '2026-01-21 11:15:00',
            progress: 65
          }
        ];
        setTasks(mockTasks);
      } finally {
        setLoading(false);
      }
    };

    loadModuleTasks();
  }, [module, fsm]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
      case 'completed':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
      case 'in_progress':
      case 'processing':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300';
      case 'error':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'pending':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'paused':
        return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'success':
      case 'completed':
        return '完成';
      case 'in_progress':
      case 'processing':
        return '处理中';
      case 'error':
        return '错误';
      case 'pending':
        return '待处理';
      case 'paused':
        return '已暂停';
      default:
        return '未知';
    }
  };

  if (loading) {
    return (
      <div className="text-center py-4 text-gray-500 dark:text-gray-400">
        加载中...
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {tasks.length === 0 ? (
        <div className="text-center py-4 text-gray-500 dark:text-gray-400">
          暂无历史任务
        </div>
      ) : (
        tasks.map(task => (
          <div
            key={task.id}
            className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
            onClick={() => switchTask(task.id)}
          >
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {task.name}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {task.createdAt}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(task.status)}`}>
                {getStatusText(task.status)}
              </span>
              {task.progress !== undefined && task.status === 'processing' && (
                <span className="text-xs text-blue-600 dark:text-blue-400">
                  {task.progress}%
                </span>
              )}
              <button
                className="text-gray-400 hover:text-red-500 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  clearTaskContext(task.id);
                }}
              >
                <AlertCircle className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

// 上下文污染防护组件
export const ContextPollutionGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentTaskId, getTaskContext } = useTaskIsolation();
  const [maskedStats, setMaskedStats] = useState({ total: 0, masked: 0, savedSize: 0 });

  useEffect(() => {
    if (currentTaskId) {
      const task = getTaskContext(currentTaskId);
      if (task) {
        console.log(`[Context Pollution Guard] Active task: ${task.id}`);
        console.log(`[Context Pollution Guard] Memory layer size:`, {
          conversation: task.memoryLayer.conversationHistory.length,
          results: task.memoryLayer.processingResults.length,
          intermediate: task.memoryLayer.intermediateData.length
        });

        // 计算观察值掩码统计
        const allObservations = [
          ...task.memoryLayer.conversationHistory,
          ...task.memoryLayer.processingResults,
          ...task.memoryLayer.intermediateData
        ];

        const maskedObservations = allObservations
          .filter((obs: any) => obs.isMasked)
          .map((obs: any) => observationMask.mask(obs.content || obs));

        const stats = observationMask.getStats(maskedObservations);
        setMaskedStats(stats);
      }
    }
  }, [currentTaskId]);

  return (
    <div className="relative">
      {/* 防护指示器 */}
      <div className="absolute top-0 right-0 z-10">
        <div className="flex items-center gap-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs px-2 py-1 rounded-bl-lg">
          <Activity className="w-3 h-3" />
          <span>上下文隔离中</span>
        </div>
      </div>
      
      {/* 观察值掩码统计 */}
      {maskedStats.masked > 0 && (
        <div className="absolute bottom-0 right-0 z-10 mb-2">
          <div className="flex items-center gap-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs px-2 py-1 rounded-lg">
            <EyeOff className="w-3 h-3" />
            <span>已掩码 {maskedStats.masked} 个观察值，节省 {formatSize(maskedStats.savedSize)}</span>
          </div>
        </div>
      )}
      
      {children}
    </div>
  );
};

// 辅助函数：格式化大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};