import React, { useState, useEffect, useMemo } from 'react';
import { 
  FileText, 
  AlertCircle, 
  Info, 
  Trash2, 
  Filter,
  Search,
  User,
  Activity,
  Calendar,
  Download as DownloadIcon,
  Upload as UploadIcon,
  RefreshCw,
  Settings,
  BarChart2,
  List,
  Play,
  Bug
} from 'lucide-react';
import { getLogger, LogEntry, LogLevel } from '../utils/Logger';
import { LogDemo } from '../components/LogDemo';

interface LogPageProps {
  onBack?: () => void;
}

export const LogPage: React.FC<LogPageProps> = ({ onBack }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filterLevel, setFilterLevel] = useState<LogLevel | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState<{ start: Date | null; end: Date | null }>({
    start: null,
    end: null,
  });
  const [stats, setStats] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'list' | 'stats' | 'settings' | 'demo'>('list');
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    const logger = getLogger();
    
    const updateLogs = () => {
      const allLogs = logger.getLogs();
      setLogs(allLogs);
      setStats(logger.getStats());
    };

    updateLogs();

    let interval: ReturnType<typeof setInterval>;
    if (autoRefresh) {
      interval = setInterval(updateLogs, 3000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      const matchesLevel = filterLevel === 'all' || log.level === filterLevel;
      const matchesSearch = searchTerm === '' || 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (log.data && JSON.stringify(log.data).toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesDate = (() => {
        if (!dateRange.start && !dateRange.end) return true;
        const logDate = new Date(log.timestamp);
        if (dateRange.start && logDate < dateRange.start) return false;
        if (dateRange.end && logDate > dateRange.end) return false;
        return true;
      })();

      return matchesLevel && matchesSearch && matchesDate;
    });
  }, [logs, filterLevel, searchTerm, dateRange]);

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
        return <Info className="w-4 h-4 text-gray-400" />;
      case 'info':
        return <Info className="w-4 h-4 text-blue-400" />;
      case 'warn':
        return <Info className="w-4 h-4 text-yellow-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      case 'fatal':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Info className="w-4 h-4 text-gray-400" />;
    }
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatData = (data: any) => {
    if (!data) return '';
    try {
      return typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  };

  const handleClearLogs = () => {
    const logger = getLogger();
    logger.clearLogs();
    setLogs([]);
    setStats(null);
  };

  const handleExportLogs = (format: 'json' | 'csv' = 'json') => {
    const logger = getLogger();
    const data = logger.exportLogs(format);
    const mimeType = format === 'json' ? 'application/json' : 'text/csv';
    const blob = new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${Date.now()}.${format}`;
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

  const handleImportLogs = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const importedLogs = JSON.parse(content);
        
        const logger = getLogger();
        importedLogs.forEach((log: any) => {
          logger.log(log.level, log.message, log.data, log.userId);
        });

        // 更新状态
        const allLogs = logger.getLogs();
        setLogs(allLogs);
        setStats(logger.getStats());

        alert('日志导入成功！');
      } catch (error) {
        alert('日志导入失败：' + (error as Error).message);
      }
    };
    reader.readAsText(file);

    // 清空文件输入
    event.target.value = '';
  };

  const handleRefresh = () => {
    const logger = getLogger();
    setLogs(logger.getLogs());
    setStats(logger.getStats());
  };

  const handleClearDateRange = () => {
    setDateRange({ start: null, end: null });
  };

  const getStatsSummary = () => {
    if (!stats) return null;
    
    return {
      total: stats.total,
      byLevel: stats.byLevel,
      recentErrors: stats.recentErrors,
      recentWarnings: stats.recentWarnings,
      performanceCount: stats.performanceCount,
      userActions: stats.userActions,
      avgResponseTime: stats.avgResponseTime,
      errorRate: stats.errorRate,
    };
  };

  const statsSummary = getStatsSummary();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            ← 返回
          </button>
          <h1 className="text-2xl font-bold flex items-center">
            <FileText className="w-6 h-6 mr-2" />
            日志收集系统
          </h1>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
            }`}
            title="日志列表"
          >
            <List className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('stats')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'stats' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
            }`}
            title="统计分析"
          >
            <BarChart2 className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('demo')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'demo' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
            }`}
            title="演示"
          >
            <Play className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('settings')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'settings' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
            }`}
            title="设置"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* 统计概览 */}
      {statsSummary && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-6">
          <div className="p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-xs text-gray-400">总日志数</div>
            <div className="text-xl font-bold text-white">{statsSummary.total}</div>
          </div>
          <div className="p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-xs text-gray-400">最近错误</div>
            <div className="text-xl font-bold text-red-400">{statsSummary.recentErrors}</div>
          </div>
          <div className="p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-xs text-gray-400">最近警告</div>
            <div className="text-xl font-bold text-yellow-400">{statsSummary.recentWarnings}</div>
          </div>
          <div className="p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-xs text-gray-400">性能日志</div>
            <div className="text-xl font-bold text-blue-400">{statsSummary.performanceCount}</div>
          </div>
          <div className="p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-xs text-gray-400">用户操作</div>
            <div className="text-xl font-bold text-green-400">{statsSummary.userActions}</div>
          </div>
          <div className="p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-xs text-gray-400">平均响应</div>
            <div className="text-xl font-bold text-purple-400">
              {statsSummary.avgResponseTime ? `${statsSummary.avgResponseTime.toFixed(0)}ms` : '-'}
            </div>
          </div>
        </div>
      )}

      {/* 视图内容 */}
      {viewMode === 'list' && (
        <>
          {/* 过滤器和操作栏 */}
          <div className="bg-gray-800 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* 日志级别过滤 */}
              <div>
                <label className="text-xs text-gray-400 mb-1 block">日志级别</label>
                <div className="flex items-center space-x-2">
                  <Filter className="w-4 h-4 text-gray-400" />
                  <select
                    value={filterLevel}
                    onChange={(e) => setFilterLevel(e.target.value as LogLevel | 'all')}
                    className="bg-gray-700 text-white text-sm rounded px-3 py-2 flex-1"
                  >
                    <option value="all">全部级别</option>
                    <option value="debug">调试 (Debug)</option>
                    <option value="info">信息 (Info)</option>
                    <option value="warn">警告 (Warn)</option>
                    <option value="error">错误 (Error)</option>
                    <option value="fatal">严重 (Fatal)</option>
                  </select>
                </div>
              </div>

              {/* 搜索 */}
              <div>
                <label className="text-xs text-gray-400 mb-1 block">搜索</label>
                <div className="flex items-center space-x-2">
                  <Search className="w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="搜索日志内容..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="bg-gray-700 text-white text-sm rounded px-3 py-2 flex-1 placeholder-gray-500"
                  />
                </div>
              </div>

              {/* 日期范围 */}
              <div>
                <label className="text-xs text-gray-400 mb-1 block">日期范围</label>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <input
                    type="date"
                    value={dateRange.start ? dateRange.start.toISOString().split('T')[0] : ''}
                    onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value ? new Date(e.target.value) : null }))}
                    className="bg-gray-700 text-white text-sm rounded px-2 py-2 w-full"
                  />
                  <input
                    type="date"
                    value={dateRange.end ? dateRange.end.toISOString().split('T')[0] : ''}
                    onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value ? new Date(e.target.value) : null }))}
                    className="bg-gray-700 text-white text-sm rounded px-2 py-2 w-full"
                  />
                </div>
              </div>

              {/* 自动刷新 */}
              <div>
                <label className="text-xs text-gray-400 mb-1 block">自动刷新</label>
                <div className="flex items-center space-x-2">
                  <RefreshCw className="w-4 h-4 text-gray-400" />
                  <button
                    onClick={() => setAutoRefresh(!autoRefresh)}
                    className={`px-3 py-2 rounded text-sm transition-colors ${
                      autoRefresh ? 'bg-green-600' : 'bg-gray-700 hover:bg-gray-600'
                    }`}
                  >
                    {autoRefresh ? '已开启' : '已关闭'}
                  </button>
                </div>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex flex-wrap gap-2 mt-4">
              <button
                onClick={handleRefresh}
                className="flex items-center space-x-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>刷新</span>
              </button>
              <button
                onClick={() => handleExportLogs('json')}
                className="flex items-center space-x-1 px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors"
              >
                <DownloadIcon className="w-4 h-4" />
                <span>导出JSON</span>
              </button>
              <button
                onClick={() => handleExportLogs('csv')}
                className="flex items-center space-x-1 px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors"
              >
                <DownloadIcon className="w-4 h-4" />
                <span>导出CSV</span>
              </button>
              <button
                onClick={handleExportStats}
                className="flex items-center space-x-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm transition-colors"
              >
                <Activity className="w-4 h-4" />
                <span>导出统计</span>
              </button>
              <label className="flex items-center space-x-1 px-3 py-2 bg-orange-600 hover:bg-orange-700 rounded text-sm transition-colors cursor-pointer">
                <UploadIcon className="w-4 h-4" />
                <span>导入日志</span>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImportLogs}
                  className="hidden"
                />
              </label>
              <button
                onClick={handleClearDateRange}
                className="flex items-center space-x-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
              >
                <Calendar className="w-4 h-4" />
                <span>清除日期</span>
              </button>
              <button
                onClick={handleClearLogs}
                className="flex items-center space-x-1 px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span>清空日志</span>
              </button>
            </div>
          </div>

          {/* 日志列表 */}
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">
                日志列表
                <span className="text-sm text-gray-400 ml-2">
                  ({filteredLogs.length} 条)
                </span>
              </h2>
              <div className="text-sm text-gray-400">
                {filterLevel !== 'all' && `级别: ${filterLevel.toUpperCase()}`}
                {searchTerm && ` | 搜索: "${searchTerm}"`}
                {dateRange.start && ` | 从: ${dateRange.start.toLocaleDateString()}`}
                {dateRange.end && ` | 到: ${dateRange.end.toLocaleDateString()}`}
              </div>
            </div>

            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredLogs.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>暂无日志</p>
                  <p className="text-sm mt-1">调整过滤条件或等待新日志</p>
                </div>
              ) : (
                filteredLogs.map(log => (
                  <div
                    key={log.id}
                    className="p-3 bg-gray-700 rounded-lg border-l-4 hover:bg-gray-650 transition-colors"
                    style={{ borderLeftColor: getLevelColor(log.level) }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          {getLevelIcon(log.level)}
                          <span className="text-sm font-medium text-white">
                            [{log.level.toUpperCase()}]
                          </span>
                          <span className="text-xs text-gray-400">
                            {formatTime(log.timestamp)}
                          </span>
                          {log.userId && (
                            <span className="text-xs text-gray-500 flex items-center">
                              <User className="w-3 h-3 mr-1" />
                              {log.userId}
                            </span>
                          )}
                          {log.metadata?.performance && (
                            <span className="text-xs text-blue-400 flex items-center">
                              <Activity className="w-3 h-3 mr-1" />
                              {log.metadata.duration}ms
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-200 break-words">
                          {log.message}
                        </div>
                        {log.data && (
                          <div className="mt-2 p-2 bg-gray-800 rounded text-xs font-mono text-gray-400 overflow-x-auto">
                            {formatData(log.data)}
                          </div>
                        )}
                        {log.stack && (
                          <div className="mt-2 p-2 bg-gray-900 rounded text-xs font-mono text-red-400 overflow-x-auto">
                            {log.stack}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}

      {viewMode === 'stats' && statsSummary && (
        <div className="space-y-6">
          {/* 日志级别分布 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <BarChart2 className="w-5 h-5 mr-2" />
              日志级别分布
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {Object.entries(statsSummary.byLevel).map(([level, count]) => (
                <div key={level} className="p-4 bg-gray-700 rounded-lg">
                  <div className="text-sm text-gray-400 capitalize">{level}</div>
                  <div className="text-2xl font-bold text-white">{String(count)}</div>
                  <div className="mt-2 h-2 bg-gray-600 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getLevelColor(level as LogLevel)}`}
                      style={{ width: `${(Number(count) / statsSummary.total) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 性能统计 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              性能统计
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-700 rounded-lg">
                <div className="text-sm text-gray-400">性能日志数</div>
                <div className="text-2xl font-bold text-green-400">
                  {statsSummary.performanceCount}
                </div>
              </div>
              <div className="p-4 bg-gray-700 rounded-lg">
                <div className="text-sm text-gray-400">用户操作数</div>
                <div className="text-2xl font-bold text-blue-400">
                  {statsSummary.userActions}
                </div>
              </div>
            </div>
          </div>

          {/* 用户操作统计 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <User className="w-5 h-5 mr-2" />
              用户操作统计
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-700 rounded-lg">
                <div className="text-sm text-gray-400">最近错误/警告</div>
                <div className="text-2xl font-bold text-yellow-400">
                  {statsSummary.recentErrors + statsSummary.recentWarnings}
                </div>
              </div>
            </div>
          </div>

          {/* 最近错误日志 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-red-400" />
              最近错误日志
            </h2>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {logs
                .filter(log => log.level === 'error' || log.level === 'fatal')
                .slice(0, 10)
                .map(log => (
                  <div key={log.id} className="p-3 bg-gray-700 rounded-lg border-l-4 border-red-500">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-sm font-medium text-red-400">[{log.level.toUpperCase()}]</span>
                      <span className="text-xs text-gray-400">{formatTime(log.timestamp)}</span>
                    </div>
                    <div className="text-sm text-gray-200">{log.message}</div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {viewMode === 'demo' && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Bug className="w-5 h-5 mr-2" />
              日志收集演示
            </h2>
            <p className="text-gray-400 text-sm mb-4">
              通过点击下方按钮测试不同级别的日志记录功能，包括用户操作、性能跟踪和错误处理。
            </p>
            <LogDemo />
          </div>
        </div>
      )}

      {viewMode === 'settings' && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              日志设置
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">自动刷新间隔 (秒)</label>
                <input
                  type="number"
                  min="1"
                  max="60"
                  value={3}
                  onChange={() => {}}
                  className="bg-gray-700 text-white text-sm rounded px-3 py-2 w-full md:w-64"
                  disabled
                />
                <p className="text-xs text-gray-500 mt-1">当前版本固定为3秒</p>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">最大日志保留数</label>
                <input
                  type="number"
                  min="100"
                  max="10000"
                  value={100}
                  onChange={() => {}}
                  className="bg-gray-700 text-white text-sm rounded px-3 py-2 w-full md:w-64"
                  disabled
                />
                <p className="text-xs text-gray-500 mt-1">当前版本固定为100条</p>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">日志级别</label>
                <div className="space-y-2">
                  {['debug', 'info', 'warn', 'error', 'fatal'].map(level => (
                    <label key={level} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={true}
                        onChange={() => {}}
                        disabled
                        className="rounded"
                      />
                      <span className="text-sm text-white capitalize">{level}</span>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">当前版本记录所有级别</p>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">自动报告</label>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      const logger = getLogger();
                      logger.report();
                      alert('报告已生成并发送到控制台');
                    }}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
                  >
                    生成报告
                  </button>
                  <span className="text-xs text-gray-500">手动触发日志报告</span>
                </div>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">性能跟踪</label>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      const logger = getLogger();
                      const perfData = logger.getPerformanceData();
                      console.log('性能数据:', perfData);
                      alert('性能数据已输出到控制台');
                    }}
                    className="px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm transition-colors"
                  >
                    查看性能数据
                  </button>
                  <span className="text-xs text-gray-500">查看性能跟踪数据</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Info className="w-5 h-5 mr-2" />
              关于日志收集系统
            </h2>
            <div className="space-y-2 text-sm text-gray-300">
              <p>日志收集系统提供以下功能：</p>
              <ul className="list-disc list-inside space-y-1">
                <li>多级别日志记录 (Debug, Info, Warn, Error, Fatal)</li>
                <li>自动错误报告和性能跟踪</li>
                <li>用户操作记录</li>
                <li>日志导出 (JSON/CSV)</li>
                <li>日志导入和恢复</li>
                <li>实时统计和分析</li>
                <li>自动刷新和手动刷新</li>
                <li>按级别、时间、内容过滤</li>
              </ul>
              <p className="text-xs text-gray-500 mt-4">
                版本: 1.0.0 | 最后更新: {new Date().toLocaleDateString('zh-CN')}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};