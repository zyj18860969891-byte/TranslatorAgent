import React, { useState } from 'react';
import { 
  getLogger, 
  LogEntry, 
  LogLevel 
} from '../utils/Logger';
import { 
  logUserAction, 
  logPerformance, 
  logError, 
  logInfo, 
  logWarn,
  withPerformanceLogging,
  ErrorBoundary
} from './LogIntegration';

interface LogDemoProps {}

export const LogDemo: React.FC<LogDemoProps> = () => {
  const [testCount, setTestCount] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const logger = getLogger();

  const handleTestLog = (level: LogLevel) => {
    const message = `测试日志 - ${level.toUpperCase()} - ${Date.now()}`;
    const data = { test: true, count: testCount };
    
    switch (level) {
      case 'debug':
        logger.debug(message, data);
        break;
      case 'info':
        logger.info(message, data);
        break;
      case 'warn':
        logger.warn(message, data);
        break;
      case 'error':
        logger.error(message, data);
        break;
      case 'fatal':
        logger.fatal(message, data);
        break;
    }
    
    setTestCount(prev => prev + 1);
    updateLogs();
  };

  const handleUserAction = () => {
    logUserAction('点击测试按钮', { button: 'test', count: testCount });
    updateLogs();
  };

  const handlePerformanceTest = () => {
    const start = performance.now();
    
    // 模拟一些异步操作
    setTimeout(() => {
      const duration = performance.now() - start;
      logPerformance('模拟操作', duration, { operation: 'timeout' });
      updateLogs();
    }, 100);
  };

  const handleErrorTest = () => {
    try {
      throw new Error('这是一个测试错误');
    } catch (error) {
      logError('捕获到测试错误', error, { context: 'demo' });
      updateLogs();
    }
  };

  const handleInfoTest = () => {
    logInfo('信息日志测试', { type: 'info-test', timestamp: Date.now() });
    updateLogs();
  };

  const handleWarnTest = () => {
    logWarn('警告日志测试', { type: 'warn-test', severity: 'medium' });
    updateLogs();
  };

  const updateLogs = () => {
    const allLogs = logger.getLogs();
    setLogs(allLogs.slice(0, 10)); // 只显示最近10条
  };

  const handleClearLogs = () => {
    logger.clearLogs();
    setLogs([]);
    setTestCount(0);
  };

  const handleExportLogs = () => {
    const data = logger.exportLogs('json');
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-demo-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReport = () => {
    logger.report();
    alert('日志报告已生成并输出到控制台');
  };

  const getStats = () => {
    return logger.getStats();
  };

  const stats = getStats();

  return (
    <ErrorBoundary>
      <div className="p-6 bg-gray-800 rounded-lg">
        <h2 className="text-xl font-bold text-white mb-4">日志收集演示</h2>
        
        {/* 统计信息 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="p-3 bg-gray-700 rounded">
            <div className="text-xs text-gray-400">总日志数</div>
            <div className="text-lg font-bold text-white">{stats.total}</div>
          </div>
          <div className="p-3 bg-gray-700 rounded">
            <div className="text-xs text-gray-400">错误数</div>
            <div className="text-lg font-bold text-red-400">{stats.recentErrors}</div>
          </div>
          <div className="p-3 bg-gray-700 rounded">
            <div className="text-xs text-gray-400">警告数</div>
            <div className="text-lg font-bold text-yellow-400">{stats.recentWarnings}</div>
          </div>
          <div className="p-3 bg-gray-700 rounded">
            <div className="text-xs text-gray-400">测试次数</div>
            <div className="text-lg font-bold text-blue-400">{testCount}</div>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 mb-4">
          <button
            onClick={() => handleTestLog('debug')}
            className="px-3 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded text-sm transition-colors"
          >
            Debug日志
          </button>
          <button
            onClick={() => handleTestLog('info')}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm transition-colors"
          >
            Info日志
          </button>
          <button
            onClick={() => handleTestLog('warn')}
            className="px-3 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded text-sm transition-colors"
          >
            Warn日志
          </button>
          <button
            onClick={() => handleTestLog('error')}
            className="px-3 py-2 bg-red-600 hover:bg-red-500 text-white rounded text-sm transition-colors"
          >
            Error日志
          </button>
          <button
            onClick={() => handleTestLog('fatal')}
            className="px-3 py-2 bg-red-800 hover:bg-red-700 text-white rounded text-sm transition-colors"
          >
            Fatal日志
          </button>
          <button
            onClick={handleUserAction}
            className="px-3 py-2 bg-green-600 hover:bg-green-500 text-white rounded text-sm transition-colors"
          >
            用户操作
          </button>
          <button
            onClick={handlePerformanceTest}
            className="px-3 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded text-sm transition-colors"
          >
            性能测试
          </button>
          <button
            onClick={handleErrorTest}
            className="px-3 py-2 bg-red-600 hover:bg-red-500 text-white rounded text-sm transition-colors"
          >
            错误测试
          </button>
          <button
            onClick={handleInfoTest}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm transition-colors"
          >
            信息测试
          </button>
          <button
            onClick={handleWarnTest}
            className="px-3 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded text-sm transition-colors"
          >
            警告测试
          </button>
        </div>

        {/* 工具按钮 */}
        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={handleClearLogs}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition-colors"
          >
            清空日志
          </button>
          <button
            onClick={handleExportLogs}
            className="px-3 py-2 bg-green-700 hover:bg-green-600 text-white rounded text-sm transition-colors"
          >
            导出日志
          </button>
          <button
            onClick={handleReport}
            className="px-3 py-2 bg-purple-700 hover:bg-purple-600 text-white rounded text-sm transition-colors"
          >
            生成报告
          </button>
          <button
            onClick={updateLogs}
            className="px-3 py-2 bg-blue-700 hover:bg-blue-600 text-white rounded text-sm transition-colors"
          >
            刷新日志
          </button>
        </div>

        {/* 日志列表 */}
        <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">最近日志 ({logs.length}条)</h3>
          {logs.length === 0 ? (
            <div className="text-gray-500 text-sm">暂无日志，点击上方按钮生成日志</div>
          ) : (
            <div className="space-y-2">
              {logs.map(log => (
                <div
                  key={log.id}
                  className="p-2 bg-gray-800 rounded border-l-2"
                  style={{
                    borderLeftColor: 
                      log.level === 'error' || log.level === 'fatal' ? '#ef4444' :
                      log.level === 'warn' ? '#eab308' :
                      log.level === 'info' ? '#3b82f6' :
                      '#6b7280'
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-medium text-white">
                        [{log.level.toUpperCase()}]
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(log.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </span>
                    </div>
                    {log.metadata?.performance && (
                      <span className="text-xs text-blue-400">
                        {log.metadata.duration}ms
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-300 mt-1">{log.message}</div>
                  {log.data && (
                    <div className="text-xs text-gray-500 mt-1 font-mono">
                      {JSON.stringify(log.data)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 性能统计 */}
        <div className="mt-4 p-4 bg-gray-700 rounded-lg">
          <h3 className="text-sm font-semibold text-white mb-2">性能统计</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            <div>
              <span className="text-gray-400">性能日志:</span>
              <span className="text-white ml-1">{stats.performanceCount}</span>
            </div>
            <div>
              <span className="text-gray-400">用户操作:</span>
              <span className="text-white ml-1">{stats.userActionCount}</span>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

// 使用性能监控高阶组件包装的示例组件
export const PerformanceLoggedComponent = withPerformanceLogging(
  function ExampleComponent({ name }: { name: string }) {
    const [count, setCount] = useState(0);
    
    return (
      <div className="p-4 bg-gray-700 rounded-lg">
        <h3 className="text-white font-semibold">{name}</h3>
        <p className="text-gray-400 text-sm mt-2">计数: {count}</p>
        <button
          onClick={() => setCount(prev => prev + 1)}
          className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
        >
          增加
        </button>
      </div>
    );
  },
  'ExampleComponent'
);