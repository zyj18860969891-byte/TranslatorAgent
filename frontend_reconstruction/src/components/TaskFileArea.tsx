import React, { useState } from 'react';
import { 
  FileText, 
  Video, 
  FolderOpen, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  RefreshCw,
  Download,
  Trash2
} from 'lucide-react';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';

export interface TaskFile {
  id: string;
  name: string;
  type: 'video' | 'subtitle' | 'text' | 'result';
  status: 'pending' | 'processing' | 'completed' | 'error';
  size: string;
  uploadedAt: string;
  processedAt?: string;
  path?: string;
  progress?: number;
}

// EnhancedFile 类型兼容
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

interface TaskFileAreaProps {
  files: TaskFile[];
  onFileSelect?: (file: TaskFile) => void;
  onFileDelete?: (fileId: string) => void;
  onFileDownload?: (fileId: string) => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const TaskFileArea: React.FC<TaskFileAreaProps> = ({
  files,
  onFileSelect,
  onFileDelete,
  onFileDownload,
  onRefresh,
  isRefreshing = false
}) => {
  const [filterType, setFilterType] = useState<'all' | 'video' | 'subtitle' | 'text' | 'result'>('all');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
      case 'processing':
      case 'uploading':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300';
      case 'error':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'pending':
      case 'uploaded':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="w-4 h-4" />;
      case 'subtitle':
        return <FileText className="w-4 h-4" />;
      case 'text':
        return <FileText className="w-4 h-4" />;
      case 'result':
        return <CheckCircle2 className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'video':
        return '视频';
      case 'subtitle':
        return '字幕';
      case 'text':
        return '文本';
      case 'result':
        return '结果';
      default:
        return '文件';
    }
  };

  const filteredFiles = filterType === 'all' 
    ? files 
    : files.filter(file => file.type === filterType);

  const stats = {
    total: files.length,
    completed: files.filter(f => f.status === 'completed').length,
    processing: files.filter(f => f.status === 'processing').length,
    pending: files.filter(f => f.status === 'pending').length
  };

  return (
    <div className="w-80 bg-white dark:bg-gray-950 border-l border-gray-200 dark:border-gray-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <FolderOpen className="w-4 h-4" />
            任务文件区
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={onRefresh}
            disabled={isRefreshing}
            className="h-7 w-7 p-0"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        
        {/* Stats */}
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div className="text-center p-2 bg-gray-50 dark:bg-gray-900 rounded">
            <div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total}</div>
            <div className="text-gray-500 dark:text-gray-400">总数</div>
          </div>
          <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded">
            <div className="font-semibold text-green-700 dark:text-green-300">{stats.completed}</div>
            <div className="text-green-600 dark:text-green-400">完成</div>
          </div>
          <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
            <div className="font-semibold text-blue-700 dark:text-blue-300">{stats.processing}</div>
            <div className="text-blue-600 dark:text-blue-400">处理</div>
          </div>
          <div className="text-center p-2 bg-gray-50 dark:bg-gray-900 rounded">
            <div className="font-semibold text-gray-700 dark:text-gray-300">{stats.pending}</div>
            <div className="text-gray-600 dark:text-gray-400">待处理</div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-800">
        <div className="flex gap-1">
          {(['all', 'video', 'subtitle', 'text', 'result'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                filterType === type
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              {type === 'all' ? '全部' : getTypeLabel(type)}
            </button>
          ))}
        </div>
      </div>

      {/* File List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredFiles.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <FolderOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">暂无文件</p>
            <p className="text-xs mt-1">上传文件后将显示在此处</p>
          </div>
        ) : (
          filteredFiles.map((file) => (
            <div
              key={file.id}
              className="group border border-gray-200 dark:border-gray-800 rounded-lg p-3 hover:border-primary-600 dark:hover:border-primary-600 transition-colors cursor-pointer"
              onClick={() => onFileSelect?.(file)}
            >
              <div className="flex items-start gap-2 mb-2">
                <div className="p-1.5 bg-gray-100 dark:bg-gray-800 rounded">
                  {getTypeIcon(file.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {file.name}
                    </span>
                    <Badge 
                      className={`${getStatusColor(file.status)} text-xs px-1.5 py-0.5`}
                    >
                      {file.status === 'completed' ? '完成' : 
                       file.status === 'processing' ? '处理中' : 
                       file.status === 'error' ? '错误' : '待处理'}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
                    <span>{getTypeLabel(file.type)}</span>
                    <span>•</span>
                    <span>{file.size}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{file.uploadedAt}</span>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {file.status === 'completed' && onFileDownload && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        onFileDownload(file.id);
                      }}
                    >
                      <Download className="w-3 h-3" />
                    </Button>
                  )}
                  {onFileDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 text-red-500 hover:text-red-600"
                      onClick={(e) => {
                        e.stopPropagation();
                        onFileDelete(file.id);
                      }}
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              </div>

              {file.status === 'error' && (
                <div className="mt-2 flex items-center gap-1 text-xs text-red-600 dark:text-red-400">
                  <AlertCircle className="w-3 h-3" />
                  <span>处理失败，请重试</span>
                </div>
              )}

              {file.status === 'processing' && (
                <div className="mt-2">
                  <div className="h-1 bg-gray-200 dark:bg-gray-800 rounded overflow-hidden">
                    <div className="h-full bg-blue-500 animate-pulse" style={{ width: '60%' }} />
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Empty State Actions */}
      {files.length === 0 && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-800">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => {
              // 模拟上传文件
              const mockFile: TaskFile = {
                id: `file-${Date.now()}`,
                name: '示例视频.mp4',
                type: 'video',
                status: 'pending',
                size: '15.2 MB',
                uploadedAt: new Date().toLocaleString('zh-CN')
              };
              // 这里应该调用实际的上传函数
              console.log('Upload file:', mockFile);
            }}
          >
            <FolderOpen className="w-4 h-4 mr-2" />
            上传文件
          </Button>
        </div>
      )}
    </div>
  );
};