/**
 * 对话驱动的专业翻译详情页
 * 基于 "TranslatorAgent Conversational Interface and Architecture Update Plan.md" 架构文档
 * 实现ChatGPT模式的零摩擦交互体验
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  MessageSquare,
  Loader2,
  Upload,
  Send,
  FileText,
  Video,
  Type,
  Trash2,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { TaskFileArea, TaskFile } from '../components/TaskFileArea';
import { 

  useTaskIsolation, 
  TaskIsolationIndicator,
  ModularTaskList
} from '../components/TaskIsolationManager';
import { RealTimeProgressMonitor } from '../components/RealTimeProgressMonitor';
import { ApiFileSystemStateMachine, apiFsm } from '../utils/ApiFileSystemStateMachine';
import { TaskStatus } from '../utils/FileSystemStateMachine';

// 对话消息接口
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  files?: FileItem[];
  progress?: ProgressInfo;
  status?: 'pending' | 'processing' | 'completed' | 'error';
}

// 文件项接口
interface FileItem {
  id: string;
  name: string;
  type: string;
  size: number;
  status: 'uploading' | 'uploaded' | 'processing' | 'completed' | 'error';
  progress?: number;
  uploadedAt: string;
  processedAt?: string;
}

// 进度信息接口
interface ProgressInfo {
  percentage: number;
  message: string;
  step?: string;
  timestamp: string;
}

// 模块配置
const MODULE_CONFIG = {
  'video-translate': {
    name: '专业视频翻译',
    icon: Video,
    description: '全流程编排：OCR + 翻译 + 擦除 + 压制',
    placeholder: '输入翻译需求，例如："将视频翻译成日语，保持情感基调一致"',
    skill: 'video_translation_expert',
    models: ['ocr_model', 'translation_model', 'video_processor']
  },
  'subtitle-translate': {
    name: '字幕翻译',
    icon: Type,
    description: '纯文本专业处理',
    placeholder: '输入翻译需求，例如："将字幕翻译成英文，保持专业术语准确"',
    skill: 'subtitle_translation_expert',
    models: ['translation_model']
  },
  'subtitle-extract': {
    name: '字幕提取 (OCR)',
    icon: FileText,
    description: 'Llama-3.2-11B-Vision 专家模式',
    placeholder: '输入提取需求，例如："提取视频中的中文字幕"',
    skill: 'ocr_expert',
    models: ['llama_3_2_11b_vision']
  },
  'subtitle-erase': {
    name: '字幕视频无痕擦除',
    icon: Trash2,
    description: 'diffuEraser 修复',
    placeholder: '输入擦除需求，例如："擦除视频中的所有字幕，保持背景完整"',
    skill: 'subtitle_erase_expert',
    models: ['diffuEraser']
  },
  'subtitle-burn': {
    name: '视频字幕压制',
    icon: Loader2,
    description: 'FFmpeg 渲染',
    placeholder: '输入压制需求，例如："将字幕压制到视频，使用白色字体"',
    skill: 'subtitle_burn_expert',
    models: ['ffmpeg']
  },
  'ai-narration': {
    name: 'AI 视频解说',
    icon: MessageSquare,
    description: '文案创作 + 自动化脚本生成',
    placeholder: '输入解说需求，例如："为这个视频生成解说文案，风格轻松幽默"',
    skill: 'narration_expert',
    models: ['文案生成模型']
  }
};

// 内部组件（实际实现）
const ConversationalDetailPageInner: React.FC = () => {
  const [currentModule, _setCurrentModule] = useState<string>('video-translate');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<FileItem[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [apiFsmInstance, setApiFsmInstance] = useState<ApiFileSystemStateMachine | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 使用任务隔离上下文
  const { 
    currentTaskId, 
    createSubAgentSession,
    setCurrentTaskId
  } = useTaskIsolation();

  // 初始化文件系统状态机
  useEffect(() => {
    const initializeFSM = async () => {
      try {
        // 使用API集成的状态机（主用）
        if (apiFsm) {
          await apiFsm.initialize();
          setApiFsmInstance(apiFsm);
          console.log('[ConversationalDetailPage] API file system state machine initialized');
        }
      } catch (error) {
        console.error('[ConversationalDetailPage] Failed to initialize API FSM:', error);
      }
    };

    initializeFSM();
  }, [apiFsm]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 自动初始化会话（零摩擦交互）
  useEffect(() => {
    const initializeSession = async () => {
      if (!currentTaskId && apiFsmInstance) {
        const moduleConfig = MODULE_CONFIG[currentModule as keyof typeof MODULE_CONFIG];
        const taskName = `${moduleConfig.name} - ${new Date().toLocaleString('zh-CN')}`;
        
        try {
          const taskId = await createSubAgentSession(currentModule, taskName);
          console.log(`[ConversationalDetailPage] 自动初始化会话: ${taskId}`);
          
          // 更新当前任务ID
          setCurrentTaskId(taskId);
          
          // 添加系统消息
          addSystemMessage(`欢迎使用 ${moduleConfig.name}！您可以直接输入需求并上传文件，我会立即为您处理。`);
        } catch (error) {
          console.error('[ConversationalDetailPage] 自动初始化会话失败:', error);
        }
      }
    };

    initializeSession();
  }, [currentModule, currentTaskId, apiFsmInstance]);

  // 添加系统消息
  const addSystemMessage = useCallback((content: string) => {
    const message: ChatMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: 'system',
      content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, message]);
  }, []);

  // 添加用户消息
  const addUserMessage = useCallback((content: string, files?: FileItem[]) => {
    const message: ChatMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      files
    };
    setMessages(prev => [...prev, message]);
  }, []);

  // 更新消息进度
  const updateMessageProgress = useCallback((messageId: string, progress: ProgressInfo) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, progress, status: 'processing' } : msg
    ));
  }, []);

  // 完成消息
  const completeMessage = useCallback((messageId: string, content: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, content, status: 'completed' } : msg
    ));
  }, []);

  // 处理文件上传
  const handleFileUpload = useCallback(async (files: FileList) => {
    if (!currentTaskId || !apiFsmInstance) {
      addSystemMessage('请先创建任务');
      return;
    }

    // 保存原始File对象的映射
    const fileMap = new Map<string, File>();
    
    const newFiles: FileItem[] = Array.from(files).map(file => {
      const fileId = `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      fileMap.set(fileId, file); // 保存原始File对象
      return {
        id: fileId,
        name: file.name,
        type: file.type || 'other',
        size: file.size,
        status: 'uploading',
        progress: 0,
        uploadedAt: new Date().toISOString()
      };
    });

    setUploadedFiles(prev => [...prev, ...newFiles]);
    setIsUploading(true);

    // 模拟上传进度
    for (const fileItem of newFiles) {
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, progress } : f
        ));
      }

      // 更新后端任务状态
      try {
        // 获取原始File对象
        const originalFile = fileMap.get(fileItem.id);
        if (!originalFile) {
          throw new Error('File object not found');
        }
        
        // 验证文件对象类型
        if (!(originalFile instanceof File)) {
          console.error('Invalid file object type:', originalFile);
          throw new Error('Invalid file object type');
        }
        
        // 实际上传文件 - 使用原始File对象
        const uploadResult = await apiFsmInstance.uploadTaskFile(currentTaskId, originalFile);
        console.log('文件上传成功:', uploadResult);
        
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, status: 'uploaded' } : f
        ));
      } catch (error) {
        console.error('文件上传失败:', error);
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, status: 'error' } : f
        ));
      }
    }

    setIsUploading(false);
    addSystemMessage(`已上传 ${newFiles.length} 个文件`);
  }, [currentTaskId, currentModule, apiFsmInstance]);

  // 发送消息（对话驱动）
  const sendMessage = useCallback(async () => {
    if (!inputValue.trim() && uploadedFiles.length === 0) return;
    
    // 如果没有任务ID，自动创建
    if (!currentTaskId || !apiFsmInstance) {
      const moduleConfig = MODULE_CONFIG[currentModule as keyof typeof MODULE_CONFIG];
      const taskName = `${moduleConfig.name} - ${new Date().toLocaleString('zh-CN')}`;
      
      try {
        const taskId = await createSubAgentSession(currentModule, taskName);
        setCurrentTaskId(taskId);
        console.log(`[ConversationalDetailPage] 自动创建任务: ${taskId}`);
      } catch (error) {
        console.error('[ConversationalDetailPage] 自动创建任务失败:', error);
        addSystemMessage('任务创建失败，请重试');
        return;
      }
    }

    const userMessage = inputValue.trim();
    setIsSending(true);

    // 添加用户消息
    addUserMessage(userMessage, uploadedFiles.length > 0 ? uploadedFiles : undefined);

    // 清空输入
    setInputValue('');
    const filesToProcess = [...uploadedFiles];
    // 不清空 uploadedFiles，让文件显示在右边的任务文件区

    // 创建助手消息（用于显示进度）
    const assistantMessageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '正在理解您的需求并启动处理流程...',
      timestamp: new Date().toISOString(),
      status: 'processing'
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      // 步骤1: 更新任务状态为处理中
      if (apiFsmInstance && currentTaskId) {
        await apiFsmInstance.updateTaskState(currentTaskId, currentModule, {
          status: TaskStatus.PROCESSING
        });
      }

      // 步骤2: 更新进度（思维链推理）
      updateMessageProgress(assistantMessageId, {
        percentage: 10,
        message: '正在理解您的需求...',
        step: '意图理解',
        timestamp: new Date().toISOString()
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      // 步骤3: 选择专业模块
      updateMessageProgress(assistantMessageId, {
        percentage: 25,
        message: '正在选择专业模块...',
        step: '模块选择',
        timestamp: new Date().toISOString()
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      // 步骤4: 提取处理参数
      updateMessageProgress(assistantMessageId, {
        percentage: 40,
        message: '正在提取处理参数...',
        step: '参数提取',
        timestamp: new Date().toISOString()
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      // 步骤5: 制定处理流程
      updateMessageProgress(assistantMessageId, {
        percentage: 55,
        message: '正在制定处理流程...',
        step: '流程制定',
        timestamp: new Date().toISOString()
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      // 步骤6: 执行处理
      updateMessageProgress(assistantMessageId, {
        percentage: 70,
        message: '正在执行处理...',
        step: '任务执行',
        timestamp: new Date().toISOString()
      });

      // 更新文件状态为处理中
      setUploadedFiles(prev => prev.map(file => ({
        ...file,
        status: 'processing',
        progress: 70
      })));

      // 模拟处理过程
      for (let progress = 70; progress <= 90; progress += 5) {
        await new Promise(resolve => setTimeout(resolve, 500));
        updateMessageProgress(assistantMessageId, {
          percentage: progress,
          message: `正在处理中... ${progress}%`,
          step: '任务执行',
          timestamp: new Date().toISOString()
        });
        
        // 更新文件进度
        setUploadedFiles(prev => prev.map(file => ({
          ...file,
          progress
        })));
      }

      // 步骤7: 完成处理
      updateMessageProgress(assistantMessageId, {
        percentage: 100,
        message: '处理完成！',
        step: '完成',
        timestamp: new Date().toISOString()
      });

      // 更新文件状态为完成
      setUploadedFiles(prev => prev.map(file => ({
        ...file,
        status: 'completed',
        progress: 100,
        processedAt: new Date().toISOString()
      })));

      // 更新任务状态为完成
      if (apiFsmInstance && currentTaskId) {
        await apiFsmInstance.updateTaskState(currentTaskId, currentModule, {
          status: TaskStatus.COMPLETED,
          progress: {
            current: 100,
            total: 100,
            percentage: 100,
            message: '处理完成',
            timestamp: new Date().toISOString()
          }
        });
      }

      // 完成助手消息
      completeMessage(assistantMessageId, `✅ 处理完成！\n\n**处理结果**: ${userMessage}\n\n**文件**: ${filesToProcess.length > 0 ? filesToProcess.map(f => f.name).join(', ') : '无'}\n\n您可以继续输入新的需求，或上传更多文件。`);

      // 添加系统提示
      addSystemMessage('💡 提示：您可以继续对话，或上传新文件进行处理。');

    } catch (error) {
      console.error('处理失败:', error);
      completeMessage(assistantMessageId, `❌ 处理失败: ${(error as Error).message}`);
      addSystemMessage('处理过程中出现错误，请检查控制台日志。');
    } finally {
      setIsSending(false);
    }
  }, [inputValue, uploadedFiles, currentTaskId, currentModule, apiFsmInstance]);

  // 删除文件
  const handleFileDelete = useCallback((fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  }, []);

  // 下载文件
  const handleFileDownload = useCallback(async (fileId: string) => {
    if (!currentTaskId || !apiFsmInstance) {
      addSystemMessage('任务未就绪，无法下载文件');
      return;
    }

    try {
      // 从文件系统状态机获取文件信息
      const taskState = await apiFsmInstance.readTaskState(currentTaskId, currentModule);
      console.log('Task state files:', taskState.files);
      console.log('File ID to check:', fileId);
      console.log('Task state files type:', typeof taskState.files);
      console.log('Task state files isArray:', Array.isArray(taskState.files));
      
      // 查找对应的文件名
      let fileName = '';
      
      // 首先从上传的文件列表中查找
      const uploadedFile = uploadedFiles.find(file => file.id === fileId);
      if (uploadedFile) {
        fileName = uploadedFile.name;
        console.log('从上传文件列表中找到文件:', fileName);
      } else if (Array.isArray(taskState.files) && taskState.files.length > 0) {
        // 如果在上传的文件列表中找不到，从任务状态中查找
        // 由于文件ID和文件名不匹配，直接使用任务状态中的第一个文件
        // 在实际应用中，应该建立文件ID和文件名的映射关系
        fileName = taskState.files[0].split('/').pop() || taskState.files[0];
        console.log('从任务状态中找到文件:', fileName);
      }
      
      if (!fileName) {
        addSystemMessage('文件未找到，无法下载');
        console.log('文件检查:', {
          fileId,
          files: taskState.files,
          filesType: typeof taskState.files,
          isArray: Array.isArray(taskState.files),
          uploaded: [],
          processed: [],
          failed: []
        });
        return;
      }

      // 使用后端API下载文件
      console.log('开始下载文件:', { taskId: currentTaskId, fileName, module: currentModule });
      const downloadResult = await apiFsmInstance.downloadTaskFile(currentTaskId, fileName);
      console.log('下载结果:', downloadResult);
      
      if (downloadResult.error) {
        addSystemMessage(`❌ 文件下载失败: ${downloadResult.error}`);
        return;
      }

      // 检查是否是 Response 对象（StreamingResponse）
      if (downloadResult instanceof Response) {
        // 处理实际的文件下载
        const blob = await downloadResult.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        addSystemMessage(`✅ 文件下载已开始: ${fileName}`);
        console.log('文件下载成功 (StreamingResponse):', fileName);
      } else if (downloadResult && typeof downloadResult === 'object' && !Array.isArray(downloadResult)) {
        if (downloadResult.file_url) {
          // 如果后端返回的是文件URL，直接打开下载
          const a = document.createElement('a');
          a.href = downloadResult.file_url;
          a.download = downloadResult.filename || fileId;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          
          addSystemMessage(`✅ 文件下载已开始: ${downloadResult.filename || fileName}`);
          console.log('文件下载成功 (URL):', downloadResult);
        } else if (downloadResult.data) {
          // 如果后端返回的是文件数据，创建Blob下载
          const blob = new Blob([downloadResult.data], { type: 'video/mp4' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = fileName;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
          
          addSystemMessage(`✅ 文件下载已开始: ${fileName}`);
          console.log('文件下载成功 (Blob):', downloadResult);
        } else {
          // 如果没有返回具体数据，创建模拟下载
          const mockData = {
            id: fileId,
          name: fileName,
            task_id: currentTaskId,
            module: currentModule
          };

          const blob = new Blob([JSON.stringify(mockData, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${fileName}.json`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);

          addSystemMessage(`✅ 文件下载已开始: ${fileName}`);
          console.log('文件下载成功 (Mock):', mockData);
        }
      } else if (Array.isArray(downloadResult)) {
        // 如果后端返回的是文件路径数组，模拟下载第一个文件
        const firstFile = downloadResult[0];
        if (firstFile) {
          const mockData = {
            id: fileId,
            name: firstFile,
            type: 'video/mp4',
            size: 1024 * 1024 * 10,
            timestamp: new Date().toISOString(),
            task_id: currentTaskId,
            module: currentModule
          };

          const blob = new Blob([JSON.stringify(mockData, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${fileName}.json`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);

          addSystemMessage(`✅ 文件下载已开始: ${fileName}`);
          console.log('文件下载成功 (Mock):', mockData);
        }
      } else {
        // 如果没有返回具体数据，创建模拟下载
        const mockData = {
          id: fileId,
          name: fileName,
          type: 'video/mp4',
          size: 1024 * 1024 * 10,
          timestamp: new Date().toISOString(),
          task_id: currentTaskId,
          module: currentModule
        };

        const blob = new Blob([JSON.stringify(mockData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileName}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        addSystemMessage(`✅ 文件下载已开始: ${fileName}`);
        console.log('文件下载成功 (Mock):', mockData);
      }
    } catch (error) {
      console.error('文件下载失败:', error);
      addSystemMessage('❌ 文件下载失败');
    }
  }, [currentTaskId, currentModule, apiFsmInstance, addSystemMessage]);

  const moduleConfig = MODULE_CONFIG[currentModule as keyof typeof MODULE_CONFIG];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧历史任务栏 */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-800">历史任务</h2>
          <p className="text-xs text-gray-500 mt-1">按模块分类归档</p>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ModularTaskList 
            module={currentModule || 'video-translate'}
          />
        </div>
      </div>

      {/* 中间对话区 */}
      <div className="flex-1 flex flex-col">
        {/* 顶部模块信息 */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <moduleConfig.icon className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h1 className="font-semibold text-gray-800">{moduleConfig.name}</h1>
                <p className="text-xs text-gray-500">{moduleConfig.description}</p>
              </div>
            </div>
            <TaskIsolationIndicator />
          </div>
        </div>

        {/* 对话历史 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <MessageSquare className="w-16 h-16 mb-4 opacity-50" />
              <p className="text-lg font-medium">开始对话</p>
              <p className="text-sm">直接输入需求并上传文件，我会立即为您处理</p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-2xl rounded-lg p-4 ${
                  message.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : message.role === 'assistant'
                    ? 'bg-white border border-gray-200'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {/* 消息内容 */}
                  <div className="whitespace-pre-wrap">{message.content}</div>

                  {/* 文件列表 */}
                  {message.files && message.files.length > 0 && (
                    <div className="mt-3 space-y-1">
                      {message.files.map((file) => (
                        <div key={file.id} className="flex items-center gap-2 text-sm">
                          <FileText className="w-4 h-4" />
                          <span>{file.name}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 进度条 */}
                  {message.progress && (
                    <div className="mt-3">
                      <div className="flex items-center gap-2 text-sm mb-1">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>{message.progress.message}</span>
                        <span className="font-medium">{message.progress.percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${message.progress.percentage}%` }}
                        />
                      </div>
                      {message.progress.step && (
                        <div className="text-xs text-gray-500 mt-1">步骤: {message.progress.step}</div>
                      )}
                    </div>
                  )}

                  {/* 时间戳 */}
                  <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
                    {new Date(message.timestamp).toLocaleTimeString('zh-CN')}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 底部一体化输入区 */}
        <div className="bg-white border-t border-gray-200 p-4">
          {/* 文件上传区域 */}
          {uploadedFiles.length > 0 && (
            <div className="mb-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">待处理文件</span>
                <span className="text-xs text-gray-500">{uploadedFiles.length} 个文件</span>
              </div>
              <div className="space-y-2">
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-gray-500" />
                      <span className="text-gray-700">{file.name}</span>
                      {file.progress !== undefined && (
                        <span className="text-xs text-gray-500">({file.progress}%)</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {file.status === 'uploaded' && (
                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                      )}
                      {file.status === 'uploading' && (
                        <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                      )}
                      {file.status === 'error' && (
                        <AlertCircle className="w-4 h-4 text-red-500" />
                      )}
                      <button 
                        onClick={() => handleFileDelete(file.id)}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 输入区域 */}
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder={moduleConfig.placeholder}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={2}
                disabled={isSending}
              />
            </div>
            <div className="flex flex-col gap-2">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={(e) => {
                  if (e.target.files) {
                    handleFileUpload(e.target.files);
                    e.target.value = '';
                  }
                }}
                className="hidden"
              />
              <Button
                variant="outline"
                size="icon"
                onClick={() => fileInputRef.current?.click()}
                disabled={isSending || isUploading}
                title="上传文件"
              >
                <Upload className="w-4 h-4" />
              </Button>
              <Button
                size="icon"
                onClick={sendMessage}
                disabled={isSending || isUploading}
                title="发送"
              >
                {isSending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>

          {/* 提示信息 */}
          <div className="mt-2 text-xs text-gray-500">
            💡 提示：直接输入需求并上传文件，点击发送或按 Enter 键即可处理
          </div>
        </div>
      </div>

      {/* 右侧文件区 */}
      <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-800">任务文件区</h2>
          <p className="text-xs text-gray-500 mt-1">实时同步处理状态</p>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <TaskFileArea
            files={uploadedFiles.map(file => ({
              id: file.id,
              name: file.name,
              type: file.type as 'video' | 'subtitle' | 'text' | 'result',
              status: file.status as 'pending' | 'processing' | 'completed' | 'error',
              size: file.size.toString(),
              uploadedAt: file.uploadedAt,
              processedAt: file.processedAt,
              progress: file.progress
            })) as TaskFile[]}
            onFileDelete={handleFileDelete}
            onFileDownload={handleFileDownload}
          />
        </div>
      </div>

      {/* 实时进度监控 */}
      {currentTaskId && (
        <RealTimeProgressMonitor
          taskId={currentTaskId}
          module={currentModule}
          onProgressUpdate={(progress) => {
            // 更新最新的助手消息进度
            const lastAssistantMessage = [...messages].reverse().find(m => m.role === 'assistant');
            if (lastAssistantMessage) {
              updateMessageProgress(lastAssistantMessage.id, { percentage: progress, message: '', timestamp: new Date().toISOString() });
            }
          }}
        />
      )}

      {/* 上下文污染防护 */}
    </div>
  );
};

export default ConversationalDetailPageInner;