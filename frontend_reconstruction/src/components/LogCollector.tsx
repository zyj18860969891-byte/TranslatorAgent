import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  AlertCircle, 
  Info, 
  Trash2, 
  Download, 
  Filter,
  Search,
  User,
  Activity
} from 'lucide-react';
import { getLogger, LogEntry, LogLevel } from '../utils/Logger';

interface LogCollectorProps {
  autoHide?: boolean;
  showControls?: boolean;
}

export const LogCollector: React.FC<LogCollectorProps> = ({
  autoHide = true,
  showControls = true,
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filterLevel, setFilterLevel] = useState<LogLevel | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const logger = getLogger();
    
    // 监听新日志
    const handleLog = (entry: LogEntry) => {
      setLogs(prev => {
        const newLogs = [entry, ...prev].slice(0, 100);
        
        // 自动隐藏
        if (autoHide && (entry.level === 'info' || entry.level === 'debug')) {
          setTimeout(() => {
            setLogs(prevLogs => prevLogs.filter(l => l.id !== entry.id));
          }, 5000);
        }
        
        return newLogs;
      });

      // 更新统计
      setStats(logger.getStats());
    };

    logger.addListener(handleLog);

    // 定期更新统计
    const interval = setInterval(() => {
      setStats(logger.getStats());
    }, 5000);

    return () => {
      logger.removeListener(handleLog);
      clearInterval(interval);
    };
  }, [autoHide]);

  const getLevelColor = (level: LogLevel) => {
    switch (level) {
      case 'debug':
        return 'bg-gray-500';
      case 'info':
        return 'bg-blue-500';
      case 'warn':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      case 'fatal':
        return 'bg-red-600';
      default:
        return 'bg-gray-500';
    }
  };

  const getLevelIcon = (level: LogLevel) => {
    switch (level) {
      case 'debug':
        return <Info className="w-3 h-3 text-gray-400" />;
      case 'info':
        return <Info className="w-3 h-3 text-blue-400" />;
      case 'warn':
        return <Info className="w-3 h-3 text-yellow-400" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-400" />;
      case 'fatal':
        return <AlertCircle className="w-3 h-3 text-red-600" />;
      default:
        return <Info className="w-3 h-3 text-gray-400" />;
    }
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const formatData = (data: any) => {
    if (!data) return '';
    try {
      return typeof data === 'string' ? data : JSON.stringify(data);
    } catch {
      return String(data);
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesLevel = filterLevel === 'all' || log.level === filterLevel;
    const matchesSearch = searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      formatData(log.data).toLowerCase().includes(searchTerm.toLowerCase());
    return matchesLevel && matchesSearch;
  });

  const handleClearLogs = () => {
    const logger = getLogger();
    logger.clearLogs();
    setLogs([]);
  };

  const handleExportLogs = () => {
    const logger = getLogger();
    const data = logger.exportLogs('json');
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportStats = () => {
    const logger = getLogger();
    const data = logger.exportStats();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `log-stats-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (logs.length === 0 && !stats) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className="p-3 bg-gray-800 rounded-lg shadow-lg border border-gray-700 min-w-96 max-w-md">
        {/* 标题栏 */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-medium text-white">日志收集器</span>
            {stats && (
              <span className="text-xs text-gray-400">
                ({stats.total} 条)
              </span>
            )}
          </div>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
            >
              {isMinimized ? '▼' : '▲'}
            </button>
            <button
              onClick={handleClearLogs}
              className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
              title="清除日志"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* 统计信息 */}
        {stats && !isMinimized && (
          <div className="grid grid-cols-3 gap-2 mb-2 text-xs">
            <div className="p-1 bg-gray-700 rounded">
              <div className="text-gray-400">总数</div>
                <div className="text-white font-bold">{stats.total}</div>
              </div>
              <div className="p-1 bg-gray-700 rounded">
                <div className="text-gray-400">错误</div>
                <div className="text-red-400 font-bold">{stats.recentErrors}</div>
              </div>
              <div className="p-1 bg-gray-700 rounded">
                <div className="text-gray-400">警告</div>
                <div className="text-yellow-400 font-bold">{stats.recentWarnings}</div>
            </div>
          </div>
        )}

        {/* 过滤器 */}
        {!isMinimized && showControls && (
          <div className="mb-2 space-y-2">
            <div className="flex items-center space-x-2">
              <Filter className="w-3 h-3 text-gray-400" />
              <select
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value as LogLevel | 'all')}
                className="bg-gray-700 text-white text-xs rounded px-2 py-1 flex-1"
              >
                <option value="all">全部</option>
                <option value="debug">调试</option>
                <option value="info">信息</option>
                <option value="warn">警告</option>
                <option value="error">错误</option>
                <option value="fatal">严重</option>
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <Search className="w-3 h-3 text-gray-400" />
              <input
                type="text"
                placeholder="搜索日志..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-gray-700 text-white text-xs rounded px-2 py-1 flex-1 placeholder-gray-500"
              />
            </div>
          </div>
        )}

        {/* 日志列表 */}
        {!isMinimized && (
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {filteredLogs.length === 0 ? (
              <div className="text-xs text-gray-500 text-center py-4">
                无匹配日志
              </div>
            ) : (
              filteredLogs.map(log => (
                <div
                  key={log.id}
                  className="p-2 bg-gray-700 rounded border-l-2"
                  style={{ borderLeftColor: getLevelColor(log.level) }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-1 mb-1">
                        {getLevelIcon(log.level)}
                        <span className="text-xs font-medium text-white">
                          {log.level.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-400">
                          {formatTime(log.timestamp)}
                        </span>
                      </div>
                      <div className="text-xs text-gray-300 break-words">
                        {log.message}
                      </div>
                      {log.data && (
                        <div className="text-xs text-gray-500 mt-1 font-mono">
                          {formatData(log.data).substring(0, 100)}
                          {formatData(log.data).length > 100 ? '...' : ''}
                        </div>
                      )}
                      {log.userId && (
                        <div className="text-xs text-gray-500 mt-1">
                          <User className="w-3 h-3 inline mr-1" />
                          {log.userId}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* 操作按钮 */}
        {!isMinimized && showControls && (
          <div className="flex space-x-2 mt-2">
            <button
              onClick={handleExportLogs}
              className="flex items-center space-x-1 px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
            >
              <Download className="w-3 h-3" />
              <span>导出日志</span>
            </button>
            <button
              onClick={handleExportStats}
              className="flex items-center space-x-1 px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
            >
              <Activity className="w-3 h-3" />
              <span>导出统计</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * 日志统计面板组件
 */
export const LogStatsPanel: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [recentLogs, setRecentLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    const logger = getLogger();
    
    const updateStats = () => {
      setStats(logger.getStats());
      setRecentLogs(logger.getLogs({ limit: 5 }));
    };

    updateStats();
    const interval = setInterval(updateStats, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!stats) {
    return null;
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <FileText className="w-5 h-5 mr-2" />
        日志统计
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="p-3 bg-gray-700 rounded">
          <div className="text-xs text-gray-400">总日志数</div>
          <div className="text-xl font-bold text-white">{stats.total}</div>
        </div>
        <div className="p-3 bg-gray-700 rounded">
          <div className="text-xs text-gray-400">最近错误</div>
          <div className="text-xl font-bold text-red-400">{stats.recentErrors}</div>
        </div>
        <div className="p-3 bg-gray-700 rounded">
          <div className="text-xs text-gray-400">最近警告</div>
          <div className="text-xl font-bold text-yellow-400">{stats.recentWarnings}</div>
        </div>
        <div className="p-3 bg-gray-700 rounded">
          <div className="text-xs text-gray-400">性能日志</div>
          <div className="text-xl font-bold text-blue-400">{stats.performanceCount}</div>
        </div>
      </div>

      <div className="mb-4">
        <h4 className="text-sm font-medium text-white mb-2">日志级别分布</h4>
        <div className="space-y-1">
          {Object.entries(stats.byLevel).map(([level, count]) => (
            <div key={level} className="flex items-center justify-between text-xs">
              <span className="text-gray-400 capitalize">{level}</span>
              <span className="text-white font-medium">{String(count)}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium text-white mb-2">最近日志</h4>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {recentLogs.length === 0 ? (
            <div className="text-xs text-gray-500">暂无日志</div>
          ) : (
            recentLogs.map(log => (
              <div key={log.id} className="text-xs text-gray-300 flex items-start">
                <span className="text-gray-500 mr-2">
                  {new Date(log.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                </span>
                <span className={`font-medium ${
                  log.level === 'error' ? 'text-red-400' :
                  log.level === 'warn' ? 'text-yellow-400' :
                  log.level === 'info' ? 'text-blue-400' :
                  'text-gray-400'
                }`}>
                  [{log.level.toUpperCase()}]
                </span>
                <span className="ml-1 flex-1 truncate">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};