import React, { useEffect } from 'react';
import { getLogger } from '../utils/Logger';
import { LogCollector, LogStatsPanel } from './LogCollector';

/**
 * 日志集成组件
 * 自动集成日志收集器到应用中
 */
export const LogIntegration: React.FC = () => {
  useEffect(() => {
    const logger = getLogger();
    
    // 记录应用启动
    logger.info('应用启动', { 
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      language: navigator.language,
    });

    // 监听全局错误
    const handleGlobalError = (event: ErrorEvent) => {
      logger.error('全局错误', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.toString(),
      });
    };

    // 监听未处理的 Promise 拒绝
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      logger.error('未处理的 Promise 拒绝', {
        reason: event.reason?.toString(),
      });
    };

    window.addEventListener('error', handleGlobalError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleGlobalError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      
      // 记录应用关闭
      logger.info('应用关闭', { timestamp: Date.now() });
    };
  }, []);

  return (
    <>
      <LogCollector autoHide={true} showControls={true} />
    </>
  );
};

/**
 * 日志统计集成组件
 */
export const LogStatsIntegration: React.FC = () => {
  return <LogStatsPanel />;
};

/**
 * 日志记录工具函数
 */
export const logUserAction = (action: string, data?: any) => {
  const logger = getLogger();
  logger.userAction(action, data);
};

export const logPerformance = (operation: string, duration: number, data?: any) => {
  const logger = getLogger();
  logger.performance(operation, duration, data);
};

export const logError = (message: string, error?: any, data?: any) => {
  const logger = getLogger();
  logger.error(message, { error: error?.toString(), ...data });
};

export const logInfo = (message: string, data?: any) => {
  const logger = getLogger();
  logger.info(message, data);
};

export const logWarn = (message: string, data?: any) => {
  const logger = getLogger();
  logger.warn(message, data);
};

/**
 * React 组件性能监控高阶组件
 */
export function withPerformanceLogging<P extends object>(
  Component: React.ComponentType<P>,
  componentName: string
) {
  return function WithPerformanceLogging(props: P) {
    const startTime = performance.now();

    useEffect(() => {
      const duration = performance.now() - startTime;
      logPerformance(`render_${componentName}`, duration);
    });

    return <Component {...props} />;
  };
}

/**
 * 错误边界组件
 */
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logError('组件渲染错误', error, {
      componentStack: errorInfo.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <h2 className="font-bold">出错了</h2>
          <p className="text-sm mt-1">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
          >
            重试
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}