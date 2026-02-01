/**
 * 日志收集器
 * 收集、存储和上报前端日志，支持错误追踪和性能分析
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal';

export interface LogEntry {
  id: string;
  timestamp: number;
  level: LogLevel;
  message: string;
  data?: any;
  stack?: string;
  url?: string;
  userAgent?: string;
  userId?: string;
  sessionId?: string;
  component?: string;
  metadata?: Record<string, any>;
}

export interface LoggerConfig {
  level: LogLevel;
  maxLogs: number;
  autoReport: boolean;
  reportInterval: number; // 毫秒
  reportUrl?: string;
  sampleRate: number; // 采样率 0-1
  includePerformance: boolean;
  includeUserActions: boolean;
}

// 默认配置
const DEFAULT_CONFIG: LoggerConfig = {
  level: 'info',
  maxLogs: 1000,
  autoReport: true,
  reportInterval: 30000, // 30秒
  sampleRate: 1.0,
  includePerformance: true,
  includeUserActions: true,
};

// 日志级别权重
const LOG_LEVEL_WEIGHT: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
  fatal: 4,
};

export class Logger {
  private config: LoggerConfig;
  private logs: LogEntry[] = [];
  private listeners: Set<(entry: LogEntry) => void> = new Set();
  private reportInterval: any = null;
  private sessionId: string;
  private userId?: string;

  constructor(config?: Partial<LoggerConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.sessionId = this.generateSessionId();
    
    console.log(`[Logger] Initialized - Level: ${this.config.level}, Max: ${this.config.maxLogs}`);
  }

  /**
   * 生成会话ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 设置用户ID
   */
  setUserId(userId: string): void {
    this.userId = userId;
  }

  /**
   * 检查日志级别是否应该记录
   */
  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVEL_WEIGHT[level] >= LOG_LEVEL_WEIGHT[this.config.level];
  }

  /**
   * 检查采样率
   */
  private shouldSample(): boolean {
    return Math.random() <= this.config.sampleRate;
  }

  /**
   * 记录日志
   */
  log(level: LogLevel, message: string, data?: any, metadata?: Record<string, any>): void {
    if (!this.shouldLog(level) || !this.shouldSample()) {
      return;
    }

    const entry: LogEntry = {
      id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      level,
      message,
      data,
      url: typeof window !== 'undefined' ? window.location.href : undefined,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
      userId: this.userId,
      sessionId: this.sessionId,
      metadata,
    };

    // 添加堆栈信息（如果是错误）
    if (level === 'error' || level === 'fatal') {
      entry.stack = new Error().stack;
    }

    // 添加到日志列表
    this.logs.push(entry);

    // 限制日志数量
    if (this.logs.length > this.config.maxLogs) {
      this.logs = this.logs.slice(-this.config.maxLogs);
    }

    // 输出到控制台
    this.outputToConsole(entry);

    // 通知监听器
    this.notifyListeners(entry);

    // 如果是错误级别，立即上报（如果启用自动上报）
    if ((level === 'error' || level === 'fatal') && this.config.autoReport) {
      this.reportLogs();
    }
  }

  /**
   * 输出到控制台
   */
  private outputToConsole(entry: LogEntry): void {
    const prefix = `[Logger] ${entry.level.toUpperCase()} - ${new Date(entry.timestamp).toLocaleTimeString('zh-CN')}`;
    
    switch (entry.level) {
      case 'debug':
        console.debug(prefix, entry.message, entry.data || '');
        break;
      case 'info':
        console.info(prefix, entry.message, entry.data || '');
        break;
      case 'warn':
        console.warn(prefix, entry.message, entry.data || '');
        break;
      case 'error':
      case 'fatal':
        console.error(prefix, entry.message, entry.data || '', entry.stack || '');
        break;
    }
  }

  /**
   * 通知监听器
   */
  private notifyListeners(entry: LogEntry): void {
    this.listeners.forEach(listener => {
      try {
        listener(entry);
      } catch (error) {
        console.error('[Logger] 通知监听器失败:', error);
      }
    });
  }

  /**
   * 添加监听器
   */
  addListener(listener: (entry: LogEntry) => void): void {
    this.listeners.add(listener);
  }

  /**
   * 移除监听器
   */
  removeListener(listener: (entry: LogEntry) => void): void {
    this.listeners.delete(listener);
  }

  /**
   * 日志方法别名
   */
  debug(message: string, data?: any, metadata?: Record<string, any>): void {
    this.log('debug', message, data, metadata);
  }

  info(message: string, data?: any, metadata?: Record<string, any>): void {
    this.log('info', message, data, metadata);
  }

  warn(message: string, data?: any, metadata?: Record<string, any>): void {
    this.log('warn', message, data, metadata);
  }

  error(message: string, data?: any, metadata?: Record<string, any>): void {
    this.log('error', message, data, metadata);
  }

  fatal(message: string, data?: any, metadata?: Record<string, any>): void {
    this.log('fatal', message, data, metadata);
  }

  /**
   * 记录错误
   */
  recordError(error: Error, data?: any, metadata?: Record<string, any>): void {
    this.error(error.message, {
      ...data,
      name: error.name,
      stack: error.stack,
    }, metadata);
  }

  /**
   * 记录性能指标
   */
  recordPerformance(name: string, duration: number, data?: any): void {
    if (!this.config.includePerformance) {
      return;
    }

    this.info(`[Performance] ${name}`, {
      duration,
      ...data,
    });
  }

  /**
   * 记录用户行为
   */
  recordUserAction(action: string, data?: any, metadata?: Record<string, any>): void {
    if (!this.config.includeUserActions) {
      return;
    }

    this.info(`[UserAction] ${action}`, data, metadata);
  }

  /**
   * 上报日志
   */
  async reportLogs(): Promise<void> {
    if (!this.config.reportUrl || this.logs.length === 0) {
      return;
    }

    const logsToReport = [...this.logs];
    
    try {
      const response = await fetch(this.config.reportUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          logs: logsToReport,
          sessionId: this.sessionId,
          userId: this.userId,
          timestamp: Date.now(),
        }),
      });

      if (response.ok) {
        // 清除已上报的日志
        this.logs = this.logs.filter(log => !logsToReport.includes(log));
        console.log(`[Logger] 上报 ${logsToReport.length} 条日志成功`);
      } else {
        console.warn(`[Logger] 日志上报失败: ${response.status}`);
      }
    } catch (error) {
      console.error('[Logger] 日志上报错误:', error);
    }
  }

  /**
   * 启动自动上报
   */
  startAutoReport(): void {
    if (this.reportInterval) {
      return; // 已经启动
    }

    if (!this.config.autoReport || !this.config.reportUrl) {
      return; // 未启用自动上报
    }

    console.log('[Logger] 启动自动上报');
    
    this.reportInterval = setInterval(() => {
      this.reportLogs();
    }, this.config.reportInterval);
  }

  /**
   * 停止自动上报
   */
  stopAutoReport(): void {
    if (this.reportInterval) {
      clearInterval(this.reportInterval);
      this.reportInterval = null;
      console.log('[Logger] 停止自动上报');
    }
  }

  /**
   * 获取日志
   */
  getLogs(filter?: { level?: LogLevel; limit?: number }): LogEntry[] {
    let logs = [...this.logs];

    if (filter?.level) {
      logs = logs.filter(log => log.level === filter.level);
    }

    if (filter?.limit) {
      logs = logs.slice(-filter.limit);
    }

    return logs;
  }

  /**
   * 获取错误日志
   */
  getErrorLogs(limit?: number): LogEntry[] {
    return this.getLogs({ level: 'error', limit });
  }

  /**
   * 获取性能日志
   */
  getPerformanceLogs(limit?: number): LogEntry[] {
    return this.logs
      .filter(log => log.message.startsWith('[Performance]'))
      .slice(-(limit || 10));
  }

  /**
   * 获取用户行为日志
   */
  getUserActionLogs(limit?: number): LogEntry[] {
    return this.logs
      .filter(log => log.message.startsWith('[UserAction]'))
      .slice(-(limit || 10));
  }

  /**
   * 获取统计信息
   */
  getStats(): {
    total: number;
    byLevel: Record<LogLevel, number>;
    recentErrors: number;
    recentWarnings: number;
    performanceCount: number;
    userActionCount: number;
  } {
    const byLevel: Record<LogLevel, number> = {
      debug: 0,
      info: 0,
      warn: 0,
      error: 0,
      fatal: 0,
    };

    let recentErrors = 0;
    let recentWarnings = 0;
    let performanceCount = 0;
    let userActionCount = 0;

    const oneHourAgo = Date.now() - 60 * 60 * 1000;

    this.logs.forEach(log => {
      byLevel[log.level]++;
      
      if (log.timestamp > oneHourAgo) {
        if (log.level === 'error' || log.level === 'fatal') {
          recentErrors++;
        } else if (log.level === 'warn') {
          recentWarnings++;
        }
      }

      if (log.message.startsWith('[Performance]')) {
        performanceCount++;
      }

      if (log.message.startsWith('[UserAction]')) {
        userActionCount++;
      }
    });

    return {
      total: this.logs.length,
      byLevel,
      recentErrors,
      recentWarnings,
      performanceCount,
      userActionCount,
    };
  }

  /**
   * 清除日志
   */
  clearLogs(): void {
    this.logs = [];
    console.log('[Logger] 日志已清除');
  }

  /**
   * 导出日志
   */
  exportLogs(format: 'json' | 'csv' = 'json'): string {
    if (format === 'csv') {
      const headers = ['id', 'timestamp', 'level', 'message', 'data', 'url', 'userId'];
      const rows = this.logs.map(log => [
        log.id,
        new Date(log.timestamp).toISOString(),
        log.level,
        `"${log.message.replace(/"/g, '""')}"`,
        `"${JSON.stringify(log.data || {}).replace(/"/g, '""')}"`,
        log.url || '',
        log.userId || '',
      ]);
      return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    }

    return JSON.stringify(this.logs, null, 2);
  }

  /**
   * 导出统计信息
   */
  exportStats(): string {
    const stats = this.getStats();
    return JSON.stringify(stats, null, 2);
  }

  /**
   * 生成报告
   */
  report(): void {
    const stats = this.getStats();
    const recentLogs = this.getLogs({ limit: 10 });
    
    console.group('[Logger] 日志报告');
    console.log('统计信息:', stats);
    console.log('最近日志:', recentLogs);
    console.groupEnd();
  }

  /**
   * 获取性能数据
   */
  getPerformanceData(): any[] {
    return this.logs
      .filter(log => log.metadata?.performance)
      .map(log => ({
        timestamp: log.timestamp,
        operation: log.metadata?.operation,
        duration: log.metadata?.duration,
        data: log.data,
      }));
  }

  /**
   * 记录用户操作
   */
  userAction(action: string, data?: any): void {
    this.info(`[UserAction] ${action}`, data);
  }

  /**
   * 记录性能数据
   */
  performance(operation: string, duration: number, data?: any): void {
    this.info(`[Performance] ${operation}`, {
      duration,
      ...data,
    });
  }

  /**
   * 销毁日志收集器
   */
  destroy(): void {
    this.stopAutoReport();
    this.listeners.clear();
    console.log('[Logger] 日志收集器已销毁');
  }
}

// 全局日志收集器实例
let globalLogger: Logger | null = null;

/**
 * 获取全局日志收集器
 */
export function getLogger(): Logger {
  if (!globalLogger) {
    globalLogger = new Logger();
  }
  return globalLogger;
}

/**
 * 初始化全局日志收集器
 */
export function initializeLogger(config?: Partial<LoggerConfig>): Logger {
  if (globalLogger) {
    globalLogger.destroy();
  }
  globalLogger = new Logger(config);
  return globalLogger;
}

/**
 * 销毁全局日志收集器
 */
export function destroyLogger(): void {
  if (globalLogger) {
    globalLogger.destroy();
    globalLogger = null;
  }
}