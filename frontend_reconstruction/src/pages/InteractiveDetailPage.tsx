import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  MessageSquare,
  History,
  Shield,
  Loader2
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { TaskFileArea } from '../components/TaskFileArea';
import { 
  TaskIsolationManager, 
  useTaskIsolation, 
  TaskIsolationIndicator,
  ModularTaskList,
  ContextPollutionGuard
} from '../components/TaskIsolationManager';
import { RealTimeProgressMonitor } from '../components/RealTimeProgressMonitor';
import { EnhancedUploadArea, EnhancedFile } from '../components/EnhancedUploadArea';
import { TaskStatus } from '../utils/FileSystemStateMachine';
import { ApiFileSystemStateMachine, apiFsm } from '../utils/ApiFileSystemStateMachine';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
}

interface InteractiveDetailPageProps {
  featureType: 'video-translate' | 'subtitle-extract' | 'text-translate';
  onBack: () => void;
}

const InteractiveDetailPageContent: React.FC<InteractiveDetailPageProps> = ({
  featureType,
  onBack
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<EnhancedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [apiFsm, setApiFsm] = useState<ApiFileSystemStateMachine | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 使用任务隔离上下文
  const { 
    currentTaskId, 
    createSubAgentSession
  } = useTaskIsolation();

  // 初始化文件系统状态机
  useEffect(() => {
    const initializeFSM = async () => {
      try {
        // 使用API集成的状态机（主用）
        if (apiFsm) {
          await apiFsm.initialize();
          console.log('[InteractiveDetailPage] API file system state machine initialized');
        }
      } catch (error) {
        console.error('[InteractiveDetailPage] Failed to initialize API FSM:', error);
      }
    };

    initializeFSM();
  }, [apiFsm]);

  const featureLabels = {
    'video-translate': '专业视频翻译',
    'subtitle-extract': '字幕提取',
    'text-translate': '字幕翻译'
  };

  // 创建子智能体会话
  useEffect(() => {
    const createSession = async () => {
      if (!currentTaskId && apiFsm) {
        const taskName = `${featureLabels[featureType]} - ${new Date().toLocaleString('zh-CN')}`;
        try {
          const taskId = await createSubAgentSession(featureType, taskName);
          console.log(`[InteractiveDetailPage] Created sub-agent session: ${taskId}`);
        } catch (error) {
          console.error('[InteractiveDetailPage] Failed to create sub-agent session:', error);
        }
      }
    };

    createSession();
  }, [featureType, currentTaskId, createSubAgentSession, apiFsm]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startProcessing = useCallback(async () => {
    if (!currentTaskId || !apiFsm) {
      console.error('[InteractiveDetailPage] No task ID or API FSM available');
      return;
    }

    try {
      // 更新任务状态为处理中（使用API FSM）
      await apiFsm.updateTaskState(currentTaskId, featureType, {
        status: TaskStatus.PROCESSING
      });

      // 模拟处理过程，逐步更新进度
      const processSteps = [
        { progress: 20, message: '正在分析文件格式...' },
        { progress: 40, message: '正在提取内容...' },
        { progress: 60, message: '正在处理数据...' },
        { progress: 80, message: '正在生成结果...' },
        { progress: 100, message: '处理完成' }
      ];

      for (const step of processSteps) {
        await new Promise(resolve => setTimeout(resolve, 800));
        
        await apiFsm.updateTaskProgress(currentTaskId, featureType, {
          current: step.progress,
          total: 100,
          percentage: step.progress,
          message: step.message
        });

        // 添加处理结果到记忆层
        if (step.progress === 100) {
          await apiFsm.addToMemoryLayer(currentTaskId, featureType, 'result', {
            timestamp: new Date().toISOString(),
            message: step.message,
            files: uploadedFiles.map(f => f.name)
          });
        }
      }

      // 标记所有文件为已处理
      for (const file of uploadedFiles) {
        await apiFsm.addFileToTask(currentTaskId, featureType, file.name, 'processed');
      }

      // 更新任务状态为成功
      await apiFsm.updateTaskState(currentTaskId, featureType, {
        status: TaskStatus.COMPLETED,
        completedAt: new Date().toISOString()
      });

      // 添加完成消息
      const completeMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `处理完成！所有 ${uploadedFiles.length} 个文件已成功处理。`,
        timestamp: new Date().toLocaleTimeString('zh-CN')
      };
      
      setMessages(prev => [...prev, completeMessage]);

    } catch (error) {
      console.error('[InteractiveDetailPage] Processing failed:', error);
      
      // 更新任务状态为错误
      if (currentTaskId) {
        await apiFsm.updateTaskState(currentTaskId, featureType, {
          status: TaskStatus.FAILED,
          error: '处理过程中发生错误'
        });
      }

      const errorMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: '处理过程中发生错误，请重试。',
        timestamp: new Date().toLocaleTimeString('zh-CN')
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  }, [currentTaskId, apiFsm, featureType, uploadedFiles]);

  const handleSendMessage = useCallback(async (message: string, files: EnhancedFile[]) => {
    if (!message.trim() && files.length === 0) return;
    if (!currentTaskId || !apiFsm) {
      alert('请先创建任务会话');
      return;
    }

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: message || '上传了文件，请处理',
      timestamp: new Date().toLocaleTimeString('zh-CN'),
      status: 'sending'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsSending(true);

    try {
      // 将用户消息添加到API文件系统状态机的记忆层
      await apiFsm.addToMemoryLayer(currentTaskId, featureType, 'conversation', {
        id: userMessage.id,
        role: 'user',
        content: userMessage.content,
        timestamp: userMessage.timestamp
      });

      // 模拟发送延迟
      await new Promise(resolve => setTimeout(resolve, 1000));

      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
      ));

      // 生成AI回复
      const assistantContent = generateAssistantResponse(message, files);
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date().toLocaleTimeString('zh-CN')
      };

      setMessages(prev => [...prev, assistantMessage]);

      // 将AI回复添加到API文件系统状态机的记忆层
      await apiFsm.addToMemoryLayer(currentTaskId, featureType, 'conversation', {
        id: assistantMessage.id,
        role: 'assistant',
        content: assistantMessage.content,
        timestamp: assistantMessage.timestamp
      });

      setIsSending(false);

      // 如果有文件，开始处理
      if (files.length > 0) {
        startProcessing();
      }
    } catch (error) {
      console.error('[InteractiveDetailPage] Failed to send message:', error);
      setIsSending(false);
      
      const errorMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: '发送消息时发生错误，请重试。',
        timestamp: new Date().toLocaleTimeString('zh-CN')
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  }, [currentTaskId, apiFsm, featureType, startProcessing]);

  const generateAssistantResponse = (userInput: string, files: EnhancedFile[]) => {
    if (files.length > 0) {
      const fileNames = files.map(f => f.name).join('、');
      return `收到您的文件：${fileNames}。我将开始处理这些文件。请稍候，我会在右侧文件区更新处理进度。`;
    }
    
    if (userInput.includes('翻译') || userInput.includes('translate')) {
      return `好的，我将为您翻译内容。请上传需要翻译的文件或直接输入文本。我会自动检测语言并提供高质量的翻译结果。`;
    }
    
    if (userInput.includes('字幕') || userInput.includes('subtitle')) {
      return `收到字幕处理请求。请上传视频文件，我将自动提取字幕并进行翻译。处理完成后，您可以在右侧文件区下载结果。`;
    }
    
    return `我理解您的需求。请告诉我更多细节，或者上传相关文件，我会为您提供最佳的处理方案。`;
  };

  const handleFilesUpload = useCallback(async (newFiles: EnhancedFile[]) => {
    if (!currentTaskId || !apiFsm) {
      alert('请先创建任务会话');
      return;
    }

    setIsUploading(true);

    try {
      // 将文件信息添加到API文件系统状态机
      for (const file of newFiles) {
        await apiFsm.addFileToTask(currentTaskId, featureType, file.name, 'uploaded');
      }

      // 更新任务进度
      await apiFsm.updateTaskProgress(currentTaskId, featureType, {
        current: 10,
        total: 100,
        percentage: 10,
        message: `已上传 ${newFiles.length} 个文件`
      });

      setUploadedFiles(prev => [...prev, ...newFiles]);
    } catch (error) {
      console.error('[InteractiveDetailPage] Failed to upload files:', error);
      alert('文件上传失败，请重试');
    } finally {
      setIsUploading(false);
    }
  }, [currentTaskId, apiFsm, featureType]);

  const handleFileRemove = useCallback((fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  }, []);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Left Sidebar - Module-Based History Tasks */}
      <div className="w-64 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <History className="w-4 h-4" />
            模块化历史任务
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            基于文件系统状态机，按模块分类存储
          </p>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          <ModularTaskList module={featureType} />
        </div>
      </div>

      {/* Middle - Chat & Upload Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {featureLabels[featureType]}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                对话交互 + 文件上传详情页 (任务隔离模式)
              </p>
            </div>
            <div className="flex items-center gap-2">
              <TaskIsolationIndicator />
              <Button variant="outline" onClick={onBack}>
                返回主页
              </Button>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <ContextPollutionGuard>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
                <MessageSquare className="w-16 h-16 mb-4 opacity-50" />
                <p className="text-lg font-medium">开始对话</p>
                <p className="text-sm">上传文件或输入消息，与AI助手交互</p>
                <p className="text-xs mt-2 text-blue-600 dark:text-blue-400">
                  <Shield className="w-3 h-3 inline mr-1" />
                  上下文隔离保护已启用
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-2xl rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 text-gray-900 dark:text-gray-100'
                    }`}
                  >
                    <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-primary-100' : 'text-gray-500 dark:text-gray-400'}`}>
                      {message.timestamp}
                      {message.status === 'sending' && (
                        <span className="ml-2 inline-flex items-center gap-1">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          发送中...
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </ContextPollutionGuard>

        {/* Real-Time Progress Monitor */}
        {currentTaskId && (
          <div className="px-4 pb-2">
            <RealTimeProgressMonitor 
              taskId={currentTaskId} 
              module={featureType}
            />
          </div>
        )}

        {/* Enhanced Upload Area */}
        <div className="bg-white dark:bg-gray-950 border-t border-gray-200 dark:border-gray-800 p-4">
          <EnhancedUploadArea
            files={uploadedFiles}
            onFilesUpload={handleFilesUpload}
            onFileRemove={handleFileRemove}
            onSend={handleSendMessage}
            isSending={isSending}
            isUploading={isUploading}
            featureType={featureType}
          />
        </div>
      </div>

      {/* Right - Task File Area */}
      <TaskFileArea
        files={uploadedFiles.map(file => ({
          id: file.id,
          name: file.name,
          type: file.type === 'other' ? 'text' : file.type,
          status: file.status === 'uploading' || file.status === 'uploaded' ? 'pending' : 
                  file.status === 'processing' ? 'processing' : 
                  file.status === 'completed' ? 'completed' : 'error',
          size: file.size,
          uploadedAt: file.uploadedAt,
          processedAt: file.processedAt,
          progress: file.progress
        }))}
        onFileSelect={(file) => console.log('Selected file:', file)}
        onFileDelete={handleFileRemove}
        onFileDownload={(fileId) => {
          const file = uploadedFiles.find(f => f.id === fileId);
          if (file) {
            const blob = new Blob([`模拟文件内容: ${file.name}`], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name;
            a.click();
            URL.revokeObjectURL(url);
          }
        }}
        onRefresh={() => {
          // 模拟刷新
          console.log('Refreshing file list...');
        }}
      />
    </div>
  );
};

// 主组件，包装任务隔离管理器
export const InteractiveDetailPage: React.FC<InteractiveDetailPageProps> = ({
  featureType,
  onBack
}) => {
  return (
    <TaskIsolationManager>
      <InteractiveDetailPageContent featureType={featureType} onBack={onBack} />
    </TaskIsolationManager>
  );
};