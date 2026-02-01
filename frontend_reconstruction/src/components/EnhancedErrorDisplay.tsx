import React, { useState } from 'react';
import { AlertCircle, X, RefreshCw, HelpCircle, ExternalLink } from 'lucide-react';

interface ErrorInfo {
  code: string;
  message: string;
  details?: string;
  timestamp: string;
  suggestion?: string;
  documentation?: string;
}

interface EnhancedErrorDisplayProps {
  error: ErrorInfo | null;
  onDismiss: () => void;
  onRetry?: () => void;
}

export const EnhancedErrorDisplay: React.FC<EnhancedErrorDisplayProps> = ({
  error,
  onDismiss,
  onRetry,
}) => {
  const [showDetails, setShowDetails] = useState(false);

  if (!error) return null;

  const getErrorSeverity = (code: string) => {
    if (code.startsWith('5')) return 'critical';
    if (code.startsWith('4')) return 'error';
    if (code.startsWith('3')) return 'warning';
    return 'info';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-900/90 border-red-500';
      case 'error':
        return 'bg-orange-900/90 border-orange-500';
      case 'warning':
        return 'bg-yellow-900/90 border-yellow-500';
      default:
        return 'bg-blue-900/90 border-blue-500';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-orange-400" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-blue-400" />;
    }
  };

  const getSeverityText = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '严重错误';
      case 'error':
        return '错误';
      case 'warning':
        return '警告';
      default:
        return '提示';
    }
  };

  const severity = getErrorSeverity(error.code);

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      <div className={`p-4 rounded-lg border-l-4 shadow-lg ${getSeverityColor(severity)}`}>
        {/* 标题栏 */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-start space-x-3">
            {getSeverityIcon(severity)}
            <div>
              <div className="text-sm font-bold text-white">
                {getSeverityText(severity)} [{error.code}]
              </div>
              <div className="text-xs text-gray-300 mt-1">
                {error.message}
              </div>
            </div>
          </div>
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* 详细信息 */}
        {showDetails && (
          <div className="mt-3 pt-3 border-t border-gray-600 space-y-2">
            {error.details && (
              <div className="text-xs text-gray-300">
                <div className="font-medium text-gray-400 mb-1">详细信息:</div>
                <div className="bg-gray-800/50 p-2 rounded">{error.details}</div>
              </div>
            )}
            <div className="text-xs text-gray-400">
              时间: {new Date(error.timestamp).toLocaleString('zh-CN')}
            </div>
          </div>
        )}

        {/* 建议和解决方案 */}
        {error.suggestion && (
          <div className="mt-2 p-2 bg-gray-800/50 rounded">
            <div className="flex items-start space-x-2">
              <HelpCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
              <div className="text-xs text-gray-300">
                <div className="font-medium text-blue-300 mb-1">建议解决方案:</div>
                {error.suggestion}
              </div>
            </div>
          </div>
        )}

        {/* 文档链接 */}
        {error.documentation && (
          <a
            href={error.documentation}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 flex items-center space-x-1 text-xs text-blue-400 hover:text-blue-300 transition-colors"
          >
            <ExternalLink className="w-3 h-3" />
            <span>查看文档</span>
          </a>
        )}

        {/* 操作按钮 */}
        <div className="flex space-x-2 mt-3">
          {onRetry && (
            <button
              onClick={onRetry}
              className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>重试</span>
            </button>
          )}
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded transition-colors"
          >
            {showDetails ? '隐藏详情' : '查看详情'}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * 错误历史组件
 */
export const ErrorHistory: React.FC = () => {
  const [errors, setErrors] = useState<ErrorInfo[]>([]);

  const clearErrors = () => {
    setErrors([]);
  };

  const dismissError = (index: number) => {
    setErrors(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-white">错误历史</h3>
        <button
          onClick={clearErrors}
          className="text-xs text-gray-400 hover:text-white"
        >
          清除全部
        </button>
      </div>
      
      {errors.length === 0 ? (
        <div className="text-xs text-gray-500 text-center py-4">
          暂无错误记录
        </div>
      ) : (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {errors.map((error, index) => (
            <div
              key={index}
              className="p-2 bg-gray-700 rounded border-l-2 border-red-500"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="text-xs font-medium text-white">
                    [{error.code}] {error.message}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(error.timestamp).toLocaleTimeString('zh-CN')}
                  </div>
                </div>
                <button
                  onClick={() => dismissError(index)}
                  className="text-gray-400 hover:text-white ml-2"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * 错误处理钩子
 */
export const useErrorHandler = () => {
  const [currentError, setCurrentError] = useState<ErrorInfo | null>(null);
  const [errorHistory, setErrorHistory] = useState<ErrorInfo[]>([]);

  const handleError = (error: Omit<ErrorInfo, 'timestamp'>) => {
    const errorWithTimestamp: ErrorInfo = {
      ...error,
      timestamp: new Date().toISOString(),
    };
    
    setCurrentError(errorWithTimestamp);
    setErrorHistory(prev => [errorWithTimestamp, ...prev].slice(0, 20));
    
    console.error(`[Error] ${error.code}: ${error.message}`, error.details);
  };

  const dismissError = () => {
    setCurrentError(null);
  };

  const clearHistory = () => {
    setErrorHistory([]);
  };

  return {
    currentError,
    errorHistory,
    handleError,
    dismissError,
    clearHistory,
  };
};