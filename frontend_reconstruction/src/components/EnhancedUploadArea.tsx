import React, { useState, useCallback, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  Video, 
  Type, 
  FolderOpen,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Send
} from 'lucide-react';
import { Button } from './ui/Button';
import { Textarea } from './ui/Textarea';

export interface EnhancedFile {
  id: string;
  name: string;
  type: 'video' | 'subtitle' | 'text' | 'other';
  size: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'processing' | 'completed' | 'error';
  progress?: number;
  uploadedAt: string;
  processedAt?: string;
  error?: string;
}

interface EnhancedUploadAreaProps {
  files: EnhancedFile[];
  onFilesUpload: (files: EnhancedFile[]) => void;
  onFileRemove: (fileId: string) => void;
  onSend: (message: string, files: EnhancedFile[]) => void;
  isSending: boolean;
  isUploading: boolean;
  featureType: string;
}

export const EnhancedUploadArea: React.FC<EnhancedUploadAreaProps> = ({
  files,
  onFilesUpload,
  onFileRemove,
  onSend,
  isSending,
  isUploading,
  featureType
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 处理文件
  const processFiles = useCallback((rawFiles: File[]) => {
    const newFiles: EnhancedFile[] = rawFiles.map((file, index) => ({
      id: `file-${Date.now()}-${index}`,
      name: file.name,
      type: file.type.startsWith('video/') ? 'video' : 
            file.name.endsWith('.srt') ? 'subtitle' : 
            file.name.endsWith('.txt') ? 'text' : 'other',
      size: formatFileSize(file.size),
      status: 'pending',
      uploadedAt: new Date().toLocaleString('zh-CN')
    }));

    onFilesUpload(newFiles);
  }, [onFilesUpload]);

  // 拖拽处理
  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
      processFiles(droppedFiles);
    }
  }, [processFiles]);

  // 文件选择处理
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    if (selectedFiles.length > 0) {
      processFiles(selectedFiles);
    }
  }, [processFiles]);

  // 发送消息
  const handleSendMessage = () => {
    if (!inputMessage.trim() && files.length === 0) return;
    onSend(inputMessage, files);
    setInputMessage('');
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 获取文件图标
  const getFileIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="w-4 h-4 text-purple-500" />;
      case 'subtitle':
        return <FileText className="w-4 h-4 text-blue-500" />;
      case 'text':
        return <Type className="w-4 h-4 text-green-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  // 获取文件状态图标
  const getFileStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'uploading':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return null;
    }
  };

  // 获取文件状态文本
  const getFileStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '待上传';
      case 'uploading':
        return '上传中';
      case 'uploaded':
        return '已上传';
      case 'processing':
        return '处理中';
      case 'completed':
        return '已完成';
      case 'error':
        return '错误';
      default:
        return '未知';
    }
  };

  // 获取文件状态样式
  const getFileStatusStyle = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
      case 'processing':
      case 'uploading':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300';
      case 'error':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'uploaded':
        return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
      default:
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
    }
  };

  // 自然语言指令提示
  const getInstructionPlaceholder = () => {
    switch (featureType) {
      case 'video-translate':
        return '例如：将视频翻译成日语，保持情感基调一致，添加中文字幕...';
      case 'subtitle-extract':
        return '例如：从视频中提取字幕，生成SRT格式文件...';
      case 'text-translate':
        return '例如：将文本翻译成英文，保持专业术语准确...';
      default:
        return '输入您的指令或描述需求...';
    }
  };

  return (
    <div className="space-y-4">
      {/* 文件上传区域 */}
      <div
        className={`border-2 rounded-lg p-6 transition-all duration-200 ${
          isDragging
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="text-center">
          <div className="flex justify-center mb-3">
            <Upload className={`w-10 h-10 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} />
          </div>
          <p className={`text-sm font-medium ${isDragging ? 'text-blue-600' : 'text-gray-700 dark:text-gray-300'}`}>
            拖拽文件到此处或点击上传
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            支持视频、字幕、文本文件
          </p>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            multiple
            onChange={handleFileSelect}
            accept="video/*,.srt,.txt"
          />
          <Button
            variant="outline"
            className="mt-3"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                上传中...
              </>
            ) : (
              <>
                <FolderOpen className="w-4 h-4 mr-2" />
                选择文件
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 已上传文件列表 */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
            已上传文件 ({files.length})
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {getFileIcon(file.type)}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {file.name}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {file.size} • {new Date(file.uploadedAt).toLocaleTimeString('zh-CN')}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {file.progress !== undefined && (
                    <div className="w-16 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 transition-all"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded ${getFileStatusStyle(file.status)}`}>
                    {getFileStatusText(file.status)}
                  </span>
                  {getFileStatusIcon(file.status)}
                  <button
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    onClick={() => onFileRemove(file.id)}
                    title="删除文件"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 自然语言指令输入 */}
      <div className="space-y-2">
        <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
          自然语言指令
        </div>
        <div className="flex gap-2">
          <Textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder={getInstructionPlaceholder()}
            className="resize-none flex-1"
            rows={2}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            disabled={isSending}
          />
          <Button
            onClick={handleSendMessage}
            disabled={isSending || (!inputMessage.trim() && files.length === 0)}
            className="self-end flex items-center gap-2"
          >
            {isSending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            发送
          </Button>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          💡 提示：所有配置（如目标语言、字幕样式等）均可通过自然语言指令完成
        </p>
      </div>
    </div>
  );
};