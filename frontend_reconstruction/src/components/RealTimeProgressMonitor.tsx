import React, { useState, useEffect, useCallback } from 'react';
import { 
  Loader2, 
  Activity, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  Video,
  Type
} from 'lucide-react';
import { TaskState, TaskStatus } from '../utils/FileSystemStateMachine';
import { ApiFileSystemStateMachine, apiFsm } from '../utils/ApiFileSystemStateMachine';

interface RealTimeProgressMonitorProps {
  taskId: string;
  module: string;
  onProgressUpdate?: (progress: number, message: string) => void;
}

interface ProgressStep {
  id: string;
  name: string;
  icon: React.ReactNode;
  status: 'pending' | 'active' | 'completed' | 'error';
  progress: number;
  message: string;
}

export const RealTimeProgressMonitor: React.FC<RealTimeProgressMonitorProps> = ({
  taskId,
  module,
  onProgressUpdate
}) => {
  const [taskState, setTaskState] = useState<TaskState | null>(null);
  const [fsm, setFsm] = useState<ApiFileSystemStateMachine | null>(null);
  const [loading, setLoading] = useState(true);
  const [steps, setSteps] = useState<ProgressStep[]>([]);

  // 初始化文件系统状态机
  useEffect(() => {
    const initializeFSM = async () => {
      try {
        // 使用API集成的状态机
        await apiFsm.initialize();
        setFsm(apiFsm);
      } catch (error) {
        console.error('[RealTimeProgressMonitor] Failed to initialize API FSM:', error);
      }
    };

    initializeFSM();
  }, []);

  // 加载任务状态
  const loadTaskState = useCallback(async () => {
    if (!fsm) return;

    try {
      const state = await fsm.readTaskState(taskId, module);
      
      // 只有状态发生变化时才更新
      setTaskState(prevState => {
        if (!prevState || prevState.status !== state.status || prevState.progress?.percentage !== state.progress?.percentage) {
          // 更新进度回调
          if (onProgressUpdate && state.progress) {
            onProgressUpdate(state.progress.percentage || 0, state.progress.message || '');
          }
          
          // 更新步骤状态
          const progress = state.progress?.percentage || 0;
          const newSteps: ProgressStep[] = [
            {
              id: 'upload',
              name: '文件上传',
              icon: <FileText className="w-4 h-4" />,
              status: progress >= 10 ? 'completed' : progress > 0 ? 'active' : 'pending',
              progress: Math.min(progress * 10, 100),
              message: progress >= 10 ? '上传完成' : '正在上传文件...'
            },
            {
              id: 'process',
              name: '文件处理',
              icon: <Video className="w-4 h-4" />,
              status: progress >= 50 ? 'completed' : progress > 10 ? 'active' : 'pending',
              progress: progress > 10 ? Math.min((progress - 10) * 2, 100) : 0,
              message: progress >= 50 ? '处理完成' : progress > 10 ? '正在处理文件...' : '等待处理...'
            },
            {
              id: 'translate',
              name: '翻译处理',
              icon: <Type className="w-4 h-4" />,
              status: progress >= 90 ? 'completed' : progress > 50 ? 'active' : 'pending',
              progress: progress > 50 ? Math.min((progress - 50) * 2.5, 100) : 0,
              message: progress >= 90 ? '翻译完成' : progress > 50 ? '正在翻译...' : '等待翻译...'
            },
            {
              id: 'complete',
              name: '完成',
              icon: <CheckCircle2 className="w-4 h-4" />,
              status: progress >= 100 ? 'completed' : progress > 90 ? 'active' : 'pending',
              progress: progress > 90 ? Math.min((progress - 90) * 10, 100) : 0,
              message: progress >= 100 ? '任务完成' : '正在完成...'
            }
          ];
          
          setSteps(newSteps);
          return state;
        }
        return prevState;
      });
    } catch (error) {
      console.error(`[RealTimeProgressMonitor] Failed to load task state:`, error);
    } finally {
      setLoading(false);
    }
  }, [fsm, taskId, module, onProgressUpdate]);

  // 启动轮询
  useEffect(() => {
    if (!fsm || !taskId || !module) return;

    // 立即加载一次
    loadTaskState();

    // 设置轮询间隔（每15秒检查一次，避免API限流）
    const interval = setInterval(() => {
      loadTaskState();
    }, 15000);

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [fsm, taskId, module, loadTaskState]);

  // 获取状态图标
  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case TaskStatus.PROCESSING:
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case TaskStatus.FAILED:
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case TaskStatus.PENDING:
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case TaskStatus.CANCELLED:
        return <Activity className="w-5 h-5 text-gray-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  // 获取状态文本
  const getStatusText = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return '完成';
      case TaskStatus.PROCESSING:
        return '处理中';
      case TaskStatus.FAILED:
        return '错误';
      case TaskStatus.PENDING:
        return '待处理';
      case TaskStatus.CANCELLED:
        return '已取消';
      default:
        return '未知';
    }
  };

  // 获取步骤状态样式
  const getStepStatusStyle = (status: 'pending' | 'active' | 'completed' | 'error') => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
      case 'active':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300';
      case 'error':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'pending':
        return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400';
      default:
        return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">加载中...</span>
      </div>
    );
  }

  if (!taskState) {
    return (
      <div className="flex items-center justify-center p-4 text-gray-500 dark:text-gray-400">
        <AlertCircle className="w-5 h-5 mr-2" />
        无法加载任务状态
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
      {/* 任务状态头部 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {getStatusIcon(taskState.status)}
          <div>
            <div className="font-semibold text-gray-900 dark:text-gray-100">
              {getStatusText(taskState.status)}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              任务ID: {taskState.taskId ? taskState.taskId.substr(0, 12) + '...' : 'N/A'}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {taskState.progress?.percentage || 0}%
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {taskState.progress?.timestamp ? new Date(taskState.progress.timestamp).toLocaleTimeString('zh-CN') : '--:--:--'}
          </div>
        </div>
      </div>

      {/* 主进度条 */}
      <div className="mb-4">
        <div className="h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-600 transition-all duration-500 ease-out"
            style={{ width: `${taskState.progress?.percentage || 0}%` }}
          />
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {taskState.progress?.message || '等待开始...'}
        </div>
      </div>

      {/* 详细步骤进度 */}
      <div className="space-y-3">
        <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
          处理步骤
        </div>
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-3">
            <div className={`p-1.5 rounded ${getStepStatusStyle(step.status)}`}>
              {step.icon}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {step.name}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {step.progress}%
                </span>
              </div>
              {step.status === 'active' && (
                <div className="h-1.5 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden mt-1">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${step.progress}%` }}
                  />
                </div>
              )}
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {step.message}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 文件统计 */}
      {taskState.files && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-2 bg-gray-50 dark:bg-gray-900 rounded">
              <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
                0
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">已上传</div>
            </div>
            <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded">
              <div className="text-lg font-bold text-green-600 dark:text-green-400">
                0
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">已处理</div>
            </div>
            <div className="p-2 bg-red-50 dark:bg-red-900/20 rounded">
              <div className="text-lg font-bold text-red-600 dark:text-red-400">
                0
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">失败</div>
            </div>
          </div>
        </div>
      )}

      {/* 内存层统计 */}
      {taskState.memoryLayer && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            记忆层统计
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
              <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {taskState.memoryLayer.conversationHistory?.length || 0}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">对话</div>
            </div>
            <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
              <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                {taskState.memoryLayer.processingResults?.length || 0}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">结果</div>
            </div>
            <div className="p-2 bg-orange-50 dark:bg-orange-900/20 rounded">
              <div className="text-lg font-bold text-orange-600 dark:text-orange-400">
                {taskState.memoryLayer.intermediateData?.length || 0}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">中间数据</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};